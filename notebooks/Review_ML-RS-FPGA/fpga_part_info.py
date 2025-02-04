# About the DSPs, the 7-series use DSP48E1 and the US+ DSP48E2
#         "PART":  [YEAR,  DSP,   "Family/Type"]
fpga_part_info = {
    # 3 -Series
    "XC3SD1800A": [2006,    84,    "Spartan"],  # DSP48A

    # 6 -Series
    "VLX240T"   : [2009,   768,    "Virtex"],   # DSP48E1

    # 7 -Series
    "XC7A35T"   : [2010,    90,    "Artix"],
    "XC7A200T"  : [2010,   740,    "Artix"],
    "XC7K325T"  : [2010,   840,    "Kintex"],
    "VX690T"    : [2010,  3600,    "Virtex"],   # XC7VX690T (Virtex-7)
    "Z7020"     : [2011,   220,    "Zynq"],
    "Z7035"     : [2011,   900,    "Zynq"],
    "Z7045"     : [2011,   900,    "Zynq"],
    "Z7100"     : [2011,  2020,    "Zynq"],

    # Ultra Scale
    "XCKU040"   : [2013,  1920,    "Kintex"],
    "XQRKU060"  : [2018,  2760,    "Kintex"],  # https://thexrtc.org/lib/exe/fetch.php?media=wiki:sawant_xilinx_xqrku060_spaceupdate_dec2018.pdf (Should have an asterix as it is similar in performance to xcku060)

    # UltraScale+
    "ZU9EG"     : [2015,  2520,    "Zynq"],
    "ZU15EG"    : [2015,  3528,    "Zynq"],
    "ZU19EG"    : [2015,  1968,    "Zynq"],
    "ZU3EG"     : [2015,   360,    "Zynq"],
    "ZU7EV"     : [2015,  1728,    "Zynq"],
    "U280"      : [2018,  9024,    "Alveo"],   # Released Q1 2019 https://www.hpcwire.com/off-the-wire/xilinx-announces-new-alveo-u280-hbm2-accelerator-card/
    "XCK26"     : [2021,  1248,    "Kria"],    # (Internet search but uses Zynq MPSOC (2015 ...))

    # Intel
    "5CSXC6"    : [2012,   112,    "Cyclone"],
    "5CSEMA5F31C6": [2012,  87,    "Cyclone"]  # Terasic DE-01 board (Link: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/607/Cyclone_V_Device_Overview_Web.pdf (page 13 (A5)
}
