#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Nick Waters
"""

import os
import sys
import subprocess
import argparse
import shutil
from random import shuffle

def get_args():  # pragma nocover
    parser = argparse.ArgumentParser(
        description="Download a number of complete genomes for a given organism ",
        add_help=True)
    parser.add_argument(
        "-o",
        "--organism_name",
        help="organism_name",
        required=True)
    parser.add_argument(
        "-g",
        "--genomes_dir",
        help="path to output dir",
        required=True)
    parser.add_argument(
        "-n", "--nstrains",
        help="",
        type=int,
        required=True)

    parser.add_argument(
        "-p",
        "--prokaryotes",
        action="store",
        help="path_to_prokaryotes.txt",
        default="prokaryotes.txt")
    return(parser.parse_args())


def fetch_prokaryotes(dest):
    subprocess.run(
        "wget ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt -O " + dest,
        shell=sys.platform != "win32",
        check=True)


def parse_name_from_proks_line(line):
    seq_name = line[8].split(":")[1].split(";")[0].split("/")[0]
    return seq_name


def make_fetch_cmds(org_lines, nstrains, genomes_dir, SHUFFLE=True):
    if SHUFFLE:
        shuffle(org_lines)
    # # now we shuffle the file, get the top n lines, and  split apart the
    # # chromosome:NZ_CP013218.1/CP013218.1; plasmid paadD:NZ_CP014695.1/CP014695.1; plasmid plinE154:NZ_CP014694.1/CP014694.1
    # # to
    # # NZ_CP013218.1
    # # Note that we only get the first chromasome for a given entry. Sorry vibrioists
    #for line in org_lines:
    #    sys.stderr.write(line[8].split(":")[1].split(";")[0].split("/")[0])
    cmds = []
    for line in org_lines[0:nstrains]:
        # print(line)
        shortname = parse_name_from_proks_line(line)
        name = os.path.basename(line[20])
        full_path = os.path.join(
            line[20],
            name + "_genomic.fna.gz")
        cmd = "wget " + full_path + " -O " + os.path.join(
            genomes_dir, shortname + ".fna.gz")
        # no idea why some of the ftp paths are empty/ "-".
        # Take a look at  CP043199.1 CP043211 for examples
        if name != "-":
            cmds.append(cmd)
    return cmds


def get_lines_of_interest_from_proks(path,  org):
    # column 9 has the nucc accession if it is a complete genome, or a "-" if empt
    # it starts with chromasome
    # here we select the lines for all the complete genomes,
    # find the lines matching out query
    # and save a list with the results
    org_lines = []
    # this should be caught elsewhere (as an arg if run this a script, or in
    # checking before calling main from plentyofbugs
    assert org is not None, "organism name must be provided"
    with open(path, "r") as proks:
        for line in proks:
            splitline = line.strip().split("\t")
            if splitline[8].startswith("chrom"):
                if splitline[0].startswith(org):
                    org_lines.append(splitline)
    # for line in org_lines:
    #    sys.stderr.write(line[20])
    # # if file is empty, raise an error
    if len(org_lines) == 0:
        sys.stderr.write("no " + org +
              " matches in the prokaryotes.txt file\n")
    return org_lines


def main(args=None):
    if args is None:
        args = get_args()
    try:
        os.makedirs(args.genomes_dir)
    except:
        sys.stderr.write("using exisiting genomes directory...\n")
    if not os.path.exists(args.prokaryotes):
        fetch_prokaryotes(dest=args.prokaryotes)
    org_lines = get_lines_of_interest_from_proks(path=args.prokaryotes,
                                                 org=args.organism_name)
    if args.nstrains == 0:
        args.nstrains = len(org_lines)
    cmds = make_fetch_cmds(
        org_lines,
        nstrains=args.nstrains,
        genomes_dir=args.genomes_dir,
        SHUFFLE=True)
    for i, cmd in enumerate(cmds):
        sys.stderr.write("Downloading genome %i of %i\n%s\n" %(i + 1, len(cmds), cmd))
        subprocess.run(
            cmd,
            shell=sys.platform != "win32",
            check=True)

    unzip_cmd = "gunzip " + os.path.join(args.genomes_dir, "*.gz")
    sys.stderr.write(unzip_cmd + "\n")
    subprocess.run(
        unzip_cmd,
        shell=sys.platform != "win32",
        check=True)


# if __name__ ==  "__main__":
#     args = get_args()
#     try:
#         os.makedirs(args.genomes_dir)
#     except:
#         sys.stderr.write("genomes output directory already exists!\n")
#         sys.exit(1)
#     main(args)
