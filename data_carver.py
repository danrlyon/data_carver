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

'''

import os
import sys
import imghdr
from argparse import ArgumentParser
from glob import glob
from hashlib import md5
import magic

JPEG_SOF = [b'\xFF', b'\xD8', b'\xFF', b'\xE0']
JPEG_EOF = [b'\xFF', b'\xD9']
PNG_SOF = [b'\x89', b'\x50', b'\x4E', b'\x47',
           b'\x0D', b'\x0A', b'\x1A', b'\x0A']
'''PNG: Each chunk consists of four parts:
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
PNG_IEND = [b'\x49', b'\x45', b'\x4E' ,b'\x44']
# PDF
## 1.3, there will only be EOF at the actual EOF. But 1.5 will have 2
## EOF before the end of the document
PDF13_SOF = [b'\x25', b'\x50', b'\x44', b'\x46', b'\x2D', b'\x31', b'\x2E', b'\x33']
PDF15_SOF = [b'\x25', b'\x50', b'\x44', b'\x46', b'\x2D', b'\x31', b'\x2E', b'\x35']
PDF_EOF = [b'\x0A', b'\x25', b'\x25', b'\x45', b'\x4F', b'\x46']

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
    '''Discover the type of image file and if it is valid.
       Return the type of file.
    '''
    file_type = imghdr.what(input_image)
    print(f"The image is a {file_type} file")
    test_magic(input_image)
    # Delete invalid images
    if file_type is None:
        print(f"File type {file_type} is not a valid image format.")
        print(f"Deleting {input_image}.")
        os.remove(input_image)
    return file_type


def test_magic(input_file):
    '''Test the magic number of the file.'''
    file_info = magic.from_file(input_file)
    print(f"File Info: {file_info}")
    return file_info


def scan_for_jpeg(binary_filename):
    '''Scan the whole binary file to search for JPEG files. Take a
        4 byte sliding window and test if it matches the JPEG
        magic number
    '''
    print("\nStart scanning for JPEG files...")
    files = list()
    sof_indices = list()
    eof_indices = list()
    current_file = b''
    with open(binary_filename, 'rb') as bin_file:
        file_size = os.path.getsize(binary_filename)
        window_size = len(JPEG_SOF)
        buffer = [b'\x00' for _ in range(window_size)]
        i = 0
        while i <= file_size - window_size:
            # Shift the buffer window and add the next byte to the end
            for j in range(window_size - 1):
                buffer[j] = buffer[j+1]
            buffer[-1] = bin_file.read(1)

            # Just print some status so you can see stuff is happening
            if i % 10000000 == 0:
                print(f"{i} bytes out of {file_size} processed")

            # If you found the start of a file, keep building
            if len(current_file) > 0:
                current_file = b''.join([current_file, buffer[-1]])

            # If you find the EOF indicator, finish the file if
            # it has been started. Store data in list of files.
            if (buffer[window_size - len(JPEG_EOF):] == JPEG_EOF and
                    len(current_file) > 0):
                files.append(current_file)
                eof_indices.append(i)
                current_file = b''
                print(f"Found JPEG: EOF={i}, buffer={buffer}")

            # Start building JPEG file
            if buffer == JPEG_SOF:
                print(f"Found JPEG: SOF={i}, buffer={buffer}")
                current_file = b''.join(buffer)
                sof_indices.append(i)

            # increment byte position
            i += 1

        print(f"\nFound {len(files)} JPEG files.")
        for i, each_file in enumerate(files):
            filename = f"{OUTPUT_DIR}/jpeg_file_{i}.jpg"
            with open(filename, "wb") as out_file:
                print(f"\nWrite output file: {filename}")
                out_file.write(each_file)
            file_type = test_image(filename)
            if file_type is not None:
                print(f"Type of file: {file_type}")
                print(f"File Size: {os.path.getsize(filename)} bytes")
                print(f"Start Offset: {sof_indices[i]}")
                print(f"End Offset: {eof_indices[i]}")


