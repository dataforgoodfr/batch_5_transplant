#!/usr/bin/env bash

export PATH="/anaconda3/bin:$PATH"
conda create -n transplant python=3.5
conda install -n transplant --yes --file requirements.txt
while read requirement; do conda install -n transplant --yes $requirement; done < requirements.txt
conda env export --name transplant | grep -v "^prefix: " > environment_linux.yml
source activate transplant
pip install --upgrade pip
pip install .
pip install ipykernel
ipython kernel install --user --name=transplant