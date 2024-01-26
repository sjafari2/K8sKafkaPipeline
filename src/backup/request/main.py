from fastapi import FastAPI
import pandas as pd
from json import loads, dumps
import time
import yaml
from os import listdir
from os.path import isfile, join

with open('pipeline-configmap.yaml', 'r') as file:
    yamlfile = yaml.safe_load(file)

input_path = yamlfile ['data'] ['RequestInputPath']
#print(f" input path is {input_path}")

default_date = '2022-08-22-00'
#input_path = './data/'

def pandas2json(date):
    df = pd.read_csv('{}/{}.csv'.format(input_path,date), lineterminator='\n')
    df = df.drop(columns=['Unnamed: 0', 'location', 'retweetcount', 'hashtags'])
    json_object = df.to_json(orient='split')
    return json_object

app = FastAPI()

@app.get('/snapshot')
async def get_snapshot(date: str = default_date):
    jsonobj = pandas2json(date)
    return jsonobj

# how to run: uvicorn main:app --reload
