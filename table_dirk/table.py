#!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import pickle
import re
from pathlib import Path

# Check if the tags is a array if one of the keys is there otherwise
# Print the last dictionary entry
def check_array(tags,tdict):
    name = []
    for k,ids in tdict.items():
        for v in ids:
            if(v in list(tags)[0]):
                name.append(k)
    if(name == []):
        return list(tdict)[-1]
    else:
        return ",".join(name)


class TexNode:
    def __init__(self,name,df,columns,i,sdepth):
        self.name       = name
        self.max_depth  = len(columns)
        self.nodes      = []
        self.depth      = i
        self.len        = df.shape[0]

        if(i > 0):
            self.hook   = columns[i-1].hook
            self.cwidth = columns[i-1].cwidth

        if(i < len(columns)):
            self.column = columns[i]
            self.final = False
            if(self.column.array):
                for j in range(len(df)):
                    r = df.iloc[[j]]
                    name = check_array(r[self.column.df_key],self.column.tags)
                    self.nodes.append(TexNode(name,r,columns,i+1,3))
            else:
                a = 0
                for k,v in self.column.tags.items():
                    rows = df.loc[df[self.column.df_key].isin(v)]
                    if(len(rows) == 0):
                        continue
                    if(self.depth >= sdepth):
                        for j in range(len(rows)):
                            self.nodes.append(TexNode(k,rows.iloc[[j]],columns,i+1,3))
                    else:
                        self.nodes.append(TexNode(k,rows,columns,i+1,3))
                    a += len(rows)
                if(a != self.len):
                    print("ERROR not all rows classified " + self.column.df_key)
                    print(f"Total rows {self.len} used {a}")
                    print(df[self.column.df_key])
                    for tar in df[self.column.df_key].unique():
                        found = 0
                        for k,v in self.column.tags.items(): 
                            if(tar in v):
                                found = 1
                                break
                        if(found == 0):
                            print("Missed key " + tar)
        else:
            self.column = None
            self.final = True






    def render(self,text_in,first,last,max_depth):
        text = text_in

        if(first):
            text += "".join([ "    " for x in range(self.depth - 2)])
        else:
            text += "".join([ "   &" for x in range(self.depth - 2)])
        if(self.depth > 1):
            text += "   &"
        if(self.name == ''):
            self.name = '-'

        if(self.hook == None):
            text += f"\\multirow{{{self.len}}}{{*}}{{{self.name}}}"
        else:
            text += f"\\multirow{{{self.len}}}{{*}}{{{self.hook(self.name)}}}"
        if(self.final):
            text += "\\\\\n"
            for i in range(self.len - 1):
                text += "".join([ "   &" for x in range(self.depth - 1)]) + "\\\\\n"
        else:
            text += "\n"
            for n in self.nodes:
                text = n.render(text,(n == self.nodes[0]),(n == self.nodes[-1]),max_depth)
        if(self.depth <= max_depth):
            if(not(last)):
                text += f"\cmidrule{{{self.depth}-{self.max_depth}}}\n"

        return text



class TexTable:
    def __init__(self,df,columns):
        self.data = df
        self.columns = columns
        self.start = TexNode("Start",df,columns,0,3)

    def render(self,text_in,max_depth):
        self.text = text_in
        self.text += self.header()
        for n in self.start.nodes:
            self.text = n.render(self.text,(n == self.start.nodes[0]),(n == self.start.nodes[-1]),max_depth)
        self.text += "\\bottomrule \n"
        self.text += "\\end{tabular}\n\\end{adjustbox}\n\\end{table}"
        # self.text += "\\end{tabular}\n\n"
        self.text += """
\\small
"""
        return self.text

    def header(self):
        text ="\\begin{table}\n\\centering\n"
        text+="""
\\caption{FPGA Optimization Table}
\\begin{adjustbox}{totalheight=\\textheight-2\\baselineskip}
"""
        text+="\\begin{tabular}{"
        # text ="\\centering\n\\begin{tabular}{"
        # # text += "".join([f"p{{{c.cwidth}}}" for c in self.columns])
        text += "".join([f"c" for c in self.columns])
        text += "}\n"
        for c in self.columns:
            text += "\\textbf{" +  c.name  + "}"
            if(c != self.columns[-1]):
                text += " &"
        text += "\\\\\n \\toprule \n"
        return text



class TexColumn:
    def __init__(self,df_key : str,tags : dict ,name : str, cwidth : str = "4em", array = False, hook = None):
        self.df_key = df_key
        self.tags = tags
        self.name = name
        self.cwidth = cwidth
        self.hook = hook
        self.array = array




with open('../data/Review_Ml-RS-FPGA/Dataframes/all_articles_2025-01-03_13-21-13.pkl','rb') as f:
    raw_data = pickle.load(f)

with open('../data/Review_Ml-RS-FPGA/Dataframes/all_datapoints.pkl','rb') as f:
    data = pickle.load(f)







