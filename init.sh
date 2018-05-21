#!/bin/bash
#export PYTHONPATH=''
#source ~/.virtualenvs/fuitdb2/bin/activate
#apt-get update
#apt-get install -y unzip
pip install -U -r requirements.txt
mkdir -p /code/input
cd /code/input
cp /code/data/fruits-360_dataset_2018_02_08.zip .
unzip fruits-360_dataset_2018_02_08.zip
cd /code
pwd
ls -al
#sleep 600
python classify_fruits.py
