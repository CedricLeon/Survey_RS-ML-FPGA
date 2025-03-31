#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import pickle
import re
from pathlib import Path

with open('../data/Dataframes/all_articles_2025-03-07_12-43-59.pkl','rb') as f:
    raw_data = pickle.load(f)

with open('../data/Dataframes/all_datapoints.pkl','rb') as f:
    data = pickle.load(f)
### Table
# Memory, Implementation, Task, Footprint, Utilization

impl_tags = {
        "HDL":      ['RTL design (Verilog)', 'RTL design (VHDL)' , 'RTL design (N/A)'],
        "HLS":      ['HLS (N/A)','HLS (Vitis)', 'HLS (Vivado)'],
        "FINN" :    ['FINN'],
        "Vitis AI": ['Vitis AI (v1.4)','Vitis AI (v1.4)','Vitis AI (DNNDK)','Vitis AI (v2.5)','Vitis AI (N/A)'],
        "MATLAB":   ['HLS (MATLAB)','RTL design (XSG)'],
        "VGT":      ['HLS (VGT)'],
        "-":        ['N/A'],
        }

def findN(str_in,key):
    res = re.search(r'\d+%\s*' + key,str_in)
    if(res == None):
        return "-"
    else:
        r = res.group().split("%")[0]
        return r


## Get the average utilization for DSP,BRAM & freq
## Nums,Total,Min,Max
stats = np.zeros([2,2,4])

stats[0][0][2] = 101
stats[0][1][2] = 101
stats[1][0][2] = 101
stats[1][1][2] = 101


for index, row in data.iterrows():
    i = 0
    if(row["Implementation"] in impl_tags["HDL"]):
        i = 0
    elif(row["Implementation"] in impl_tags["HLS"]):
        i = 1
    else:
        continue

    t = row["FPGA Util"]
    stat = [None,None]
    stat[0] = findN(t,"DSP")
    stat[1] = findN(t,"BRAM")
    for j in range(2):
        if(stat[j] != '-'):
            v = float(stat[j])
            stats[i][j][0] += 1
            stats[i][j][1] += v
            stats[i][j][2] = min(v,stats[i][j][2])
            stats[i][j][3] = max(v,stats[i][j][3])

# Get ze average
for i in range(2):
    for j in range(2):
        stats[i][j][1] = stats[i][j][1]/stats[i][j][0]
print("FPGA Avg Utilization (N,Avg,Min,Max)")
print("HDL")
print(stats[0])
print("HLS")
print(stats[0])



