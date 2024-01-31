import requests
import argparse
import pandas as pd
import time
from datetime import datetime
from datetime import date, timedelta
import sys
import numpy as np
# how to run: python3 request_extended.py -start 2022-8-01-00 -end 2022-8-01-05 -window hour -wait 10
    

parser = argparse.ArgumentParser()
parser.add_argument('-podcount',type = int , required=True)
parser.add_argument('-prodcount',type = int, required=True)
parser.add_argument('-totalprod', type = int, required=True)
parser.add_argument('-ipath', required=True)
parser.add_argument('-opath', required=True)
parser.add_argument('-start', required=True) 
parser.add_argument('-end', required=True)
parser.add_argument('-window', required=True)
parser.add_argument('-wait', type = int, required=True)

args = parser.parse_args()
pod_count = args.podcount
prod_count = args.prodcount
total_producer = args.totalprod
input_path = args.ipath
output_path = args.opath
start_time = args.start
end_time = args.end
window = args.window
wait = args.wait

# -start 2022-8-01-00 -end 2022-8-02-00 -window hour
# -start 2022-8-01-00 -end 2022-8-05-00 -window day

# start time
# start_time = '2022-8-01-00'
# end_time = '2022-8-02-00'

# print('start_time: {}'.format(start_time))
# print('end_time: {}'.format(end_time)) 

start_time = start_time.replace('-', ':')
end_time = end_time.replace('-', ':')

print('start_time: {}'.format(start_time))
print('end_time: {}'.format(end_time)) 

# convert time string to datetime
t1 = datetime.strptime(start_time, "%Y:%M:%d:%H")
# print('Start time:', t1.time())

t2 = datetime.strptime(end_time, "%Y:%M:%d:%H")
# print('End time:', t2.time())

# get difference
delta = t2 - t1

# get difference in hours
sec = delta.total_seconds()
hours = int(sec / (60 * 60))

days = delta.days

# -------------------------------------------------------------------
# if less than 2 days requested (e.g., 1 or a few hours)
if days < 2: 

    if window == 'hour':
        print('number of hours requested: {}'.format(hours))
        # print('processing {} hour snapshots \n'.format(hours))
        num_snapshots = hours

    if window == 'day':
        print('number of days requested: {}'.format(days))
        # print('processing {} day snapshots \n'.format(days))
        num_snapshots = days

    for snapshot in range (0, num_snapshots):

        if snapshot < 10:
            date = '-'.join(start_time.split(':')[0:-1])
            date = date + '-0{}'.format(snapshot)
        else:
            date = date + '-{}'.format(snapshot)

        print('requesting snapshot {}'.format(date))   

        jsonobj = requests.get('http://127.0.0.1:8000/snapshot?date={}'.format(date))
       # print(f"Json object is {jsonobj.json()}")
        df = pd.read_json(jsonobj.json(), orient='split')

        list_df = np.array_split(df,total_producer)
        k = 0
        for i in range(0,pod_count):
            for j in range(0,prod_count):
                list_df[k].to_csv(f"{output_path}/{date}-pod-{i}-prod-{j}.csv", index=False)
                k = k+1

        print('{} snapshot received and saved'.format(date))
        
        for i in range(0, wait):
            sys.stdout.write(str(i)+' ')
            sys.stdout.flush()
            time.sleep(1)

        print('moving on to next snapshot \n')    

# -------------------------------------------------------------------
# more than 1 day is being requested
# can only request complete days (from 00 to 00)
else:
    days = []
    for i in range(delta.days + 1):
        day = str(start_date + timedelta(days=i))
        days.append(day)
    num_snapshots = 24
    for day in days:
        
        for snapshot in range (0, num_snapshots):

            if snapshot < 10:
                day = '-'.join(day.split(':')[0:-1])
                day = day + '-0{}'.format(snapshot)
            else:
                day = day

            print('requesting snapshot {}'.format(day))   

            jsonobj = requests.get('http://127.0.0.1:8000/snapshot?date={}'.format(day))

            # print(jsonobj.json())

            df = pd.read_json(jsonobj.json(), orient='split')
            list_df = np.array_split(df,total_producer)
            k = 0
            for i in range(0,pod_count):
                for j in range(0,prod_count):
                    list_df[k].to_csv(f"{output_path}/{date}-pod-{i}-prod-{j}.csv", index=False)
                    k = k+1


            print('{} snapshot received and saved as csv file'.format(day))
            print('sleeping for {} seconds'.format(wait))
            time.sleep(wait)

            print('sleeping is over, continue to next snapshot \n')
