# plentyofbugs
![plentyofbugslogo](https://github.com/nickp60/plentyofbugs/blob/master/icon/pob.png)

Find your sequenced isolate a compatable reference genome based on location, interests, and anverage nucleotide identity


This repository contains the pipeline to identity a suitable reference isolate based on comparing a mini assembly to a set of complete genomes via [pyani](github.com/widdowquinn/pyani).  While this is used for riboSeed, its purpose was deemed different enough to warrant its own repository.  For more information, see [this page on choosing reference genomes](https://riboseed.readthedocs.io/en/latest/REFERENCE.html).

# Installation
Run this with Docker or singularity -- it will save yourself a lot of trouble!

# Manual Installation
## dependencies
plentyofbugs requires
- skesa (or spades)
- seqtk
- mash (or pyani, development branch)
```
conda create pob skesa seqtk mash
conda activate pob
python setup.py develop
```
# Running
## Get example data
The data in the `test_data` directory was gathered using the `test_data/get_data.sh` script. It consists of 19 plasmids from E coli, and a test plasmid from which reads were generated using ART. https://www.niehs.nih.gov/research/resources/software/biostatistics/art/.  The contigs in this diretory were made with SKESA.

## Running on example data

```
# running with raw reads
plentyofbugs -g ./test_data/plasmids/  -f ./test_data/test_reads1.fq -o tmp
# running with an assembly instead of raw reads
plentyofbugs -g ./test_data/plasmids/  --assembly ./test_data/contigs.fasta -o tmp
# running on a new cast of E coli genomes to compare to, downloading the required genomes on the way
plentyofbugs -g ./new_comparison_e_coli/ -n 5  --assembly ./test_data/contigs.fasta -o tmp --genus_species "Escherichia coli"
```


## Docker
```
docker run --rm -t -v  ${PWD}:/data/ nickp60/plentyofbugs:0.87 -f /data/test_reads1.fq -o "Escherichia coli" -n 5 -e test -d /data/results/
```
which is

```
docker run --rm -t -v  <current directory>:/data/ nickp60/plentyofbugs:0.87  -f /data/<name of F reads file> -o "<bug of interest>" -n <max number of strains to compare with>  -e <name of experiment> -d /data/<name for output folder>/
```

## Singularity

```
singularity pull docker://nickp60/plentyofbugs:0.87
plentyofbugs:0.87.sing -f ./test_reads1.fq -o "Escherichia coli" -n 5 -e test -d ./results/
```

# Under the hood
## What it does:
1. Runs a mini assembly with skesa or SPAdes
2. Identify which complete genomes are available for the genus and species
3. *optional* Subset number of complete genomes
4. Download reference genomes
with pyani or mash
5. indexes/sketches genomes
6. Calculate the ANI/mash distance  of the mini assembly to the database of reference strains
7. Report the closest reference genone and the ANI
