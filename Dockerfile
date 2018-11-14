FROM python:3
MAINTAINER Nick Waters <nickp60@gmail.com>

RUN apt-get update && apt-get install -y \
			       ncbi-blast+ \
			       mummer \
			       seqtk \
		               build-essential \
			       libboost-all-dev -y  \
			       && \
    pip3 install --upgrade pip && \
    pip3 install pyani
#RUN pip3 uninstall pyani
RUN git clone https://github.com/ncbi/SKESA && cd SKESA && make -f Makefile.nongs
RUN git clone https://github.com/nickp60/plentyofbugs
RUN git clone https://github.com/widdowquinn/pyani
RUN cd pyani && git checkout development && python setup.py develop
# test
RUN pyani
RUN pyani --help
