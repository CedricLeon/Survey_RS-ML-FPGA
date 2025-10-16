#!/usr/bin/python3
import numpy as np
import pickle
import re
import matplotlib.pyplot as plt
from utils.metadata import *

with open("../data/Dataframes/all_articles_2025-06-01_12-33-03.pkl", "rb") as f:
    raw_data = pickle.load(f)

with open("../data/Dataframes/all_datapoints.pkl", "rb") as f:
    data = pickle.load(f)


# print(data.columns)
# print(data["Precision"].unique())
# print(data["Publication year"].unique())
#
# prec_dict = {
#         "float": ["Original","Float (32)",],
#         "mixed": ["Mixed (Fixed (1 to 24) weights (3) act)","Mixed width (Fixed 32 and 8)","Mixed (Fixed 8 and Float 32)",
#             'Mixed (Fixed)','Mixed (Fixed 4 and Float 32)' ,'Mixed width (MPQAT)'],
#         "fixed8":["Fixed (8)"],
#         "fixed16":["Fixed (16)"],
#         "fixed32":["Fixed (32)"],
#         "fixed4":["Fixed (4)"],
#         'bin':["Binary"],
#         "N/A":["N/A"]
#         }
# kk=(data["Publication year"].unique())
# kk.sort()
# print(kk)
#
# val_dict = {}
# for k,v in prec_dict.items():
#     nums =[]
#     for y in kk:
#         num=data.loc[(data["Publication year"] ==y) & (data["Precision"].isin(v))].shape[0]
#         nums.append(num)
#     val_dict[k]=nums
# print(val_dict)


def get_part(board_str):
    tag =  board_str.split("(")[0]
    board = board_str.split("{")[1].split("}")[0]
    part = board_str.split("(")[1].split(")")[0]
    if(board.endswith("KV260")):
        part = "XCK26"
    return part

def get_num(part):
    return fpga_part_info[part][1]

def findN(str_in, key):
    res = re.search(r"\d+%\s*" + key, str_in)
    if res == None:
        return "-"
    else:
        r = res.group().split("%")[0]
        return float(r)

def get_bram_util(t):
    return findN(t, "BRAM")

def get_dsp_util(t):
    return findN(t, "DSP")

def get_max_util(t):
    dd = findN(t,"DSP")
    bb = findN(t,"BRAM")
    if(dd == "-"):
        return bb
    if(bb == "-"):
        return dd
    return max(dd,bb)

def get_first(t):
    v = t.split(" ")[0]
    try:
        return float(v)
    except:
        return "-"


data["Board"] = data["Board"].apply(get_part)
data["dsp"] = data["Board"].apply(get_num)
data["dsp_util"] = data["FPGA Util"].apply(get_bram_util)
data["bram_util"] = data["FPGA Util"].apply(get_dsp_util)
data["max_util"] = data["FPGA Util"].apply(get_max_util)
data["Power consumption"] = data["Power consumption"].apply(get_first)
data["Throughput"] = data["Throughput"].apply(get_first)
data["Footprint"] = data["Footprint"].apply(get_first)



def replace_comp(val):
    if val == "" or val == "O(n) OP":
        return 0
    val = val.split(" ")[0]
    fac = val[-1]
    v = float(val[:-1])
    if fac == 'K':
        ret = v*1024
    elif fac == 'M':
        ret = v*1024*1024
    elif fac == 'G':
        ret = v*1024*1024*1024
    else:
        ret = 0
    return ret

data["Complexity"]= (data["Complexity"].apply(replace_comp))

print(data["Complexity"].unique())

def get_data_points(data,xkey,ykey,ignore):
    unique_x = sorted(data[xkey].unique())
    out_data = {
            "x" : [],
            "avg" : [],
            "min" : [],
            "max" : [],
            "num" : []
            }
    for x in unique_x:
        print(x)
        d = data.loc[data[xkey] == x]
        avg = 0.0
        minv = 100000000.0
        maxv = 0.0
        num = 0
        for v in d[ykey]:
            if(v != ignore):
                num+=1
                avg+= float(v)
                minv = min(minv,float(v))
                maxv = max(maxv,float(v))
        if(num > 0):
            avg = avg/num
            out_data["x"].append(x)
            out_data["avg"].append(avg)
            out_data["min"].append(minv)
            out_data["max"].append(maxv)
            out_data["num"].append(num)
    return out_data


def best_fit(X_in,Y_in,log2=True):
    Y = np.array(Y_in)
    if(log2):
        X = np.log2(np.array(X_in))
    else:
        X = np.array(X_in)
    xbar = sum(X)/len(X)
    ybar = sum(Y)/len(Y)
    n = len(X) # or len(Y)
    numer = sum([xi*yi for xi,yi in zip(X, Y)]) - n * xbar * ybar
    denum = sum([xi**2 for xi in X]) - n * xbar**2

    b = numer / denum
    a = ybar - b * xbar

    first,last = X.min(),X.max()
    
    x,y = [first,last],[a + b*first,a + b*last]

    return x,y


def scatter_fit(ax,data,key,ignore,index="dsp"):
    df =data[data[key] != ignore]
    dd = np.array(df[index])
    x,y = best_fit(df[index],df[key])
    xt = np.array(df[index].unique())

    sz = np.ones(len(df[key]))*60
    ax.plot(x,y,color='k',lw=3)
    ax.scatter(np.log2(dd),df[key],sizes=sz)#,color='orange',marker="d")
    # ax.set_xticks(np.log2(xt),xt,rotation=90,fontsize=20)
    xt = np.array([6+i for i in range(0,8)])
    ax.set_xticks(xt,2**xt,fontsize=20,rotation=90)



plt.rcParams.update({'font.size': 20})

fig,ax = plt.subplots(1,4,layout="constrained")#,sharex=True)
# scatter_fit(ax[0],data,"dsp_util","-")
# scatter_fit(ax[0],data,"bram_util","-")
scatter_fit(ax[0],data,"max_util","-")
scatter_fit(ax[1],data,"Power consumption","-")
scatter_fit(ax[2],data,"Throughput","-")
scatter_fit(ax[3],data,"Footprint","-")

ax[2].set_yscale('symlog')
ax[3].set_yscale('symlog')
ax[0].set_ylim(0,100)
ax[2].set_ylim(0)
ax[3].set_ylim(0)

ax[0].set_ylabel("Max BRAM/DSP Util. [%]")
ax[1].set_ylabel("Power [W]")
ax[2].set_ylabel("Throughput [GOP/s]")
ax[3].set_ylabel("Footprint MB")
fig.supxlabel("Number of DSPs")

# print(data[data["dsp"] != 12288])
xt = np.array(data[data["dsp"] != 12288]["dsp"].unique())
# ax[1][0].set_xticks(np.log2(xt),xt,rotation=90,fontsize=20)
plt.show()

quit()


