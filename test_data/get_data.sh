#!/bin/bash

###################################  Download the plasmid sequences ##################
# run this from the test_data dir
cat ../prokaryotes.txt | grep "Escherichia coli" |grep "plasmid" | head -n 20 > tmp_out
cat tmp_out | cut -f 9 | cut -f 2,3 -d " " | sed "s/^plas[^:]*://" |sed "s/[;\/].*//" >tmp_accessions
head -n 1 tmp_accessions  >test_accession
tail -n+2 tmp_accessions  >plasmid_accessions
# use get_genomes.py from pyutilsnrw
get_genomes.py -i plasmid_accessions -f fasta  -o plasmids/
get_genomes.py -i test_accession -f fasta  -o ./

rm tmp_out
rm tmp_accessions

###########################  Generate samle reads  ##################
# install ART, if you haven't already
# https://www.niehs.nih.gov/research/resources/software/biostatistics/art/
art_illumina -ss HS25 -i ./NC_017659.1.fasta -l 150 -f 10 -o test_reads1

############################  Generate sample assembly  ##################
skesa --fastq ./test_data/test_reads1.fq  > contigs.fasta