### Table
# Memory, Implementation, Task, Footprint, Utilization
mem_tags = {
        "On":          ['On-chip'],
        "Off":         ['Off-chip','Off-chip (HBM)'],
        "tbd.":             ['???','','N/A']
        }


impl_tags = {
        "RTL":      ['RTL design (Verilog)', 'RTL design (XSG)','RTL design (VHDL)' , 'RTL design (N/A)'],
        "HLS":      ['HLS (N/A)','HLS (Vitis)', 'HLS (Vivado)','HLS (VGT)'],
        "N/A":      ['N/A'],
        "FINN" :    ['FINN'],
        "MATLAB":   ['HLS (MATLAB)'],
        "Vitis AI": ['Vitis AI (v1.4)','Vitis AI (v1.4)','Vitis AI (DNNDK)','Vitis AI (v2.5)','Vitis AI (N/A)'],
        }

task_tags = {
        'Class': ['Classification'],
        'PClass': ['Pixel classification'],
        'Obj': ['Object detection'],
        'Reg': ['Regression'],
        'Seg': ['Segmentation']
        }

design_tags = {
        'MS':   ['Model Specific (All layers on FPGA)','Algorithm Specific','Model Specific'],
        'VK':   ['Various Kernels'],
        'N/A':  ['???','','N/A'],
        'LIB':  ['Library']
        }



def optimTag(df,name):
    v = 0
    col = df["Optimizations"]
    for a in col:
        if((name in a)):
            v = 1
            break
    if(v == 0):
        print(f"ERROR: {name} not in!")
        print(col)
        return {}

    not_name = [] 
    for x in col:
        if(x != name):
            not_name.append(x)
    rd = {
            "{\color{green} \\checkmark}"   : [name],
            "{\color{red} X}"   : []
        }
    return rd

special_ops = {
        "HWP": ["HW aware pruning"],
        "DD": ["DSP double rate (like DPU)"],
        "AD": ["Advanced Dataflow"],
        "MP": ["Multiple PEs"],
        "-": []
        }



util_tags = {
        "-" : ["???","N/A",""],
        "TS"  : ["41% (total slices)"]
        }

def findN(str_in):
    res = re.search(r'\d+.*DSP',str_in)
    if(res == None):
        return "-"
    else:
        r = res.group().split("%")[0]
        return r


for t in sorted(data["FPGA Util"].unique()):
    s = findN(t)
    if(s in util_tags.keys()):
        util_tags[s].append(t)
    else:
        util_tags[s] = [t]

    # if(t.endswith("LUT)")):
    #     s = findN(t) 
    #     util_tags["{\color{red}L:" + s + "}"] = [t]
    # elif(t.endswith("rest)")):
    #     s = findN(t) 
    #     util_tags["{\color{cyan}R:" + s + "}"] = [t]
    # elif(t.startswith("Low")):
    #     s = findN(t) 
    #     # util_tags["{\color{red}" + s + "}"] = [t]
    #     util_tags[s] = [t]
    # elif(t.startswith("Average")):
    #     s = findN(t)
    #     # util_tags["{\color{orange}" + s + "}"] = [t]
    #     util_tags[s] = [t]
    # elif(t.startswith("High")):
    #     s = findN(t) 
    #     # util_tags["{\color{green}" + s + "}"] = [t]
    #     util_tags[s] = [t]

print(util_tags)


freq_tags = {f.split(" ")[0]: [f]  for f in data["Frequency"].unique()}
compl_task = {f.split(" ")[0]: [f]  for f in data["Complexity"].unique()}
power_tags = {f.split(" ")[0]: [f]  for f in data["Power consumption"].unique()}
cit_tags  = {f"\\cite{{{f}}}": [f]  for f in sorted(data["BBT Citation Key"].unique())}
through_tags  = {f.split(" ")[0]: [f]  for f in sorted(data["Throughput"].unique())}
fp_tags  = {f.split(" ")[0]: [f]  for f in sorted(data["Footprint"].unique())}
lat_tags = {f: [f]  for f in data["Latency"].unique()}


board_tags  = {} 
for f in sorted(data["Board"].unique()):
    tag = f.split("(")[0]

    ss = tag.split(" ")
    ls = tag.split("-")
    k = tag[0]
    if(ss[1] != ''):
        if(ss[1] == "7000"):
            k+= "7"
        else:
            k+= ss[1]
    elif(len(ls)> 1):
        k += ls[1]
    else:
        k = "Alveo"

    board = f.split("{")[1].split("}")[0]
    part = f.split("(")[1].split(")")[0]

    if(len(board) > 0):
        k = k + "(" + board +")"
    else:
        k = k + "(" + part +")"

    if(k in board_tags.keys()):
        board_tags[k].append(f)
    else:
        board_tags[k] = [f]


print(board_tags)


