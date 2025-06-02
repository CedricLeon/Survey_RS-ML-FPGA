"""This file is responsible for generating the FPGA taxonomy (Table 3). It groups different experiments and outputs the latex table."""

#!/usr/bin/python3
import pickle
import re
from pathlib import Path

# Check if the tags is a array if one of the keys is there otherwise print the last dictionary entry
def check_array(tags, tdict):
    name = []
    for k, ids in tdict.items():
        for v in ids:
            if v in list(tags)[0]:
                name.append(k)
    if name == []:
        return list(tdict)[-1]
    else:
        return ",".join(name)


class TexNode:
    def __init__(self, name, df, columns, i, sdepth):
        self.name = name
        self.max_depth = len(columns)
        self.nodes = []
        self.depth = i
        self.len = df.shape[0]

        if i > 0:
            self.hook = columns[i - 1].hook

        if i < len(columns):
            self.column = columns[i]
            self.final = False
            if self.column.array:
                for j in range(len(df)):
                    r = df.iloc[[j]]
                    name = check_array(r[self.column.df_key], self.column.tags)
                    self.nodes.append(TexNode(name, r, columns, i + 1, 3))
            else:
                a = 0
                for k, v in self.column.tags.items():
                    rows = df.loc[df[self.column.df_key].isin(v)]
                    if len(rows) == 0:
                        continue
                    if self.depth >= sdepth:
                        for j in range(len(rows)):
                            self.nodes.append(
                                TexNode(k, rows.iloc[[j]], columns, i + 1, sdepth)
                            )
                    else:
                        self.nodes.append(TexNode(k, rows, columns, i + 1, sdepth))
                    a += len(rows)
                if a != self.len:
                    print("ERROR not all rows classified " + self.column.df_key)
                    print(f"Total rows {self.len} used {a}")
                    print(df[self.column.df_key])
                    for tar in df[self.column.df_key].unique():
                        found = 0
                        for k, v in self.column.tags.items():
                            if tar in v:
                                found = 1
                                break
                        if found == 0:
                            print("Missed key " + tar)
        else:
            self.column = None
            self.final = True

    def render(self, text_in, first, last, max_depth):
        text = text_in

        if first:
            text += "".join(["    " for x in range(self.depth - 2)])
        else:
            text += "".join(["   &" for x in range(self.depth - 2)])
        if self.depth > 1:
            text += "   &"
        if self.name == "":
            self.name = "-"

        if self.hook == None:
            text += f"\\multirow{{{self.len}}}{{*}}{{{self.name}}}"
        else:
            text += f"\\multirow{{{self.len}}}{{*}}{{{self.hook(self.name)}}}"
        if self.final:
            text += "\\\\\n"
            for i in range(self.len - 1):
                text += "".join(["   &" for x in range(self.depth - 1)]) + "\\\\\n"
        else:
            text += "\n"
            for n in self.nodes:
                text = n.render(
                    text, (n == self.nodes[0]), (n == self.nodes[-1]), max_depth
                )
        if self.depth <= max_depth:
            if not (last):
                text += f"\cmidrule{{{self.depth}-{self.max_depth}}}\n"

        return text


class TexTable:
    def __init__(self, df, columns):
        self.data = df
        self.columns = columns
        self.start = TexNode("Start", df, columns, 0, 5)

    def render(self, text_in, max_depth, custom_head=None, custom_foot=None):
        self.text = text_in
        self.text += self.header(custom_head)
        for n in self.start.nodes:
            self.text = n.render(
                self.text,
                (n == self.start.nodes[0]),
                (n == self.start.nodes[-1]),
                max_depth,
            )
        self.text += "\\bottomrule \n"
        self.text += "\\end{tabular}\n"
        if custom_foot:
            self.text += custom_foot + "}\n\\end{table}"
        else:
            "}\n\\end{table}"
        return self.text

    def header(self, custom_head):
        text = "\\begin{table}\n\\centering\n"
        text += """
\\caption{FPGA Optimization Table}
\\label{table:fpga_optim}
"""
        text += "{\\tiny"
        if custom_head == None:
            text += "\\begin{tabular}{"
            text += "".join([f"c" for c in self.columns])
            text += "}\n"
            for c in self.columns:
                text += "\\textbf{" + c.name + "}"
                if c != self.columns[-1]:
                    text += " &"
            text += "\\\\\n \\toprule \n"
        else:
            text += custom_head
        return text


class TexColumn:
    def __init__(
        self,
        df_key: str,
        tags: dict,
        array=False,
        hook=None,
    ):
        self.df_key = df_key
        self.tags = tags
        self.hook = hook
        self.array = array


