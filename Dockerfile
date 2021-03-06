FROM python:3
MAINTAINER Nick Waters <nickp60@gmail.com>

RUN apt-get update && apt-get install -y \
			       ncbi-blast+ \
			       #mummer \
			       seqtk -y
# why, you ask, are we both installing stuff with and without pip
# conda pyani fails to build becasue of c extensions with numpy, so pip
# but building skesa from source fails mysteriously
# so we install just skesa with conda, and use pip for everything else

# install conda
RUN curl -o miniconda3.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash miniconda3.sh -b -p /bin/miniconda/

# this fails compilation for some reason, both with and without the -f `Makefile.nongs`
# RUN git clone https://github.com/ncbi/SKESA && cd SKESA && make -f Makefile.nongs

# install skesa
RUN /bin/miniconda/bin/conda install -c bioconda skesa mash
#  for that get_genomes.py script
# RUN pip install pyutilsnrw

## get plentyofbugs
#####  Production
RUN pip install plentyofbugs==0.97

#####  Dev
#ADD . /plentyofbugs/
#RUN cd /plentyofbugs/ &&	python setup.py install
# test
#RUN plentyofbugs -f ./test_data/test_reads1.fq --genus_species "Escherichia coli" -n 3 -o ./tmp/ -h
# RUN rm -rf tmp
#run which plentyofbugs
#WORKDIR plentyofbugs
#RUN wget ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt
ENV PATH="$PATH:/bin/miniconda/bin"
ENTRYPOINT [ "/usr/local/bin/plentyofbugs" ]
