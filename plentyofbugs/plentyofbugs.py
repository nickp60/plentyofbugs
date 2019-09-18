#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
"""

import argparse
import sys
import time
import os
import glob
import traceback
import shutil
import subprocess

from . import get_n_genomes
from . import _version

# --------------------------- methods --------------------------- #


def get_args(test_args=None):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Get the closest reference genome for an isolate ")
    parser.add_argument(
        "-f", "--readsF", action="store",
        help="forward reads", required=False)
    parser.add_argument(
        "-o", "--output", action="store",
        help="output directory", required=True)
    parser.add_argument(
        "-r", "--readsR", action="store",
        help="reverse reads", required=False)
    parser.add_argument(
        "-n", "--nstrains", action="store",
        type=int,
        help="number of strains; enter 0 for all", required=False)
    parser.add_argument(
        "--genus_species", dest="organism_name", action="store",
        help="'Genus species', in quotes", required=False)
    parser.add_argument(
        "--assembler", action="store",
        choices=["skesa", "spades"],
        default="skesa",
        help="assembler to use", required=False)
    parser.add_argument(
        "-m", "--method", action="store",
        choices=["pyani", "mash"],
        default="mash",
        dest="method",
        help="method to calculate genomic distances; use pyani " +
        "for accuracy, and mash for speed", required=False)
    parser.add_argument(
        "-p",
        "--prokaryotes",
        action="store",
        default="prokaryotes.txt",
        help="path_to_prokaryotes.txt",
        required=False)
    parser.add_argument(
        "-g",
        "--genomes_dir",
        help="path to genomes dir. Creates " +
        "it if it  doesnt exist",
        required=False)
    parser.add_argument(
        "-a",
        "--assembly",
        help="path to assembly",
        required=False)
    parser.add_argument(
        "-t",
        "--threads",
        default=4,
        type=int,
        help="number of threads to try to use",
        required=False)
    parser.add_argument(
        "--downsampling_ammount",
        help="For assembly; downsampling amount must be a float between 0.1 and .9999, or a number of reads",
        type=float,
        default=.9999,
        required=False)
    if test_args is None:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(test_args)
    if args.genomes_dir is None:
        args.genomes_dir = "plentyofbugs_genomes"
    if not os.path.isdir(args.genomes_dir):
        os.makedirs(args.genomes_dir)
    if args.downsampling_ammount < .1:
        raise ValueError(args.downsampling_ammount, "invalid value")
    if args.downsampling_ammount > 1 and args.downsampling_ammount < 10:
        raise ValueError(args.downsampling_ammount, "invalid value")
    if args.method == "pyani":
        print("Error: please run PlentyOfBugs via a docker version < 0.88 to use pyani")
        sys.exit(1)
    if len(os.listdir(args.genomes_dir)) == 0 :
        if  args.organism_name is None:
            print("Error: if genomes_dir is empty, must provide --genus_species")
            sys.exit(1)
        if args.nstrains is None:
            print("Error: if genomes_dir is empty, must provide --nstrains")
            sys.exit(1)
    if args.readsF is None and args.assembly is None:
        print("Error: Must provide either --readsF or --assembly!")
        sys.exit(1)
    return args


def get_closest_ANI(path):
    matrix = []
    with open(sys.argv[1], 'r') as inf:
        for line in inf:
            thisline = line.strip().split("\t")
            matrix.append(thisline)
        # for i,x in enumerate(thisline):
        #     if x == "contigs" or x == "scaffolds":
                # print(i + 2) # unix indexes at 1, and line starts with a blak tab
                #                 sys.exit()

    # raise ValueError("contigs not found in header")
    # just start by getting the first forward comparison (ie, the vertical part of the matrix
    # we assume rthere is just one entry

    # lets transpose this
    tmatrix = list(map(list, zip(*matrix)))
    # print(tmatrix)

    # get the index of the row/column with id "contigs*
    contigs_idx = [i for i, x in enumerate(tmatrix) if x[0].startswith("contigs") or x[0].startswith("run")][0]
    # print(contigs_idx)

    # select our headers
    headers = matrix[0]
    # note here that we have to trim the first column from the row of interest, we have one less header column than the rest of the rows, cause the first one is empty
    line_of_interest = sorted(zip(headers, tmatrix[contigs_idx][1:]), key=lambda x: x[1], reverse=True)
    # print(line_of_interest)
    # bam
    # we need to do this stupid loop thing because if there is a score tie, the contigs
    # entry won't neccesdarily be first.  So, we go through the line, printing the first entry that doesnt start with "contigs" and isn't identical (probably an artifact)
    for pair in line_of_interest:
        # the new version appends _## to the names
        if not (pair[0].startswith("contigs") or pair[0].startswith("run")) and pair[1] != "1":
            closest_id = "_".join(pair[0].split("_")[0:-1])
            closest_id_perc = pair[1]
            return("{0}\t{1}".format(closest_id, closest_id_perc))


def get_best_mash_result(mash_results):
    # be aware there is an empty line at the end
    max_org = [[float(x[2]), x[0]] for x in mash_results[0:-1]]
    max_org.sort(reverse=False)
    return([max_org[0][1], max_org[0][0]])


def main():
    print("PlentyOfBugs version " + _version.__version__)
    # check for required programs
    args = get_args()
    args.output = os.path.join(args.output, "")
    args.genomes_dir = os.path.join(args.genomes_dir, "")
    for prog in [args.assembler, "mash", "wget"]:
        if shutil.which(prog) is None:
            print(prog + "not found in PATH! exiting...")
            sys.exit(1)
    if os.path.exists(args.output):
        print("Output directory already exists! exiting...")
        sys.exit(1)
    else:
        os.makedirs(args.output)
    #######################   Download close genomes  #########################
    if len(glob.glob(args.genomes_dir + "*.f*a"))  == 0:
        if args.organism_name is None:
            print("No fasta (*.f*a) file in genomes directory; must provide --genus_species")
            sys.exit(1)
        get_n_genomes.main(args)
    #############################   Run Mini Assembly  ########################
    if args.assembly is None:
        # downsample
        cmds = []
        ds_dir = os.path.join(args.output,"downsampled_reads")
        ds_readsF = os.path.join(args.output,"downsampled_reads", "reads1.fq")
        os.makedirs(ds_dir)
        ds_cmd_1 = str(
            "seqtk sample -s100 {args.readsF}  {args.downsampling_ammount} " +
            "> {ds_readsF}").format(**locals())
        cmds.append(ds_cmd_1)
        if args.readsR is not None:
            ds_readsR = os.path.join(args.output,"downsampled_reads", "reads2.fq")
            ds_cmd_2 = str(
                "seqtk sample -s100 {args.readsR}  {args.downsampling_ammount} " +
                "> {ds_readsR}").format(**locals())
            cmds.append(ds_cmd_2)
            SPADES_STRING="-1 {ds_readsF} -2 {ds_readsR}".format(**locals())
            SKESA_STRING="{ds_readsF} {ds_readsR}".format(**locals())
        else:
            SPADES_STRING="-s {ds_readsF} ".format(**locals())
            SKESA_STRING="{ds_readsF}".format(**locals())
        assembly_dir = os.path.join(args.output, "assembly")
        args.assembly = os.path.join(assembly_dir, "contigs.fasta")
        if args.assembler == "skesa":
            os.makedirs(assembly_dir)
            assembly_cmd = str(
                "skesa --fastq {SKESA_STRING} --cores {args.threads} " +
                "--contigs_out {args.assembly} 2> " +
                "{args.output}/log.txt").format(**locals())
        else:
            assembly_cmd = str(
                "spades.py {SPADES_STRING} -o {assembly_dir} -t " +
                "{args.threads}").format(**locals())
        cmds.append(assembly_cmd)
        for cmd in cmds:
            print(cmd)
            subprocess.run(
                cmd,
                shell=sys.platform!="win32",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True)

    #######################   Find closest  ###########################

    if args.method == "pyani":
        pyani_cmds = []
        labels_txt = os.path.join(args.genomes_dir, "labels.txt")
        classes_txt = os.path.join(args.genomes_dir, "classes.txt")
        for path in ["labels.txt", "classes.txt"]:
            if os.path.exists(path):
                os.remove(os.path.join(args.genomes_dir, path))
        pyani_index = "pyani index {args.genomes_dir} -v"
        pyani_cmds.append(pyani_index)
        # then fix the columns; we dont care about the name
        fix_labels_cmds = [
            "paste <(cut -f 1,2 $GENOMESDIR/classes.txt) <(cut -f 2 $GENOMESDIR/classes.txt) > tmp_classes",
            "mv tmp_classes $GENOMESDIR/classes.txt"
            "paste <(cut -f 1,2 $GENOMESDIR/labels.txt) <(cut -f 2 $GENOMESDIR/labels.txt) > tmp_labels",
            "mv tmp_labels $GENOMESDIR/labels.txt"
        ]
        pyani_cmds.extend(fix_labels_cmds)
        pyanidb = os.path.join(args.genomes_dir, "pyani", "pyanidb")
        if not os.path.exists(pyanidb):
            pyani_cmds.append("pyani createdb --dbpath ${GENOMESDIR}/.pyani/pyanidb")
        pyani_cmds.append(str(
            "pyani anim {args.genomes_dir} {args.output}pyani --workers {args.threads}  --dbpath {pyanidb} -v --labels {labels_txt} --classes {classes_txt}").format(**locals())
                          )
        pyani_cmds.append("tail -n 1 $OUTDIR/pyani/runs.tab | cut -f 1")
        pyani_cmds.append(str(
            "pyani report -v --runs {args.output}pyani  --dbpath {pyanidb}").format(**locals()))

        for cmd in pyani_cmds:
            print(cmd)
            subprocess.run(cmd,
                shell=sys.platform!="win32",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True)
        ############# remove contigs from genomes dir if we plan on reusing   ########
        # get rid of the fasta and md5
        for path in glob.glob(os.path.join(args.genomes_dir, "contigs_")):
            os.remove(path)
        parse_closest_ANI(path)
    else:
        mash_cmds = []
        #
        mash_sketch = os.path.join(args.genomes_dir, "reference.msh")
        if not os.path.exists(mash_sketch):
            mash_cmds.append(
                "mash sketch -o {mash_sketch} {args.genomes_dir}*.f*a".format(
                    **locals()))
        mash_cmds.append("mash dist {mash_sketch} {args.assembly}".format(
            **locals()))
        cmds_results = mash_cmds
        for i, cmd in enumerate(mash_cmds):
            print(cmd)
            cmds_results[i] = subprocess.run(
                cmd,
                shell=sys.platform!="win32",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True)
        mash_results = [x.split("\t") for x in cmds_results[-1].stdout.decode().split("\n")]
        best_reference = get_best_mash_result(mash_results)
    with open(os.path.join(args.output, "best_reference"), "w") as outf:
        print("\t".join([str(x) for x in best_reference]))
        outf.write("\t".join([str(x) for x in best_reference]) + "\n")




if __name__ == "__main__":
    main()