##### Load Data #####
with open("../data/Dataframes/all_articles_2025-06-01_12-33-03.pkl", "rb") as f:
    raw_data = pickle.load(f)

with open("../data/Dataframes/all_datapoints.pkl", "rb") as f:
    data = pickle.load(f)

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

frame_tags = {"Manual": [], "Automatic": [], "Unclassified": []}

for k, v in impl_tags.items():
    if k == "HDL" or k == "HLS":
        frame_tags["Manual"].extend(v)
    elif k == "-":
        frame_tags["Unclassified"].extend(v)
    else:
        frame_tags["Automatic"].extend(v)

design_tags = {
    "S": [
        "Model Specific (All layers on FPGA)",
        "Algorithm Specific",
        "Model Specific",
    ],
    "F": ["Various Kernels", "Library"],
    "-": ["???", "", "N/A"],
}
util_tags = {"-": ["???", "N/A", ""], "TS": ["41% (total slices)"]}
bram_tags = {"-": ["???", "N/A", ""]}


def findN(str_in, key):
    res = re.search(r"\d+%\s*" + key, str_in)
    if res == None:
        return "-"
    else:
        r = res.group().split("%")[0]
        return r


for t in sorted(data["FPGA Util"].unique()):
    s = findN(t, "DSP")
    l = findN(t, "BRAM")
    if s in util_tags.keys():
        util_tags[s].append(t)
    else:
        util_tags[s] = [t]

    if l in bram_tags.keys():
        bram_tags[l].append(t)
    else:
        bram_tags[l] = [t]


freq_tags = {f.split(" ")[0].split(".")[0]: [f] for f in data["Frequency"].unique()}
cc_tasks = {f.split(" ")[0]: [f] for f in data["Complexity"].unique()}

compl_task = {}
compl_task["-"] = cc_tasks["O(n)"]
compl_task[""] = cc_tasks[""]

del cc_tasks["O(n)"]


rd_compl = {"G": "M", "M": "K", "K": ""}

for k, v in cc_tasks.items():
    if (k == "-") or (k == ""):
        continue
    l = k[-1]
    val = float(k[:-1])
    if val < 1:
        l = rd_compl[l]
        val = val * 1000
    val = "%.2f" % val
    if len(val.split(".")[0]) < 3:
        val = val[:4] + l
    else:
        val = val[:3] + " " + l
    if val in compl_task:
        compl_task[val].extend(v)
    else:
        compl_task[val] = v


power_tags = {f.split(" ")[0]: [f] for f in data["Power consumption"].unique()}
cit_tags = {f"\\cite{{{f}}}": [f] for f in sorted(data["BBT Citation Key"].unique())}
through_tags = {}
for t in sorted(data["Throughput"].unique()):
    if t.split(" ")[0] == "":
        through_tags[""] = [t]
    else:
        v = float(t.split(" ")[0])
        st = "%.1f" % v
        if st[-1] == "0":
            st = st[:-2]

        through_tags[st] = [t]

lat_tags = {f: [f] for f in data["Latency"].unique()}
fps_tags = {f.split(" ")[0]: [f] for f in data["FPS"].unique()}

board_tags = {}
for f in sorted(data["Board"].unique()):
    tag = f.split("(")[0]

    ss = tag.split(" ")
    ls = tag.split("-")
    k = tag[0]
    if ss[1] != "":
        if ss[1] == "7000":
            k += "7"
        else:
            k += ss[1]
    elif len(ls) > 1:
        k += ls[1]
    else:
        k = "Alveo"

    board = f.split("{")[1].split("}")[0]
    part = f.split("(")[1].split(")")[0]

    k = part.split("XC")[-1]


    if k in board_tags.keys():
        board_tags[k].append(f)
    else:
        board_tags[k] = [f]

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

dpu_util = {f.split("%")[0]: [f] for f in sorted(data["DPU Util"].unique())}
dpu_config = {f.split(" ")[0]: [f] for f in sorted(data["DPU Config"].unique())}
dpu_core = {f.split(" ")[0]: [f] for f in sorted(data["DPU Core"].unique())}

model_tags = {"CNN": [], "YOLO": [], "SSD": [], "MLP": [], "GNN": []}

em_tags = {f: [f] for f in sorted(data["Equivalent model"].unique())}
model_tags = {f: [f] for f in sorted(data["Model"].unique())}

model_tags["BRAM\_DSP"] = model_tags.pop("BRAM_DSP")
model_tags["LUT\_MUL"] = model_tags.pop("LUT_MUL")

