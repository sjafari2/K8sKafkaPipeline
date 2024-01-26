import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-snapshot', required=True) 
parser.add_argument('-request_path', '--request_path', type=str, dest='request_path', help='Request Path',metavar='REQUESTPATH')
args = parser.parse_args()
snapshot = args.snapshot
rq_path = args.request_path
request = requests.get(f"rq_path+snapshot?date={snapshot}")
print(request.json())

# how to run: python3 request.py -snapshot 2022-8-22-00
