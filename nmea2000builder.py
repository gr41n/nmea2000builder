import serial
from datetime import datetime
import time
import binascii
import math

###!!! This script allows you to build a NMEA 2000 string and write to the bus using specificly an Actisense device  !!!###
###!!! It provides a somewhat modular structure to add new PGNs granted that you know the PGN and the data structure !!!###
###!!! It then calculates everything needed to created a working NMEA string, such as lengths and the CRC            !!!###
###!!! Special thanks to Fathom5 and their phenomenal Hack the Boat CTF at Defcon. They sparked my interest in this, gave me the foundation I needed to understand NMEA 2000, and answered questions long after the event when I felt stuck.  !!!###

###~~~ Open the serial port ~~~###
def openPort():
    ser = serial.Serial('COM4', 115200, timeout=5)
    return ser
###~~~ -------------------- ~~~###

###~~~ PGN Codes - Add new PGN codes here as a running list  ~~~###
pgn_130312 = [8, 253, 1] #This is the PGN for "Temperature - DEPRECATED" and is used for miscellanenous temperatures like ambient air between -273.15 and 379.63 celsius
###~~~ -------------------- ~~~###

###~~~ PGN Data Field Builder - This section is used to store functions to build specific data strings based on known data strings  ~~~###
def pgn130312_set_temp():
    #The structure of this PGN's data is:
    #Field 1 (1 byte) = Sequence ID
    #Field 2 (1 byte) = Temperature Instance
    #Field 3 (1 byte) = Termperature Source
    #Field 4 (2 bytes) = Actual temperature, where firt hex byte increases temperature in increments of 0.01 and the second increases it by 2.56
    #Field 5 (2 bytes) = Set Temperature, with the same math as actual temp. 
    #Field 6 (1 byte) = Reserved field 
    value = float(input('For PGN 130312, what do you want to set the temperature to? Input should be in celsius, with valid ranges being equal to and between -273.15 and 379.63 celsius: '))

    while True: 
        try:
            float(value)
            if -273.15 <= value <= 379.63: #Confirm input is valid
                break
            else:
                print("Not a valid entry, try again. Input should be in celsius, with valid ranges being equal to and between -273.15 and 379.63 celsius")
                pgn130312_set_temp() #Rerun function if input not valid
        except ValueError:
                print("Not a valid entry, try again. Input should be in celsius, with valid ranges being equal to and between -273.15 and 379.63 celsius")
                pgn130312_set_temp() #Rerun function if input not valid

    # Convert Celsius to Kelvin
    K = (value + 273.15) # Convert the input to Kelvin. Our calculations are based on temperature in kevlin, and it is easier to work with the positive number. 
        
    byte1_temp = (K % 2.56) * 100 # For every incremental increase in the first hex byte, the temperature increases by 0.01
    byte2_temp = K // 2.56 # For every incremental increase in the secon hex byte, the temperature increases by 2.56
    
    temp_hex = [math.ceil(byte1_temp), math.ceil(byte2_temp)] # Round up due to python floating math

    pgn_data = [0, 1] + temp_hex + [255,255,255] # Create the data string.
    
    return pgn_data
###~~~ -------------------- ~~~###



###~~~ This function builds the NMEA 2000 string and calls in the necessary functions to do so ~~~###
def n2kBuild():
    n2kStart = [16, 2] # In hex, the start of a NMEA string is denoted by \x10\x02
    cmd = [148] # The \x94 byte is used to write to the bus. 
    #pkt_len will be located in this order in the final string, but will be calculated by adding the number of bytes to include priority, pgn, dst, src, pgn_len, and pgn_data. Do not include cmd, pkt_len, and crc, or the start and end bytes
    prio = [5] # Setting priority to 5 to match devices in our environment, but this would be tweaked if you wanted to change priority in relation to other devices. 
    #pgn = pgn_130312 # Select a variable from the PGN codes in the static variables section. This section is used to keep a list of PGN codes.
    dst = [255] # NMEA uses bus technology, so everyone will receive all frames. But setting the dst to 255 will cause all devices act on it. 
    src = [52] # The source will be rewritten by the device that we are writing to (such as the Actisense)
    #pgn_len will be located in this order int he final string, but is calvulated by adding the number of bytes in pgn_data
    #pgn_data will be located in this order int the final string. The bytes represent different things as defined by the NMEA standard. 
    #crc will be located in this order int he final string. It is calculated by ADDING the decimal representation of each hex byte precreding it (except for the NMEA start bytes) followed by MODULO 256, followed by SUBTRACTING that result by 256. 
    n2kEnd = [16,3] # In hex, the start of a NMEA string is denoted by \x10\x03

    
    menu = {}
    menu['1']="PGN 130312 - Temperature (Ambient air, water, and miscellaneous."
    menu['99']="Exit"
    while True: 
        options=menu.keys()
        #options.sort()
        for entry in options: 
            print(entry, menu[entry])
        selection=input("Select the PGN that you would like to build") 
        if selection =='1':
            pgn = pgn_130312
            pgn_data = pgn130312_set_temp()
            break
        elif selection == '99': 
            break
        else: 
            print("Unknown Option Selected!")

    # Determine the pgn length by checking the length of the pgn_data byte array. 
    pgn_len = [] 
    pgn_len.append(len(pgn_data))

    # Determine the packet length by checking the length of various fields and summing them. 
    pkt_len_sum = len(prio) + len(pgn) + len(dst) + len(src) + len(pgn_len) + len(pgn_data)
    pkt_len = []
    pkt_len.append(pkt_len_sum)

    # The CRC is calculated by summing the decimal numbers of several fields, then performing modulo 256 on that sum, and subtracting that by 256. Must be correct to write to actisense. 
    crc_calc = sum(cmd) + sum(pkt_len) + sum(prio) + sum(pgn) + + sum(src) + sum(dst) + sum(pgn_len) + sum(pgn_data)
    crc_calc = crc_calc % 256
    crc_calc = 256 - crc_calc
    crc = []
    crc.append(crc_calc)

    #Finally, create the NMEA 2000 string by concatenating the byte arrays together. 
    nmea_string = n2kStart + cmd + pkt_len + prio + pgn + dst +src + pgn_len + pgn_data + crc + n2kEnd
    nmea_string = binascii.hexlify(bytearray(nmea_string)) # hexlify turns this into a single hex string ('1002148....') from the Decimal bytearray 
    nmea_string = binascii.unhexlify(nmea_string) # unhexlify takes the hex string and converts it into the format that it must be in to write with '\x10\x02\x148....'.

    return nmea_string
###~~~ -------------------- ~~~###

###~~~ This function is used to write the NMEA 2000 string created in n2kBuild() ~~~###
def nmeaWrite(nmea_string):
    ser = openPort()
    while 1 == 1:
        ser.write(nmea_string) #Take the constructed nmea string and write to the COM port. 
        
        print("Wrote to Actisense at ", datetime.now())
        
        time.sleep(.1)
    ser.close()
###~~~ -------------------- ~~~###

def main ():
    # place scripts to run here
    nmea_string = n2kBuild()
    nmeaWrite(nmea_string)

# run script
main()
