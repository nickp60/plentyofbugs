FROM continuumio/miniconda3
RUN conda config --add channels defaults
RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge
RUN conda install seqtk skesa spades mummer
RUN git clone https://github.com/nickp60/plentyofbugs
RUN git clone https://github.com/widdowquinn/pyani
RUN cd pyani && git checkout development && python setup.py develop
# test
RUN pyani
RUN pyani --help
