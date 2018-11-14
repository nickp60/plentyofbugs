# plentyofbugs
![plentyofbugslogo](https://github.com/nickp60/plentyofbugs/blob/master/icon/pob.png)

Find your sequenced isolate a compatable reference genome based on location, interests, and anverage nucleotide identity

# Installation
## dependencies
plentyofbugs requires
- the `development` branch of pyani
- skesa
- mummer
- seqtk

# Running

Run this with docker. you will pull out less hair in the long run

```
docker run -v  ~/GitHub/riboSeed/riboSeed/integration_data/:/input/ -v ${PWD}:/output/ -t nickp60/plentyofbugs ./plentyofbugs -f /input/test_reads1.fq -o "Escherichia coli" -n 5 -e test -d /output/tmptmptmp/
```
which is

```
docker run -v  <input directory>:/input/ -v <where to put your output folder>:/output/ -t nickp60/plentyofbugs ./plentyofbugs -f /input/<name of F reads file> -o "<bug of interest>" -n <max number of strains to compare with>  -e <name of experiment> -d /output/<name for output folder>/
```

# Notes

##  WORK IN PROGRESS

This repository contains the pipeline to identity a suitable reference isolate based on comparing a mini assembly to a set of complete genomes via [pyani](github.com/widdowquinn/pyani).  While this is used for riboSeed, its purpose was deemed different enough to warrant its own repository.  For more information, see [this page on choosing reference genomes](https://riboseed.readthedocs.io/en/latest/REFERENCE.html).
