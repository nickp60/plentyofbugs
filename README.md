# plentyofbugs
![plentyofbugslogo](https://github.com/nickp60/plentyofbugs/blob/master/icon/pob.png)

Find your sequenced isolate a compatable reference genome based on location, interests, and mash distance.


This repository contains the pipeline to identity a suitable reference isolate based on comparing a mini assembly to a set of complete genomes via [mash](https://github.com/marbl/Mash). For more information on using this with riboSeed, see [this page on choosing reference genomes](https://riboseed.readthedocs.io/en/latest/REFERENCE.html).

# Installation

# Manual Installation
## Dependencies
plentyofbugs requires
- skesa (or spades)
- seqtk
- mash

```
conda create pob skesa seqtk mash
conda activate pob
pip install plentyofbugs
plentyofbugs  -h
```

# Running
## Get example data
The data in the `test_data` directory was gathered using the `test_data/get_data.sh` script. It consists of 19 plasmids from E coli, and a test plasmid from which reads were generated using ART. https://www.niehs.nih.gov/research/resources/software/biostatistics/art/. The contigs in this diretory were made with SKESA.

## Running on example data

```
# running with raw reads
plentyofbugs -g ./test_data/plasmids/  -f ./test_data/test_reads1.fq -o tmp
# running with an assembly instead of raw reads
plentyofbugs -g ./test_data/plasmids/  --assembly ./test_data/contigs.fasta -o tmp
# running on a new cast of E coli genomes to compare to, downloading the required genomes on the way
plentyofbugs -g ./new_comparison_e_coli/ -n 5  --assembly ./test_data/contigs.fasta -o tmp --genus_species "Escherichia coli"
```


## Just want the download the genomes?
Plentyofbugs includes the genomes-getter as a standalone script: `get_n_genomes`.
```
get_n_genomes -o "Escherichia coli" -g tmpnewgenomes -n 4
```


# Running via container
NOTE: To run the legacy version that used pyani, run a version older than 0.87 with Docker or singularity -- it will save yourself a lot of trouble!

## Docker
```
docker run --rm -t -v  ${PWD}:/data/ nickp60/plentyofbugs:0.97 -f /data/test_reads1.fq --genus_species "Escherichia coli" -n 5 -o /data/results/
```
which is

```
docker run --rm -t -v  <current directory>:/data/ nickp60/plentyofbugs:0.97  -f /data/<name of F reads file> --genus_species "<bug of interest>" -n <max number of strains to compare with>  -o /data/<name for output folder>/
```

## Singularity

```
singularity pull docker://nickp60/plentyofbugs:0.97
plentyofbugs:0.92.sing -f ./test_reads1.fq --genus_species "Escherichia coli" -n 5  -o ./results/
```

# Under the hood
## What it does:
1. Runs a mini assembly with skesa or SPAdes
2. Identify which complete genomes are available for the genus and species
3. *optional* Subset number of complete genomes
4. Download reference genomes
5. Indexes/sketches genomes
6. Calculate the Mash distance/ANI of the mini assembly to the database of reference strains
7. Report the closest reference genome and the distance/ANI
