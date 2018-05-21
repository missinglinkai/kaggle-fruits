#!/bin/bash
#source ~/.virtualenvs/fuitdb2/bin/activate
#apt-get update && apt-get install -y unzip
pip install -q -U -r requirements.txt
mkdir -p /code/input
cd /code/input
cp /code/data/fruits-360_dataset_2018_02_08.zip .
unzip -qq fruits-360_dataset_2018_02_08.zip
cd /code
python classify_fruits.py
