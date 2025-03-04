#!/usr/bin/python3
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
import numpy as np
import pickle
import re
import math
from pathlib import Path

import sys
sys.path.insert(0,'../notebooks/')

from fpga_part_info import *
import pandas as pd


pickleName = "all_datapoints.pkl"
datapointsDfPath = "../data/Dataframes/" + pickleName
datapointsDf = pd.read_pickle(datapointsDfPath)


### Copy this stuff over!


# Cylcone 5, Kintex US rad hard , Zynq 7000, Kintex US (KU040) , Z-7
unreportedFPGAS = ["5CSEMA5F31C6", "XQRKU060" , "Z7020","XCKU040","Z7020"]

def get_part(board_str):
    tag =  board_str.split("(")[0]
    board = board_str.split("{")[1].split("}")[0]
    part = board_str.split("(")[1].split(")")[0]
    if(board.endswith("KV260")):
        part = "XCK26"
    return part,board


parts_info = {}
## Loop through papers



def add_part(parts,p):
    if(p in parts.keys()):
            parts[p]["quantity"] += 1
    else:
        parts[p] = {}
        parts[p]["quantity"] = 1
        parts[p]["year"] = fpga_part_info[p][0]
        parts[p]["DSP"] =  fpga_part_info[p][1]
        parts[p]["family"] =fpga_part_info[p][2]

for k in datapointsDf["BBT Citation Key"].unique():
    df = datapointsDf[datapointsDf["BBT Citation Key"] == k]
    for board in df["Board"].unique():
        p,b = get_part(board)
        add_part(parts_info,p)

for p in unreportedFPGAS:
    add_part(parts_info,p)


parts_info = {k: v for k, v in sorted(parts_info.items(), key=lambda item: item[1]["quantity"],reverse=True)}


plt.rcParams.update({'font.size': 40})
fig,ax = plt.subplots(1,1,layout="constrained")

circles = {}
labels = {}


fcolors = {
        "Spartan":  "k",
        "Artix":    "r",
        "Kintex":   "m",
        "Zynq":     "b",
        "Kria":     "darkblue",
        "Virtex":   "tab:orange",
        "Alveo":    "darkorange",
        "Cyclone":  "olive"
        }

pts = {}

for k,v in parts_info.items():
    x = v["year"]
    y = np.log2(v["DSP"] )
    r = v["quantity"]*3000
    pts[k] = (ax.scatter(x,y,r,ec="gray",lw=4,c=fcolors[v["family"]]))


for k,v in parts_info.items():
    x = v["year"]
    y = np.log2(v["DSP"])
    xt = x - 2
    yt = y + 0.6
    ha = "left"
    col = fcolors[v["family"]]
    if(k == "XC3SD1800A"):
        xt = x
        yt = y + 1
        ha = "center"
    if(k == "XC7A200T"):
        xt = x + 0.5
        yt = y - 0.5
        # ha = "center"
    if(k == "5CSEMA5F31C6" or k == "Z7045"):
        xt = x + 1
        yt = y
        ha = "left"
    lab = k + "(" + str(v["quantity"]) + ")"
    labels[k] =  ax.annotate(lab, xy=(x,y),xytext=(xt,yt),fontsize=20,ha=ha,
            arrowprops=dict(facecolor=col, shrink=0.05),backgroundcolor="w")


handles = []
for k,v in fcolors.items():
    handles.append(plt.Line2D([0], [0], color=v, linewidth=0, linestyle='-',label=k,marker="o",markersize=40))


fig.legend(title="FPGA Type",handles=handles,loc='lower right',ncols=2,framealpha=1,bbox_to_anchor=(1.0,0.14),
    labelspacing=0.4,borderpad=0.3,handleheight=0.8,columnspacing=0.8)

yt = [str(2**f) for f in range(6,14)]
ax.set_yticks(range(6,14),yt)

xt = np.arange(2006,2022,2)
ax.set_xticks(xt,xt)

ax.set_xlim(2005,2022)
ax.set_ylim(6,14)
ax.set_ylabel("#DSP")
ax.set_xlabel("Release [Year]")


plt.show()
