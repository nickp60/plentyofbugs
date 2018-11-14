FROM python:3
MAINTAINER Nick Waters <nickp60@gmail.com>

RUN apt-get update && apt-get install -y \
			       ncbi-blast+ \
			       mummer \
			       seqtk -y
RUN which python
RUN  curl -o miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash miniconda3.sh -b -p /bin/miniconda/
RUN which python

# this fails compilation for some reason, both with and without the -f `Makefile.nongs`
# RUN git clone https://github.com/ncbi/SKESA && cd SKESA && make -f Makefile.nongs

RUN /bin/miniconda/bin/conda install -c bioconda skesa

RUN git clone https://github.com/nickp60/plentyofbugs
RUN git clone https://github.com/widdowquinn/pyani
RUN cd pyani && git checkout development && python setup.py develop
# test
RUN pyani --help
WORKDIR plentyofbugs
ENV  PATH="$PATH:/bin/miniconda/bin"
RUN ./plentyofbugs -h
