#!/usr/bin/python3
import numpy as np
import pickle
import re

with open("../data/Dataframes/all_articles_2025-06-01_12-33-03.pkl", "rb") as f:
    raw_data = pickle.load(f)

with open("../data/Dataframes/all_datapoints.pkl", "rb") as f:
    data = pickle.load(f)
### Table
# Memory, Implementation, Task, Footprint, Utilization

impl_tags = {
    "HDL": ["RTL design (Verilog)", "RTL design (VHDL)", "RTL design (N/A)"],
    "HLS": ["HLS (N/A)", "HLS (Vitis)", "HLS (Vivado)"],
    "FINN": ["FINN"],
    "Vitis AI": [
        "Vitis AI (v1.4)",
        "Vitis AI (v1.4)",
        "Vitis AI (DNNDK)",
        "Vitis AI (v2.5)",
        "Vitis AI (N/A)",
    ],
    "MATLAB": ["HLS (MATLAB)", "RTL design (XSG)"],
    "VGT": ["HLS (VGT)"],
    "-": ["N/A"],
}

design_tags = {
    "S": [
        "Model Specific (All layers on FPGA)",
        "Algorithm Specific",
        "Model Specific",
    ],
    "F": ["Various Kernels", "Library"],
    "-": ["???", "", "N/A"],
}


def findN(str_in, key):
    res = re.search(r"\d+%\s*" + key, str_in)
    if res == None:
        return "-"
    else:
        r = res.group().split("%")[0]
        return r


## Get the average utilization for DSP,BRAM & freq
## Nums,Total,Min,Max
stats = np.zeros([2, 2, 4])

stats[0][0][2] = 101
stats[0][1][2] = 101
stats[1][0][2] = 101
stats[1][1][2] = 101


for index, row in data.iterrows():
    i = 0
    if row["Implementation"] in impl_tags["HDL"]:
        i = 0
    elif row["Implementation"] in impl_tags["HLS"]:
        i = 1
    else:
        continue

    t = row["FPGA Util"]
    stat = [None, None]
    stat[0] = findN(t, "DSP")
    stat[1] = findN(t, "BRAM")
    for j in range(2):
        if stat[j] != "-":
            v = float(stat[j])
            stats[i][j][0] += 1
            stats[i][j][1] += v
            stats[i][j][2] = min(v, stats[i][j][2])
            stats[i][j][3] = max(v, stats[i][j][3])

# Get ze average
for i in range(2):
    for j in range(2):
        stats[i][j][1] = stats[i][j][1] / stats[i][j][0]
print("FPGA Avg Utilization (N,Avg,Min,Max)")
print("HDL")
print(stats[0])
print("HLS")
print(stats[0])


em_tags = {
    "CNN": [
        "CNN",
        "YOLOv4",
        "LeNet-5",
        "AlexNet",
        "YOLOv2",
        "SSD",
        "YOLOv3",
        "YOLOv4-tiny",
    ],
    "Trad. ML": ["Fuzzy ARTMAP", "RBM", "MLP", "ML", "WNS"],
    "GNN": ["GNN"],
}


num_cnn = data.loc[
    (
        data["Implementation"].isin(impl_tags["HDL"])
        | (data["Implementation"].isin(impl_tags["HLS"]))
    )
    & data["Equivalent model"].isin(em_tags["CNN"])
].shape[0]

total_manual = data.loc[
    (data["Implementation"].isin(impl_tags["HDL"]))
    | (data["Implementation"].isin(impl_tags["HLS"]))
].shape[0]
print(f"Num CNNs: {num_cnn} CNNs percentage of manual implementations({num_cnn / total_manual})")


#### Measure the average memory of off-chip vs on-chip
# Add various kernels to all Vitis AI stuff
df = data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])]
df["Design"] = df["Design"].replace("", "Various Kernels")
data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])] = df

df = data.loc[data["Implementation"].isin(impl_tags["FINN"])]
df["Design"] = df["Design"].replace("N/A", "Model Specific")
data.loc[data["Implementation"].isin(impl_tags["FINN"])] = df

df = data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])]
df["Memory"] = df["Memory"].replace("", "Off-chip")
data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])] = df

design_tags = {
    "S": [
        "Model Specific (All layers on FPGA)",
        "Algorithm Specific",
        "Model Specific",
    ],
    "F": ["Various Kernels", "Library"],
    "-": ["???", "", "N/A"],
}

# Number of F with off-chip

flex_total = data.loc[(data["Design"].isin(design_tags["F"]))].shape[0]
flex_off = data.loc[
    (data["Design"].isin(design_tags["F"])) & (data["Memory"] == "Off-chip")
].shape[0]

spec_total = data.loc[(data["Design"].isin(design_tags["S"]))].shape[0]
spec_off = data.loc[
    (data["Design"].isin(design_tags["S"])) & (data["Memory"] == "Off-chip")
].shape[0]

print(f"Number Flexible {(flex_total)}: Avg Off-Chip: {(flex_off) / (flex_total)}")
print(f"Number Specific {(spec_total)}: Avg Off-Chip: {(spec_off) / (spec_total)}")


off_chip = data.loc[(data["Memory"] == "Off-chip") & (data["Footprint"] != "")][
    "Footprint"
].to_list()
on_chip = data.loc[(data["Memory"] == "On-chip") & (data["Footprint"] != "")][
    "Footprint"
].to_list()


off_chip = [float(x.split(" ")[0]) for x in off_chip]
on_chip = [float(x.split(" ")[0]) for x in on_chip]


print(f"Number Off-chip {len(off_chip)}: Avg Memory Footprint: {sum(off_chip) / len(off_chip)} MB")
print(f"Number On-chip {len(on_chip)}: Avg Memory Footprint: {sum(on_chip) / len(on_chip)} MB")



## Get precision metrics
fixed_tags = {
    "i4": ["(CloudSatNet-1 Q4) Fixed (4)", "Fixed (4)"],
    "i8": ["Fixed (8)"],
    "i8,f32": ["Mixed (Fixed 8 and Float 32)", "Mixed (Fixed 4 and Float 32)"],
    "i16": ["Fixed (16)"],
    "i32": ["Fixed (32)"],
    "i8,i32": ["Mixed width (Fixed 32 and 8)"],
    "f32": ["Float (32)", "float"],
    "-": ["N/A"],
    "b": ["Binary"],
    "i?": ["Mixed width (Fixed)", "Mixed width (MPQAT)", "Mixed (Fixed)"],
    "i(mix)": ["Mixed (Fixed (1 to 24) weights (3) act)"],
    "f32*": ["Original"],
    "???": ["???"],
}

i8_vals = data.loc[
    data["Precision"].isin(fixed_tags["i8"])
    | data["Precision"].isin(fixed_tags["i8,i32"])
    | data["Precision"].isin(fixed_tags["i8,f32"])
].shape[0]
manual = data.loc[
    (data["Implementation"].isin(impl_tags["HDL"]))
    | (data["Implementation"].isin(impl_tags["HLS"]))
]
i8_man_vals = manual.loc[
    data["Precision"].isin(fixed_tags["i8"])
    | data["Precision"].isin(fixed_tags["i8,i32"])
    | data["Precision"].isin(fixed_tags["i8,f32"])
].shape[0]

num_total = data.shape[0]

print(f"Percentage of int8: {i8_vals / float(num_total)}")
print(f"Percentage of int8 in manual designs: {i8_man_vals / float(total_manual)}")


pc = data.loc[data["Power consumption"] != ""]
print(f"Percentage of experiments reporting power: {(pc.shape[0]*100)/num_total}")