fixed_tags = {
        "i4":       ['(CloudSatNet-1 Q4) Fixed (4)','Fixed (4)'],
        "i8":       ['Fixed (8)'],
        "i8,f32":   ['Mixed (Fixed 8 and Float 32)'],
        "i16":      ['Fixed (16)'],
        "i32":      ['Fixed (32)'],
        "i8,i32":   ['Mixed width (Fixed 32 and 8)'],
        "f32":      ['Float (32)','float'],
        "-":        ['N/A'],
        "bin":      ["Binary"],
        "i?":       ['Mixed width (Fixed)','Mixed width (MPQAT)','Mixed (Fixed)'],
        "i(mix)":  ['Mixed (Fixed (1 to 24) weights (3) act)'],
        "Orig":     ["Original"],
        "???":      ['???']
        }



dpu_util  = {f.split("%")[0]: [f]  for f in sorted(data["DPU Util"].unique())}
dpu_config = {f.split(" ")[0]: [f]  for f in sorted(data["DPU Config"].unique())}
dpu_core = {f.split(" ")[0]: [f]  for f in sorted(data["DPU Core"].unique())}




model_tags = {
        "CNN" : [],
        "YOLO": [],
        "SSD" : [],
        "MLP" : [],
        "GNN" : []
        }

df = raw_data["Tags"]
for j in range(len(df)):
    tags = df.iloc[[j]][0]
    for tag in tags:
        if(tag.startswith("Model:")):
            key =   tag.split("Model: ")[1].split("(")[0].strip()
            t   =   tag.split("Model: ")[1].split("(")[1].split(")")[0]
            if(t == "LeNet-5"):
                t = "CNN"
            if(t == "AlexNet"):
                t = "CNN"
            if(t.startswith("YOLO")):
                t = "YOLO"
            if(t == "Diverse"):
                t = "ML"
            if(t in model_tags.keys()):
                model_tags[t].append(key)
            else:
                model_tags[t] = [key]

# Add various kernels to all Vitis AI stuff
df = data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])]
df["Design"] = df["Design"].replace('',"Various Kernels")
data.loc[data["Implementation"].isin(impl_tags["Vitis AI"])] = df

df = data.loc[data["Implementation"].isin(impl_tags["FINN"])]
df["Design"] = df["Design"].replace('N/A',"Model Specific")
data.loc[data["Implementation"].isin(impl_tags["FINN"])] = df



columns = [
        TexColumn("Implementation",     impl_tags,                      "Impl.","2.5em"),
        TexColumn("Model",              model_tags,                    "Model","2.5em"),
        TexColumn("Design",             design_tags,                    "Design","1.5em"),
        TexColumn("BBT Citation Key",   cit_tags,                       "Ref.","1em"),
        # TexColumn("Task",               task_tags,                      "Task","3em"),
        TexColumn("Board",              board_tags,                     "Board","2.5em"),
        TexColumn("Footprint",          fp_tags,                        "Mem [MB]","2em"),
        TexColumn("Memory",             mem_tags,                       "Mem.","2em"),
        TexColumn("Complexity",         compl_task,                     "Model Compl. [GOPS]","2em"),
        TexColumn("Precision",          fixed_tags,                     "Precision","2em"),
        TexColumn("Frequency",          freq_tags,                      "freq. [MHz]","2em"),
        TexColumn("Throughput",         through_tags,                   "Peak Throughput [GOP/s]","2.5em"),
        TexColumn("Latency",            lat_tags,                       "BW/Lat[FPS/ms]","2.5em"),
        TexColumn("Power consumption",  power_tags,                     "Power[W]","2em"),
        TexColumn("FPGA Util",          util_tags,                      "DSP Util[\%]","1em"),
        # TexColumn("Optimizations",      optimTag(data,"Multiple PEs"),  "MP","1em",True),
        # TexColumn("DPU Config",         dpu_config,                     "DC","1em"),
        # TexColumn("DPU Util",         dpu_util,                     "DU","1em"),
        # TexColumn("DPU Core",         dpu_core,                     "DC2","1em")
        # TexColumn("Optimizations",      special_ops,                    "Optim","2em",True),
        ]


header = """
\\documentclass{article}
\\usepackage{array}
\\usepackage{booktabs}
\\usepackage{multirow}
\\usepackage{pdflscape}
\\usepackage{amssymb}
\\usepackage{adjustbox}
\\usepackage[dvipsnames,table]{xcolor}
\\begin{document}
"""

tab = TexTable(data,columns)
text = tab.render("",3)

footer = "\n\end{document}\n"

Path("./gen").mkdir(parents=True, exist_ok=True)

f = open("gen/table.tex","w")
f.write(header + text + footer)
f.close()

f = open("gen/export.tex","w")
f.write(text)
f.close()




# \multicolumn{5}{c}{\textbf{General}} & \multicolumn{4}{c}{\textbf{Model}} & \multicolumn{5}{c}{\textbf{Peformance \& Util.}} &\multicolumn{3}{c}{Vitis AI} \\
# \cmidrule(lr){1-5}  \cmidrule(lr){6-9} \cmidrule (lr){10-14}
