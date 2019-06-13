#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from . import plentyofbugs as pob


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
