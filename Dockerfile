FROM python:3
MAINTAINER Nick Waters <nickp60@gmail.com>

RUN apt-get update && apt-get install -y \
			       ncbi-blast+ \
			       mummer \
			       seqtk -y
# why, you ask, are we woth installing stuff with and without pip
# conda pyani fails to build becasue of c extensions with numpy, so pip
# but building skesa from source fails mysteriously
# so we install just skesa with conda, and use pip for everything else

# install conda
RUN curl -o miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash miniconda3.sh -b -p /bin/miniconda/

# this fails compilation for some reason, both with and without the -f `Makefile.nongs`
# RUN git clone https://github.com/ncbi/SKESA && cd SKESA && make -f Makefile.nongs

# install skesa
RUN /bin/miniconda/bin/conda install -c bioconda skesa

# get plentyofbugs and pyani
RUN git clone https://github.com/nickp60/plentyofbugs
RUN git clone https://github.com/widdowquinn/pyani

# develop, not install, because of setup.py packages declaration
RUN cd pyani && git checkout development && python setup.py develop
#  for that get_genomes.py script
RUN pip install pyutilsnrw
# test
RUN pyani --help
WORKDIR plentyofbugs
ENV PATH="$PATH:/bin/miniconda/bin"
RUN ./plentyofbugs -h