def scan_for_png(binary_filename):
    '''Scan the file for PNGs'''
    print("\nStart scanning for PNG files...")
    files = list()
    sof_indices = list()
    eof_indices = list()
    current_file = b''
    with open(binary_filename, 'rb') as bin_file:
        file_size = os.path.getsize(binary_filename)
        window_size = len(PNG_SOF)
        buffer = [b'\x00' for _ in range(window_size)]
        i = 0
        while i <= file_size - window_size:
            # Shift the buffer window and add the next byte to the end
            for j in range(window_size - 1):
                buffer[j] = buffer[j+1]
            buffer[-1] = bin_file.read(1)

            # Just print some status so you can see stuff is happening
            if i % 10000000 == 0:
                print(f"{i} bytes out of {file_size} processed")

            # If you found the start of a file, keep building
            if len(current_file) > 0:
                current_file = b''.join([current_file, buffer[-1]])

            # If you find the EOF indicator, finish the file if
            # it has been started. Store data in list of files.
            if (buffer[window_size - len(PNG_IEND):] == PNG_IEND and
                    len(current_file) > 0):
                files.append(current_file)
                eof_indices.append(i)
                current_file = b''
                print(f"Found PNG: EOF={i}, buffer={buffer}")

            # Start building PNG file
            if buffer == PNG_SOF:
                print(f"Found PNG: SOF={i}, buffer={buffer}")
                current_file = b''.join(buffer)
                sof_indices.append(i)

            # increment byte position
            i += 1

        print(f"\nFound {len(files)} PNG files.")
        for i, each_file in enumerate(files):
            filename = f"{OUTPUT_DIR}/png_file_{i}.png"
            with open(filename, "wb") as out_file:
                print(f"\nWrite output file: {filename}")
                out_file.write(each_file)
            file_type = test_image(filename)
            if file_type is not None:
                print(f"Type of file: {file_type}")
                print(f"File Size: {os.path.getsize(filename)} bytes")
                print(f"Start Offset: {sof_indices[i]}")
                print(f"End Offset: {eof_indices[i]}")


def scan_for_pdf(binary_filename):
    '''Scan the file for PDFs'''
    print("\nStart scanning for PDF files...")
    files = list()
    sof_indices = list()
    eof_indices = list()
    current_file = b''
    pdf13 = True
    with open(binary_filename, 'rb') as bin_file:
        file_size = os.path.getsize(binary_filename)
        window_size = len(PDF13_SOF)
        buffer = [b'\x00' for _ in range(window_size)]
        i = 0
        while i <= file_size - window_size:
            # Shift the buffer window and add the next byte to the end
            for j in range(window_size - 1):
                buffer[j] = buffer[j+1]
            buffer[-1] = bin_file.read(1)

            # Just print some status so you can see stuff is happening
            if i % 10000000 == 0:
                print(f"{i} bytes out of {file_size} processed")

            # If you found the start of a file, keep building
            if len(current_file) > 0:
                current_file = b''.join([current_file, buffer[-1]])

            # If you find the EOF indicator, finish the file if
            # it has been started. Store data in list of files.
            if (buffer[window_size - len(PDF_EOF):] == PDF_EOF and
                    len(current_file) > 0):
                if pdf13:
                    files.append(current_file)
                    eof_indices.append(i)
                    current_file = b''
                    print(f"Found PDF: EOF={i}, buffer={buffer}")
                else:
                    pdf13 = True

            # Start building PDF file
            if buffer == PDF13_SOF:
                print(f"Found PDF v1.3: SOF={i}, buffer={buffer}")
                current_file = b''.join(buffer)
                sof_indices.append(i)
            
            # Start building PDF file
            if buffer == PDF15_SOF:
                print(f"Found PDF v1.5: SOF={i}, buffer={buffer}")
                current_file = b''.join(buffer)
                sof_indices.append(i)
                pdf13 = False

            # increment byte position
            i += 1

        print(f"\nFound {len(files)} PDF files.")
        for i, each_file in enumerate(files):
            filename = f"{OUTPUT_DIR}/pdf_file_{i}.pdf"
            with open(filename, "wb") as out_file:
                print(f"\nWrite output file: {filename}")
                out_file.write(each_file)
            file_info = test_magic(filename)
            print(f"Type of file: {file_info}")
            print(f"File Size: {os.path.getsize(filename)} bytes")
            print(f"Start Offset: {sof_indices[i]}")
            print(f"End Offset: {eof_indices[i]}")


def hash_file(input_file):
    '''Take input file and return hashed hex string'''
    print(f"MD5 Hashing {input_file}.")
    with open(input_file, 'rb') as in_f:
        hash_hex = md5(in_f.read()).hexdigest()
        print(f"Hash hex found: {hash_hex}")
        return hash_hex


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
    scan_for_png(args.file)
    scan_for_pdf(args.file)

    print(f"\nGenerate MD5 hashes of the files in {OUTPUT_DIR}/.")
    with open(f'{OUTPUT_DIR}/hashes.txt', 'wt', encoding='ascii') as f:
        f.write("Source File -> MD5 Hash\n")
        for out_file in glob(f"{OUTPUT_DIR}/*"):
            if "txt" not in out_file:
                f.write(f"{out_file} -> {hash_file(out_file)}\n")


if __name__ == "__main__":
    main()
