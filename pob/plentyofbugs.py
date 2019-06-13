#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
"""

POB_VERSION=0.87

import argparse
import sys
import time
import os
import traceback
import shutil

from Bio import SeqIO
from . import get_n_genomes


# --------------------------- methods --------------------------- #


def get_args(test_args=None):  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Get the closest reference genome for an isolate ")
    parser.add_argument(
        "-e", "--experiment_name", action="store",
        help="name of the experiment", required=True)
    parser.add_argument(
        "-f", "--readsF", action="store",
        help="forward reads", required=True)
    parser.add_argument(
        "-d", "--outdir", action="store",
        help="output directory", required=True)
    parser.add_argument(
        "-r", "--readsR", action="store",
        help="reverse reads", required=False)
    parser.add_argument(
        "-n", "--nstrains", action="store",
        help="number of strains", required=True)
    parser.add_argument(
        "-o", "--organism_name", action="store",
        help="'Genus species', in quotes", required=True)
    parser.add_argument(
        "--assembler", action="store",
        choices=["skesa", "spades"],
        default="skesa",
        help="assembler to use", required=False)
    parser.add_argument(
        "-m", "--distance_method", action="store",
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
        help="path to output dir",
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
        help="downsampling ammount must be a float between 0.1 and .9999, or a number of reads",
        type=float,
        default=.9999,
        required=False)
    if test_args is None:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(test_args)
    if args.downsampling_ammount < .1:
        raise ValueError(args.downsampling_ammount, "invalid value")
    if args.downsampling_ammount > 1 and args.downsampling_ammount < 10:
        raise ValueError(args.downsampling_ammount, "invalid value")
    if args.method == "pyani":
        print("Error: please run PlentyOfBugs via a docker version < 0.88 to use pyani")
        sys.exit(1)
    return args

def  main():
    print("PlentyOfBugs version: $POB_VERSION")
    # check for rrequired programs
    args = get_args()
    for prog in [args.assembler, "mash", "wget"]:
        if shutil.which(prog) is None:
            print(prog + "not found in PATH! exiting...")
            sys.exit(1)
    if os.path.exists(args.outdir):
        print("Output directory already exists! exiting...")
        sys.exit(1)
    #############################   Run Mini Assembly  #########################
    if args.assembly is None:
        # downsample
        cmds = []
        dsdir = os.path.join(args.output,"downsampled_reads")
        ds_readsF = os.path.join(args.output,"downsampled_reads", "reads1.fq")
        os.makesdirs(ds_dir)
        ds_cmd_1 = str(
            "seqtk sample -s100 {args.readsF}  {args.downsampling_ammount} " +
            "> {ds_readsF}").format(**locals())
        cmds.append(ds_cmd_1)
        if args.readsR is not None:
            ds_readsR = os.path.join(args.output,"downsampled_reads", "reads2.fq")
            ds_cmd_1 = str(
                "seqtk sample -s100 {args.readsR}  {args.downsampling_ammount} " +
                "> {ds_readsR}").format(**locals())
            cmds.append(ds_cmd_2)
            SPADES_STRING="-1 {ds_cmd_1} -2 {ds_cmd_2}".format(**locals())
            SKESA_STRING="{ds_cmd_1} {ds_cmd_2}".format(**locals())
        else:
            SPADES_STRING="-s {ds_cmd_1} ".format(**locals())
            SKESA_STRING="{ds_cmd_1}".format(**locals())
        assembly_dir = os.path.join(args.output, "assembly")
        args.assembly = os.path.join(assembly_dir, "contigs.fasta")
        if args.assembler == "skesa":
            os.path.makedirs(assembly_dir)
            assembly_cmd = str(
                "skesa --fastq {SKESA_STRING} --cores {args.threads}" +
                "--contigs_out {args.assembly} 2> " +
                "{args.outdir}/log.txt").format(**locals())
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

    #######################   Download close genomes  ###########################
    if not os.path.exists(args.genomes_dir):
        os.path.makedirs(args.genomes_dir)
    if len(os.listdir(args.genomes_dir)) is None:
        get_n_genomes.main(args)

    if args.method == "pyani":
        pyani_cmds = []
        labels_txt = os.path.join(args.genomes_dir, "labels.txt")
        classes_txt = os.path.join(args.genomes_dir, "classes.txt")
        for path in ["labels.txt", "classes.txt"]:
            if os.path.exists( path)):
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
            "pyani anim {args.genomes_dir} {args.outdir}pyani --workers {args.threads}  --dbpath {pyanidb} -v --labels {labels_txt} --classes {classes_txt}").format(**locals())
                          )
        pyani_cmds.append("tail -n 1 $OUTDIR/pyani/runs.tab | cut -f 1")
        pyani_cmds.append(str(
            "pyani report -v --runs {args.outdir}pyani  --dbpath {pyanidb}").format(**locals()))

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
# echo "extract best hit"  >> "${LOGFILE}"
# echo "python ${SCRIPTPATH}/parse_closest_ANI.py $OUTDIR/pyani/matrix_identity_${this_run}.tab > ${OUTDIR}/best_reference"  >&2
# python ${SCRIPTPATH}/parse_closest_ANI.py $OUTDIR/pyani/matrix_identity_${this_run}.tab > ${OUTDIR}/best_reference

# bestref=$(cat ${OUTDIR}/best_reference)
# # this should be the only line going to stdout
# #  #pipergonnapipe
# echo -e "${NAME}\t${bestref}"
if __name__ == "__main__":
    main()
