#!/usr/bin/env python
# MIT License
# 
# Copyright (c) 2025 Joakim Bech
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import hashlib
import logging
import os
import shutil
import sys

from argparse import ArgumentParser
from pathlib import Path

good_hashes = {}
nbr_files_copied = 0
missing_files = []

args = None

def get_parser():
    """ Takes care of script argument parsing. """
    parser = ArgumentParser(description='Arcade Time Capsule ROM checker')

    parser.add_argument('-s', '--source', required=True,
                        action="store",
                        default="",
                        help='ROM source folder')

    parser.add_argument('-d', '--destination', required=False,
                        action="store",
                        default="Roms",
                        help='ROM destination folder')

    parser.add_argument('-f', '--force', required=False, action="store_true",
                        default=False,
                        help='Force overwrite existing files')

    parser.add_argument('-m', '--missing', required=False, action="store_true",
                        default=False,
                        help='Write a "missing.txt" file')

    parser.add_argument('-v', '--verbose', required=False, action="store_true",
                        default=False,
                        help='Output some verbose debugging info')
    return parser


def configure_logging(args):
    """ Set the logging depending on the verbose argument. """
    if args.verbose:
        logging.basicConfig(format='[%(levelname)s]: %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='[%(levelname)s]: %(message)s',
                            level=logging.INFO)


def dump_all_hashes():
    """ Dump hashes of all files expected to be found. """
    for filename, sha256_hash in good_hashes.items():
        logging.info(f"{filename}: {sha256_hash}")


def compute_file_hash(path, filename):
    """ Compute SHA-256 of a file. """
    with open(path + filename, 'rb') as f:
        file_hash = hashlib.sha256()

        while chunk := f.read(4096):
            file_hash.update(chunk)

        return file_hash.hexdigest()


def copy_file(source, dest, filename, force=False):
    """ Copy a file from source to dest (possible to force). """
    global nbr_files_copied
    source_file = os.path.join(source, filename)
    destination_file = os.path.join(dest, filename)
    
    if not os.path.exists(dest):
        os.makedirs(dest)
    
    if not os.path.exists(destination_file):
        shutil.copy2(source_file, destination_file)
        nbr_files_copied += 1
        logging.debug(f"File '{filename}' copied successfully from {source} to {dest}")
    else:
        # Check the hash of the already existing file that we eventually want
        # to overwrite when using the force flag.
        hex_digest = compute_file_hash(dest, filename)
        if hex_digest != good_hashes[filename]:
            if force:
                logging.debug(f"Found unexpected hash for {dest + filename} (force set, overwriting existing file)")
                shutil.copy2(source_file, destination_file)
                nbr_files_copied += 1
        else:
            logging.debug(f"File '{filename}', already exists")


def find_files(source):
    """ Lists all files in the given directory. """
    try:
        dir_path = Path(source)
        if not dir_path.is_dir():
            print(f"Not a directory: {source}")
            sys.exit()
        
        files = [f.name for f in dir_path.iterdir() if f.is_file()]
        return files
    
    except FileNotFoundError:
        print(f"Directory not found: {source}")
        return []


def check_file(source, filename, force, destination = None):
    """ Main function to traverse, check and copy files. """
    good_hash = False

    # Don't spend time on computing hashes on files that doesn't even match by
    # name.
    if filename not in good_hashes:
        return

    hex_digest = compute_file_hash(source, filename)

    try:
        if hex_digest == good_hashes[filename]:
            logging.debug(f"Found a good hash for {filename}")
            good_hash = True

        if good_hash:
            copy_file(source, destination, filename, force)
    except KeyError:
        # Ignore unexpected files
        pass


def load_roms_hash_file(filename):
    """ Loads the files with hashes known to be good. """
    print(f"Loading '{filename}'")
    with open(filename, 'r') as f:
        for l in f:
            sha256_hash, filename = l.strip().split('*', 1)
            good_hashes[filename.strip()] = sha256_hash.strip()


def show_missing_files(files, write_to_file):
    """ Prints the Roms missing in the Arcade Time Capsule Roms folder. """
    fh = None
    if write_to_file:
        fh = open("missing.txt", 'w')

    for f in files:
        if write_to_file:
            fh.write(f"{f}\n")
        print(f)
    
    if write_to_file and fh:
        fh.close()


def main():
    global args, nbr_files_copied
    parser = get_parser()
    print("Running Arcade Time Capsule ROM checker")

    args = parser.parse_args()
    configure_logging(args)
    if args.source:
        # Make sure we have an ending slash
        args.source = os.path.join(args.source, "")
        logging.debug(f"Looking for ROMs at {args.source}")

    if args.destination:
        # Make sure we have an ending slash
        args.destination = os.path.join(args.destination, "")
        logging.debug(f"Storing ROMs at {args.destination}")

    load_roms_hash_file("roms.sha256")

    # Get all files in the source directory
    files = find_files(args.source)
    print(f"Found {len(files)} files, start checking ...")
    i = 0
    for f in files:
        check_file(args.source, f, args.force, args.destination)
        if i % 100 == 0:
            print(f"Checked {i} files ...")
        i += 1

    # We're done with the copy stage, let's check what files are missing or
    # incorrect.
    for filename, sha256_hash in good_hashes.items():
        if not os.path.exists(args.destination + filename):
            missing_files.append(filename)
        else:
            hex_digest = compute_file_hash(args.destination, filename)
            if hex_digest != good_hashes[filename]:
                missing_files.append(f"{filename} exist with unexpected hash, expect: {good_hashes[filename]} found: {hex_digest}")

    show_missing_files(missing_files, args.missing)
    print("================================================================================")
    print(f"(*) Copied '{nbr_files_copied}' new files from {args.source} to {args.destination}")
    print(f"(*) If you see *.zip files above, then you're missing these Roms in")
    print(f"    your Arcade Time Capsule installation")


if __name__ == "__main__":
    main()
