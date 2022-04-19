#! /usr/bin/env python3

import sys
import os
import binascii

fname = input("Enter a file name: ")
sof = input("Enter the start of file byte offset: ")
eof = input("Enter the end of file byte offset: ")

fname_obj = open(fname, 'rb')
data = fname_obj.read()
fname_obj.close()
subdata = data[int(sof, 16):int(eof, 16)]


carve = input("enter a file name to save carved data: ")
fcarve = open(carve, 'wb')
fcarve.write(subdata)
fcarve.close()
print ("Your file has been saved, Goodbye")
sys.exit()



