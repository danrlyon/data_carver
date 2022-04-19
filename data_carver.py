'''Data Carver

Requirements:
    Write a Python program to carve evidence from a binary file.
        - There are no import library restrictions
        - Your program must accept a binary file as a command-line argument (test 
            using a binary file in the same folder as your python program)
        - Your program must write carved files to a folder titled with your last name
        - Your program must write the MD5 hash of each carved file to a file names
            hashes.txt in the same folder as the carved images
        - Your program must output to screen some basic file information such as
            file type found, file size, and location offset for each carved file

    Recommend you start by carving one file type, then expand your solution to carve various file types.
    Your solution will be testing using a binary file with primarily jpg, png, and pdf file types.



'''

import binascii, re, os, sys


def main():
    print("Starting the data carving software...")


if __name__ == "__main__":
	main()