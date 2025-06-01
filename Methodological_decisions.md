# Methodological decisions
*This file was used to track all decisions made during the literature analysis and reporting. It is more exhaustive than the Methodology section of the paper.*

## Data Selection
***
When studies used several datasets for the same tasks, we selected only 1 representative dataset.
Examples of representative datasets chosen (These choices are arbitrary, within the scope of this survey):
- University of Pavia for HSI Pixel classification.
- MSTAR for SAR classification.
- DOTAv1.0 for RGB object detection.

For simplicity, the unusual modalities have been simplified in the table. More explicitly, \citet{yahiaouiParallelizationFuzzyARTMAP2017a} uses an infrared channel in addition to RGB, and \citet{wangFastDetectionObstacle2024} uses RGB and MilliMeter-Wave (MMW) radar data. These details are mentionned when describing the contribution of the study.

## Model Reporting
***
When a study evaluates the same model at different stages of optimization, we only report the "best" or last stage model. Refer to Section~\ref{section:RQ4_optimizations} for detailed descriptions of iterative design workflows.

Reporting DL architectures is challenging due to the number of different architectures. Indeed, some names are well-spread (VGG, ResNet), but some older architectures (AlexNet, GoogleNet) are commonly re-created, re-branded, or simply called "CNN". Therefore:
- We report the model's name used in the study.
- We also report the "core architecture" it is based on, i.e., its Backbone when available, otherwise its "equivalent model."
About the model selection in \cite{yangAlgorithmHardwareCodesign2022}: They target a specific latency, and it was obvious to pick the lower latency MobileNets because the same accuracy score, but we selected the model usnig more hardware ressources for SqueezeNet.

## Metric Reporting
***
We try to not hazard into figure reading. Metrics that could not be found in the text of the articles were not reported, at the exception of the accuracies (that we considered primordial).
When several accuracy metrics were available, we chose to report the most common one for the task. This means in detail:
- OA for all classification and pixel classification.
- mIoU for Segmentation.
- mAP for Object detection (mIoU would have been preferred, but too few articles reported mIoU).
Also, by default, we assumed that says "accuracy" in Classification, meant Overall Accuracy (OA).

Model size, Computational Throughput, and Power were all converted to respectively MB, GOP/s, and W.
For "Latency," we preferred the latency in ms over the image throughput in FPS. However, many studies report only the FPS.
Because of the possible use of pipelining within the accelerator, translating FPS to ms is not straightforward and was left as the original on-purpose.
In general, the processing time of a method is a relevant and important metric, especially for solutions aiming at real-time performance.
However, given the different problems and image sizes of the studies, direct comparisons are impossible.
Nevertheless, we consider such metric to be informative and report it in the tables.
Algorithms processing 1 pixel at a time, therefore subject to significantly lower latencies, are marked with *.


## FPGA: Choices Made
***
5 out of 46 articles used several FPGA boards. In each of these articles, one of the FPGAs was used for more experiments, and the authors reported more results. Therefore, we reported the most used board.
For example, in Table~\ref{table:rs-ml_taxonomy}, we report only the ZC106 and not the KU060 of \cite{rapuanoFPGAbasedHardwareAccelerator2021a}. This is also because the Zynq US+ family is more common than the Kintex US.
All FPGAs used in the studies are plotted in Figure~\ref{fig:fpga_distribution}.

If several software tools were used during the design and implementation of the solution, we only extracted the toolchain used for the ML component. For example, in \cite{huangEdgeTrustworthyAI2024}, VHDL is used for cryptographic modules, but Vitis AI is used for the models, so we report Vitis AI.

We separate the FPGA designs into two design paradigms (Specific, Flexible).
- A specific design can exclusively support one network architecture without re-implementation of the bitstream. This can include different weights but not different layers or a different sequence of layers.
- Everything else is classified as flexible and thus able to support either different layers, different hyperparameters, or a different sequence of layers without having to re-implement the bitstream and reconfigure the FPGA.

The memory accesses are separated based on the location from which memory is loaded during the operation of the network.
- If weights are encoded insight the bitstream or are loaded once before inference starts, the memory is classified as on-chip as no major access to DRAM or other off-chip memory is required during inference.
- If the FPGA design accesses DRAM during operation to load parameters, it is classified as off-chip.

Some models use different quantization for different layers, we report this either as mixed or as one of the precision's if a significant majority of the operation is performed in this precision
