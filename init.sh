#!/bin/bash
#export PYTHONPATH=''
#source ~/.virtualenvs/fuitdb2/bin/activate
apt-get update
apt-get install -y unzip
pip install -U -r requirements.txt
cp data/fruits-360_dataset_2018_02_08.zip input/
cd data
unzip fruits-360_dataset_2018_02_08.zip
cd ..
python classify_fruits.py
