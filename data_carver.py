''' Data Carver

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

        Recommend you start by carving one file type, then expand your solution
        to carve various file types. Your solution will be testing using a binary
        file with primarily jpg, png, and pdf file types.


    TODO:
        X- Take input args
        X- Open File
        X- Find JPG Header
        X- Find JPG Footer
        - Write the JPG to a file
            - Into Folder titled with my last name
            - Write the filenames and its hash to hashes.txt in same folder
        - Print the following:
            - file type
            - file size
            - start and finish offsets
        - Repeat for PNG
        - Repeat for PDF

'''

import os
import sys
import imghdr
from itertools import islice
from argparse import ArgumentParser

JPEG_SOF = [b'\xFF', b'\xD8', b'\xFF', b'\xE0']
JPEG_EOF = [b'\xDD', b'\xD9']
PNG_SOF = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
'''Each chunk consists of four parts:
Length
    A 4-byte unsigned integer giving the number of bytes in the chunk's data field.
    The length counts only the data field, not itself, the chunk type code, or the
    CRC. Zero is a valid length. Although encoders and decoders should treat the
    length as unsigned, its value must not exceed (2^31)-1 bytes.
Chunk Type
    A 4-byte chunk type code. For convenience in description and in examining PNG
    files, type codes are restricted to consist of uppercase and lowercase ASCII
    letters (A-Z and a-z, or 65-90 and 97-122 decimal). However, encoders and
    decoders must treat the codes as fixed binary values, not character strings.
    For example, it would not be correct to represent the type code IDAT by the
    EBCDIC equivalents of those letters. Additional naming conventions for chunk
    types are discussed in the next section.
Chunk Data
    The data bytes appropriate to the chunk type, if any. This field can be
    of zero length.
CRC
    A 4-byte CRC (Cyclic Redundancy Check) calculated on the preceding bytes in
    the chunk, including the chunk type code and chunk data fields, but not including
    the length field. The CRC is always present, even for chunks containing no data.
    See CRC algorithm.
'''
PNG_IEND = b'\x49\x45\x4E\x44'
PDF_SOF = b'\x25\x50\x44\x46\x2D'

OUTPUT_DIR = 'Allen'


def parse_arguments():
    '''Parse command line arguments'''
    parser = ArgumentParser(
        description='''This script will take a binary input file and extract all
                       of the JPG, PNG, and PDF files to the output directory
                       ./allen/ along with a hashes.txt of all of the files discovered.
                    ''')
    parser.add_argument(
        '-f', '--file', help='File to be parsed.', required=True)
    return parser.parse_args()


def make_dir(out_dir):
    '''Use the constant, OUTPUT_DIR, which is my last name,
       and create the directory if it doesn't exist to store the
       output files.
    '''
    print(f"{out_dir} exists = {os.path.exists(out_dir)}")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print(f"Created output directory: {out_dir}")
        return
    print(f"{out_dir} already exists")


def test_image(input_image):
    '''Discover the type of image file and if it is valid.'''
    file_type = imghdr.what(input_image)
    print(f"The image is a {file_type} file")


def scan_for_jpeg(binary_filename):
    '''Scan the whole binary file to search for JPEG files. Take a
        4 byte sliding window and test if it matches the JPEG
        magic number
    '''
    with open(binary_filename, 'rb') as bin_file:
        file_size = os.path.getsize(binary_filename)
        window_size = len(JPEG_SOF)
        buffer = [b'\x00' for _ in range(window_size)]
        print(f"Buffer Starting Point: {buffer}")
        print(f"File is {file_size} bytes.")
        i = 0
        while i <= file_size - window_size:
            for j in range(window_size - 1):
                buffer[j] = buffer[j+1]
                # print(buffer)
            buffer[-1] = bin_file.read(1)
            # print(f"Current Buffer: {buffer}")
            if i % 10000000 == 0:
                print(f"{i} bytes out of {file_size} processed")
            i += 1
            if buffer == JPEG_SOF:
                print(f"Found JPEG: SOF={i}, buffer={buffer}")
            if buffer[window_size - len(JPEG_EOF):] == JPEG_EOF:
                print(f"Found JPEG: EOF={i}, buffer={buffer}")


def main():
    '''Main Function'''
    print("Starting the data carving software...")

    print("Parse command line args")
    args = parse_arguments()

    out_dir = f"{sys.path[0]}/{OUTPUT_DIR}"
    print(f"Check if directory {out_dir} exists.")
    make_dir(out_dir)

    print(f"Try to open {args.file}")
    scan_for_jpeg(args.file)



if __name__ == "__main__":
    main()
