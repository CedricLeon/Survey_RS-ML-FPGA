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

design_tags = {
        'S':   ['Model Specific (All layers on FPGA)','Algorithm Specific','Model Specific'],
        'F':   ['Various Kernels','Library'],
        '-':  ['???','','N/A'],
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



em_tags = {
    "CNN": ['CNN','YOLOv4','LeNet-5','AlexNet','YOLOv2', 'SSD','YOLOv3','YOLOv4-tiny'],
    "Trad. ML": ['Fuzzy ARTMAP','RBM','MLP','ML', 'WNS' ],
    "GNN": ['GNN']
    }


num_cnn = data.loc[(data["Implementation"].isin(impl_tags["HDL"]) | (data["Implementation"].isin(impl_tags["HLS"]) ))
        & data["Equivalent model"].isin(em_tags["CNN"])].shape[0]

total_manual = data.loc[(data["Implementation"].isin(impl_tags["HDL"]) )| (data["Implementation"].isin(impl_tags["HLS"]) )].shape[0]
print(f"Num CNNs: {num_cnn} ({num_cnn/total_manual})")



#### Measure the average memory of off-chip vs on-chip
# Add various kernels to all Vitis AI stuff
df = data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])]
df["Design"] = df["Design"].replace('',"Various Kernels")
data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])] = df

df = data.loc[data["Implementation"].isin(impl_tags["FINN"])]
df["Design"] = df["Design"].replace('N/A',"Model Specific")
data.loc[data["Implementation"].isin(impl_tags["FINN"])] = df

df = data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])]
df["Memory"] = df["Memory"].replace('',"Off-chip")
data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])] = df

design_tags = {
        'S':   ['Model Specific (All layers on FPGA)','Algorithm Specific','Model Specific'],
        'F':   ['Various Kernels','Library'],
        '-':  ['???','','N/A'],
        }

# Number of F with off-chip

flex_total =data.loc[(data["Design"].isin(design_tags["F"]))].shape[0]
flex_off=   data.loc[(data["Design"].isin(design_tags["F"])) & (data["Memory"] ==  "Off-chip")].shape[0]

spec_total =data.loc[(data["Design"].isin(design_tags["S"]))].shape[0]
spec_off=   data.loc[(data["Design"].isin(design_tags["S"])) & (data["Memory"] ==  "Off-chip")].shape[0]

print(f"Number Flexible {(flex_total)}: Avg: {(flex_off)/(flex_total)}")
print(f"Number Specific {(spec_total)}: Avg: {(spec_off)/(spec_total)}")



off_chip =  data.loc[(data["Memory"] == "Off-chip") & (data["Footprint"] != "")]["Footprint"].to_list()
on_chip =  data.loc[(data["Memory"] == "On-chip")  & (data["Footprint"] != "")]["Footprint"].to_list()



off_chip = [float(x.split(" ")[0]) for x in off_chip]
on_chip = [float(x.split(" ")[0]) for x in on_chip]


print(f"Number Off-chip {len(off_chip)}: Avg: {sum(off_chip)/len(off_chip)}MB")
print(f"Number On-chip {len(on_chip)}: Avg: {sum(on_chip)/len(on_chip)}MB")

# Get stuff that report both power and computiotanal througput

comp_vals = data.loc[(data["Power consumption"] != "") & (data["Throughput"] != "")]["Throughput"].to_list()
comp_vals = [float(x.split(" ")[0]) for x in comp_vals]

power_vals = data.loc[(data["Power consumption"] != "") & (data["Throughput"] != "")]["Power consumption"].to_list()
power_vals = [float(x.split(" ")[0]) for x in power_vals]

print(comp_vals)
print(power_vals)



