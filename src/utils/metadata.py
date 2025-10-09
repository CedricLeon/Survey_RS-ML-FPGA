plot_colors: dict[str, str] = {
    "mpl_blue": "#1f77b4",  # Default matplotlib blue
    "blue_1":   "#2066a8",  # Blues
    "blue_2":   "#4B93BA",
    "blue_3":   "#8cc5e3",
    "blue_4":   "#AFD8ED",
    "red_1":    "#A71313",  # Reds
    "red_2":    "#af2c2c",
    "red_3":    "#c46666",
    "red_4":    "#E18A8A",
    "red_5":    "#F7ABAB",
    "green_1":  "#389339",  # Greens
    "green_2":  "#58b459",
    "green_3":  "#83d984",
    "green_4":  "#BAF4BB",
    "teal_1":   "#1f6f6f",  # Teals
    "teal_2":   "#54a1a1",
    "teal_3":   "#9fc8c8",
    "orange_1": "#F49515",  # Oranges
    "orange_2": "#F2AB4C",
    "orange_3": "#F6BD71",
    "gray":     "#aaaaaa",  # Gray
    "dark_gray": "#7A7A7A", 
}
general_task_colors = {
    'Classification': plot_colors["blue_1"],
    'Segmentation - Pixel': plot_colors["teal_2"],
    'Object detection': plot_colors["red_1"],
    'Segmentation - Tile': plot_colors["green_1"],
    'Regression': plot_colors["gray"],
}


# About the DSPs, the 7-series use DSP48E1 and the US+ DSP48E2
#         "PART":  [YEAR,  DSP,   "Family/Type"]
fpga_part_info = {
    # 3 -Series
    "XC3SD1800A"    : [2006,    84,    "Spartan"],  # DSP48A

    # 6 -Series
    "XC6VLX240T"    : [2009,   768,    "Virtex"],   # DSP48E1

    # 7 -Series
    "XC7A35T"       : [2010,    90,    "Artix"],
    "XC7A200T"      : [2010,   740,    "Artix"],
    "XC7K325T"      : [2010,   840,    "Kintex"],
    "XC7VX690T"     : [2010,  3600,    "Virtex"],   # XC7VX690T (Virtex-7)
    "XC7Z020"       : [2011,   220,    "Zynq"],
    "XC7Z035"       : [2011,   900,    "Zynq"],
    "XC7Z045"       : [2011,   900,    "Zynq"],
    "XC7Z100"       : [2011,  2020,    "Zynq"],

    # Ultra Scale
    "XCKU040"       : [2013,  1920,    "Kintex"],
    "XQRKU060"      : [2018,  2760,    "Kintex"],  # https://thexrtc.org/lib/exe/fetch.php?media=wiki:sawant_xilinx_xqrku060_spaceupdate_dec2018.pdf (Should have an asterix as it is similar in performance to xcku060)

    # UltraScale+
    "XCZU9EG"       : [2015,  2520,    "Zynq"],
    "XCZU15EG"      : [2015,  3528,    "Zynq"],
    "XCZU19EG"      : [2015,  1968,    "Zynq"],
    "XCZU3EG"       : [2015,   360,    "Zynq"],
    "XCZU7EV"       : [2015,  1728,    "Zynq"],
    "U280"          : [2018,  9024,    "Alveo"],   # Released Q1 2019 https://www.hpcwire.com/off-the-wire/xilinx-announces-new-alveo-u280-hbm2-accelerator-card/
    "XCK26"         : [2021,  1248,    "Kria"],    # (Internet search but uses Zynq MPSOC (2015 ...))

    # Intel
    "5CSXC6"        : [2012,   112,    "Cyclone"],
    "5CSEMA5F31C6"  : [2012,  87,    "Cyclone"]  # Terasic DE-01 board (Link: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/607/Cyclone_V_Device_Overview_Web.pdf (page 13 (A5)
}

def assign_model_core(row):
    # Combine the values from the three columns
    combined_info = f"{row['Model']} {row['Equivalent model']} {row['Backbone']}".upper()
    for keyword, core_label in model_core_map.items():
        if keyword.upper() in combined_info:
            return core_label
    raise ValueError(f"Model core not found for row: {row}")

def rename_application(app: str) -> str:
    if app == "Safe UAV landing site identification":
        return "UAV landing site id."
    elif app == "Railway track fastener defect detection":
        return "Railway defect det."
    app = app.replace("identification", "id.")
    app = app.replace("detection", "det.")
    app = app.replace("classification", "class.")
    app = app.replace("extraction", "extr.")
    return app

model_core_map = {
    # Deep Learning
    'ALEXNET': 'AlexNet',
    'YOLO': 'YOLO',
    'SSD': 'SSD',
    'VGG': 'VGG',
    'RESNET': 'ResNet',
    'GHOSTNET': 'GhostNet',
    'U-NET': 'U-Net',
    'MOBILENET': 'Custom CNN', # to avoid being identify as "LeNet"
    # 'FPN': 'Custom CNN',
    # 'SQUEEZENET': 'Custom CNN',
    # 'ENET': 'Custom CNN',
    # 'ESPNET': 'Custom CNN',
    'LENET': 'LeNet',
    'VIT': 'ViT',

    # Shallow Neural Networks
    'MLP': 'Shallow NN',
    'DEEP BELIEF NETWORK': 'Shallow NN',
    'WEIGHTLESS NEURAL SYSTEMS': 'Shallow NN',

    # Graph Neural Networks
    'GNN': 'GNN',

    # Traditionnal Machine Learning
    'SVM': 'Trad. ML',
    'DECISION TREE': 'Trad. ML',
    'Fuzzy ARTMAP': 'Trad. ML',
    'LPDBL': 'Trad. ML',
    'ROLLER DUNG BETTLE CLUSTERING': 'Trad. ML',
    # Mixed models
    'CAL-SC2S': 'Trad. ML',
    'CAG-SC2S': 'Trad. ML',

    # Not enough information
    'CNN': 'Custom CNN',
}