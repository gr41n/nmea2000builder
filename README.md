# nmea2000builder
Python script to build NMEA 2000 strings and write to an Actisense device. PGNs are limited and must be created for additional functionality. 

This script allows you to build a NMEA 2000 string and write to the bus using specificly an Actisense device
It provides a somewhat modular structure to add new PGNs granted that you know the PGN and the data structure
It then calculates everything needed to created a working NMEA string, such as lengths and the CRC
Special thanks to Fathom5 and their phenomenal Hack the Boat CTF at Defcon. They sparked my interest in this, gave me the foundation I needed to understand NMEA 2000, and answered questions long after the event when I felt stuck.
And special thanks to some individuals:
- Anthony Efantis with whome I embarked on the journey of learning the NMEA 2000 protocol with

For this script to be more useful, more PGNs must be added. I only had a thermometer to test with, but would like to add more codes in the future, either through access to the manual, or by reverse engineering codes that I have access to. 

I would love help! To add PGNs you must do a few things!
1. Add a PGN variable under the PGN Codes sections, with the variable being a bytearray of the decimal (ex pgn_130312 = [8, 253, 1]) 
2. Create a function that builds and returns the pgn data string. (see pgn130312_set_temp()) for an example.
3. Add a menu option, located within the n2kBuild function. Within this menu you must...
---add a menu selection number that the user would select to specify what pgn they want to make (ie 2, 3, or 4)
---Based on that selection, set the variable of "pgn" from the PGN codes section (pgn = pgn_130312) and set the pgn_data variable to call your corresponding function (ie pgn_data = pgn130312_set_temp())
pgn_data = pgn130312_set_temp())

### ToDo! ###
\x10\x02 and \x10\x03 must be escaped if they appear anywhere outside of the start and end of a NMEA string. This check must be added...
