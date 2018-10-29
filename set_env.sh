#!/usr/bin/env bash

conda create -n transplant python=3.5
conda install -n transplant --yes --file requirements.txt
while read requirement; do conda install -n transplant --yes $requirement; done < requirements.txt
conda env export --name transplant | grep -v "^prefix: " > environment_linux.yml