model_tags["RDBC"] = model_tags.pop("Roller Dung Bettle Clustering")
model_tags["WNS"] = model_tags.pop("Weightless Neural Systems")

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
    "ML": ["Fuzzy ARTMAP", "RBM", "MLP", "ML", "WNS"],
    "GNN": ["GNN"],
}


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


# Calculate Power Efficiency
for i, r in data.iterrows():
    pc = r["Power consumption"].split(" ")[0]
    tp = r["Throughput"].split(" ")[0]
    if (pc != "") and (tp != ""):
        data.loc[i, "Power efficiency"] = "{:.1f}".format(float(tp) / float(pc))
    else:
        data.loc[i, "Power efficiency"] = ""

eff_tags = {x: [x] for x in data["Power efficiency"].unique()}

# Merge footprint and location
mem_tags = {
    "On": ["On-chip"],
    "Off": ["Off-chip", "Off-chip (HBM)"],
    "-": ["N/A"],
}

for index, row in data.iterrows():
    nw = row["Footprint"].split(" ")[0]
    if nw == "":
        nw = "-"
    if row["Memory"] in mem_tags["On"]:
        nw += "\\textsuperscript{\\textbf{\\textdagger}}"
        # \\footnote[2]{text}"
    elif row["Memory"] in mem_tags["Off"]:
        nw += ""
    else:
        nw += "\\textsuperscript{\\textbf{?}}"
    data.loc[index, "Footprint"] = nw

fp_tags = {f: [f] for f in sorted(data["Footprint"].unique())}


def fun(x):
    t = f"\\rotatebox[origin=c]{{90}}{{\\textbf{{{x}}}}}"
    return t


columns = [
    TexColumn("Implementation", frame_tags, hook=fun),
    TexColumn("Implementation", impl_tags),
    TexColumn("Equivalent model", em_tags),
    TexColumn("Design", design_tags),
    TexColumn("BBT Citation Key", cit_tags),
    TexColumn("Board", board_tags),
    TexColumn("Model", model_tags),
    TexColumn("Precision", fixed_tags),
    TexColumn("Complexity", compl_task),
    TexColumn("Footprint", fp_tags),
    TexColumn("FPGA Util", util_tags),
    TexColumn("FPGA Util", bram_tags),
    TexColumn("Frequency", freq_tags),
    TexColumn("Throughput", through_tags),
    TexColumn("Power consumption", power_tags),
    TexColumn("Power efficiency", eff_tags),
    TexColumn("Latency", lat_tags),
    TexColumn("FPS", fps_tags),
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
\\tiny
"""

table_head = """
\\begin{tabular}{cccccccclccccccccc}
 \\multicolumn{7}{c}{\\textbf{Implementation Choices}} & \\multicolumn{5}{c}{\\textbf{Design Metrics}} & \\multicolumn{5}{c}{\\textbf{Peformance Metrics}}  \\\\
 \\cmidrule(lr){1-7}  \\cmidrule(lr){8-12} \\cmidrule (lr){13-18}

&\\textbf{Impl.}&\\textbf{Fam.} &\\textbf{P} &\\textbf{Ref.} &\\textbf{FPGA} &\\textbf{Model Name} &\\textbf{Prec.} &\\textbf{C[OP]}&\\textbf{MB}  &\\textbf{D[\\%]} &\\textbf{B[\\%]} &\\textbf{MHz} &\\textbf{GOP/s} & \\textbf{P[W]} & \\textbf{T/P} &\\textbf{L[s]} &\\textbf{FPS}\\\\
 \\toprule
 """

table_foot = """
\\flushleft{
\\textit{FPGA:} AMD/XILINX Fpga names are stripped of leading  to increase readability\\\\
\\textit{Mem:} \\textbf{\\textdagger} Uses On-Chip Memory, \\textbf{?} Memory Location unknown\\\\
\\textit{Latency:} \\textbf{*} Latency of a single Pixel\\\\
\\textit{Model Name:} \\textbf{RDBC} Roller Dung Beetle Clustering, \\textbf{WNS} Weightless Neural System\\\\
}
"""

tab = TexTable(data, columns)
text = tab.render("", 4, table_head, table_foot)
footer = "\n\end{document}\n"

Path("./gen").mkdir(parents=True, exist_ok=True)

# Write single latex document to compile table
f = open("gen/table.tex", "w")
f.write(header + text + footer)
f.close()

# Export table to plain latex to copy into Survey
f = open("gen/export.tex", "w")
f.write(text)
f.close()
