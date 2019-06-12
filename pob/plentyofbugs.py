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
    if not os.path.exists(args.genomes_dir):
        os.path.makedirs(args.genomes_dir)

    if len(os.listdir(args.genomes_dir)) is None:
        get_n_genomes.main(args)


#     #######################   Download close genomes  ###########################
#     echo "Downloading genomes"  >> "${LOGFILE}"
#     accession_n=$(wc -l < $OUTDIR/accessions)
#     accession_counter=1
#     while read accession
#     do
# 	echo "downloading $accession $accession_counter of $accession_n"
# 	get_genomes.py -q $accession -o $GENOMESDIR   >> "${LOGFILE}"2>&1
# 	accession_counter=$((accession_counter+1))
#     done < $OUTDIR/accessions
# else
#     echo "using existing genomes directory"   >> "${LOGFILE}"
#     # delete any existing "conigs.fasta" file from the dir, as those would be from old runs.
#     # probaly shoudl make this a try/catch thingy
#     # {
#     # 	rm "${GENOMESDIR}/contigs_*.*"
#     # } || {
#     # 	echo "no need to clean genomes dir" &>> "${LOGFILE}"
#     # }
# fi

# echo "copy the mini_assembly result to the potential genomes dir"  >> "${LOGFILE}"
# cp $ASSEMBLY $GENOMESDIR/contigs_${NAME}.fasta

# ##########################   Run ANI analysis  ###############################
# echo "Running pyani index"   >> "${LOGFILE}"
# if [ -f "$GENOMESDIR/labels.txt" ]
# then
#     rm $GENOMESDIR/labels.txt
# fi
# if [ -f "$GENOMESDIR/classes.txt" ]
# then
#     rm $GENOMESDIR/classes.txt
# fi
# echo "pyani index $GENOMESDIR -v -l $PYANILOGFILE"  >&2
# pyani index $GENOMESDIR -v -l $PYANILOGFILE
# echo "recreating pyani labels"   >> "${LOGFILE}"
# # then fix the columns; we dont care about the name
# paste <(cut -f 1,2 $GENOMESDIR/classes.txt) <(cut -f 2 $GENOMESDIR/classes.txt) > tmp_classes
# mv tmp_classes $GENOMESDIR/classes.txt
# paste <(cut -f 1,2 $GENOMESDIR/labels.txt) <(cut -f 2 $GENOMESDIR/labels.txt) > tmp_labels
# mv tmp_labels $GENOMESDIR/labels.txt


# if [ -f "${GENOMESDIR}/.pyani/pyanidb" ]
# then
#     echo "pyani db already exists" >> $PYANILOGFILE
# else
#     echo "pyani createdb --dbpath ${GENOMESDIR}/.pyani/pyanidb"  >&2
#     pyani createdb --dbpath ${GENOMESDIR}/.pyani/pyanidb  >> "${LOGFILE}" 2>&1
# fi

# echo "Running pyani anim"   >> "${LOGFILE}"
# echo "pyani anim $GENOMESDIR $OUTDIR/pyani --workers $CORES  --dbpath ${GENOMESDIR}/.pyani/pyanidb -v -l $PYANILOGFILE --labels $GENOMESDIR/labels.txt --classes $GENOMESDIR/classes.txt"  >&2
# pyani anim $GENOMESDIR $OUTDIR/pyani --workers $CORES  -v -l $PYANILOGFILE --labels $GENOMESDIR/labels.txt --classes $GENOMESDIR/classes.txt --dbpath ${GENOMESDIR}/.pyani/pyanidb >> "${LOGFILE}" 2>&1

# echo "Generating report of pyani runs"   >> "${LOGFILE}"
# echo "pyani report -v -l $PYANILOGFILE --runs $OUTDIR/pyani --dbpath ${GENOMESDIR}/.pyani/pyanidb"  >&2
# pyani report -v -l $PYANILOGFILE --runs $OUTDIR/pyani --dbpath ${GENOMESDIR}/.pyani/pyanidb  >> "${LOGFILE}" 2>&1


# echo "Getting name of most recent pyani run"   >> "${LOGFILE}"
# this_run=$(tail -n 1 $OUTDIR/pyani/runs.tab | cut -f 1)

# echo "Generating genome comparison matrix"   >> "${LOGFILE}"
# echo "pyani report -v -l $PYANILOGFILE --run_matrices $this_run $OUTDIR/pyani --dbpath ${GENOMESDIR}/.pyani/pyanidb"  >&2
# pyani report -v -l $PYANILOGFILE --run_matrices $this_run $OUTDIR/pyani  --dbpath ${GENOMESDIR}/.pyani/pyanidb >> "${LOGFILE}" 2>&1


# # average_nucleotide_identity.py -v -i $GENOMESDIR -g -o $OUTDIR/pyani  &>> "${LOGFILE}"


# ############# remove contigs from genomes dir if we plan on reusing   ########
# # rm $GENOMESDIR/contigs.fasta
# rm $GENOMESDIR/contigs_${NAME}.fasta
# rm $GENOMESDIR/contigs_${NAME}.md5

# echo "extract best hit"  >> "${LOGFILE}"
# echo "python ${SCRIPTPATH}/parse_closest_ANI.py $OUTDIR/pyani/matrix_identity_${this_run}.tab > ${OUTDIR}/best_reference"  >&2
# python ${SCRIPTPATH}/parse_closest_ANI.py $OUTDIR/pyani/matrix_identity_${this_run}.tab > ${OUTDIR}/best_reference

# bestref=$(cat ${OUTDIR}/best_reference)
# # this should be the only line going to stdout
# #  #pipergonnapipe
# echo -e "${NAME}\t${bestref}"
if __name__ == "__main__":
    main()
