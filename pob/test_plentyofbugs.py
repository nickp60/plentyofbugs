#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import os
from . import plentyofbugs as pob
from . import get_n_genomes as gng

#####  Pob tests
def test_get_best_mash_result():
    mash_results = [
        ['./genomes_of_niss/NC_007350.1.fasta', 'tmp/assembly/contigs.fasta', '0.3', '1', '0/1000'],
        ['./genomes_of_niss/NZ_CP014057.2.fasta', 'tmp/assembly/contigs.fasta', '0.6', '1', '0/1000'],
        ['./genomes_of_niss/NZ_CP014113.2.fasta', 'tmp/assembly/contigs.fasta', '.99', '1', '0/1000'],
        ['./genomes_of_niss/NZ_CP022056.1.fasta', 'tmp/assembly/contigs.fasta', '1', '1', '0/1000'],
        ['./genomes_of_niss/NZ_CP022093.1.fasta', 'tmp/assembly/contigs.fasta', '.15', '1', '0/1000'],
        ['./genomes_of_niss/NZ_LT963436.1.fasta', 'tmp/assembly/contigs.fasta', '.004', '1', '0/1000'],
        ['']
    ]
    test_result = pob.get_best_mash_result(mash_results)
    print(test_result)
    assert ["./genomes_of_niss/NZ_LT963436.1.fasta", .004] == test_result

###########################    get n genomes tests #####################
proks_file = "test_proks.txt"

def test_download_proks():
    if not os.path.exists(proks_file):
        gng.fetch_prokaryotes(dest=proks_file)
    assert os.path.exists(proks_file),  "error downloading prrokaryotes.txt"

def test_get_lines():
    org = "Escherichia coli"
    lines = gng.get_lines_of_interest_from_proks(path=proks_file,
                                                      org=org)
    print(lines)
    assert "PRJNA315511" in  [x[2] for x in lines],  "PRJNA315511 not found!!"

def test_get_names():
    org = "Escherichia coli"
    lines = gng.get_lines_of_interest_from_proks(path=proks_file,
                                                      org=org)
    names = []
    for line in lines:
        name = gng.parse_name_from_proks_line(line)
        print(name)
        names.append(name)

    assert "CP017061.1" in names,  "CP017061.1 not found!!"
