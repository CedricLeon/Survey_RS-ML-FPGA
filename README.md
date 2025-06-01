# Survey RS-ML-FPGA
@TODO: add the html tags
@TODO: add links to markdown sections.

## Description
***
This repository provides context to the manuscript "FPGA-Enabled Machine Learning Applications in Earth Observation: A Systematic Review" submitted at ACM CSUR and available on [arXiv]().

**How to cite**
@TODO + move at the end of README?

### Content
The literature data, the code for the data analysis, figure and table generation, as well as the supplemental material are available here.
Below you will find supplemental sections of the survey (moved because of the 35-page limit) and instructions to run code snippets. 

#### Repo structure
**General**:
- [metadata.py](src/utils/metadata.py): Contains color, model cores, and FPGA information used in the different notebooks.
- [analysis.ipynb](src/analysis.ipynb): Contains high-level analysis of the experiments.
- [fpga_metrics.py](src/fpga_metrics.py): ???? @dirkstober
- [plotting_exploration.ipynb](src/plotting_exploration.ipynb: Contains a wide diversity of deprecated figures)

**Figure generation**:
- [fig_applications_tasks.ipynb](src/fig_applications_tasks.ipynb): Visualization of relations between RS applications and ML tasks (Fig.1)
- [fig_ML_models.ipynb](src/fig_ML_models.ipynb): Visualization of all ML models used in the experiments (Fig. 2)
- [fig_FPGA_boards.ipynb](src/fig_FPGA_boards.ipynb): Visualization of the FPGA boards used in the articles (Fig. 3)
- [fig_dataset_treemap.ipynb](src/fig_dataset_treemap.ipynb): Visualization of the datasets and tasks as a treemap using [squarify](https://github.com/laserson/squarify) (unused in the manuscript)

**Table generation**:
- [table_RS-ML.ipynb](src/table_RS-ML.ipynb): Generates the LaTeX code for the RS/ML taxonomy (Table 2)
- [table_FPGA.py](src/table_FPGA.py): Generates the LaTeX code for the FPGA taxonomy (Table 3)

### Workflow
This systematic survey was conducted following the PRISMA 2020 guidelines. Studies were exported from Web of Science to Zotero, where records have been, screened, tagged and summarized.
Zotero API was later accessed through Python to analyze the data and generate the survey's material.

> Note: While the surveyed studies and their tags are available in this repository (`data/Dataframes/`), the complete original Zotero collection is locked behind Zotero API key system.
> See `src/utils/Zotero_data_processing/create_articles_df.py` and @TODO: find URL to obtain personal Zotero API keys, and @TODO: add file links


## Supplemental material
***

### Methodological Considerations
*The section below was originally contained in the manuscript. It consists in a shortened version of the complete [methodological considerations](Methodological_decisions.md).*
Due to the heterogeneity of the surveyed research, arising from diverse backgrounds, motivations, data, models, and hardware platforms, we make several methodological decisions to ensure consistency and clarity in result reporting.

#### Data and Model Reporting
When studies evaluate multiple datasets for the same task, we select a representative dataset for reporting (e.g., University of Pavia **[1]** for HSI pixel classification, MSTAR **[2]** for SAR classification, DOTAv1.0 **[3]** for RGB object detection). Similarly, for studies iteratively optimizing models, we report results for the best-performing final-stage model; see Section 4.1 for a description of iterative optimization workflows. To address the challenge of diverse naming conventions for Deep Learning architectures, we report the model's name as used in the study alongside its underlying backbone architecture when available. Such practice aims to clarify model architectures, given that some older architectures, e.g., LeNet **[4]** or AlexNet **[5]**, are commonly re-branded, called "CNN."

#### Hardware and Implementation Decisions
In cases where studies utilize multiple FPGA products, we select the device used in most experiments. However, for a fair snapshot of the landscape, Fig. ***3*** shows the complete distribution of FPGAs used in the surveyed studies. When solutions involve a combination of software tools, we extract the toolchain used for the Machine Learning component. We classify FPGA designs based on their architectural paradigm (*Specific* or *Flexible*), depending on their ability to support different networks, diverse hyperparameters, or various sequences of layers without re-implementation of the bitstream. Furthermore, memory accesses are separated based on the location from which parameters are loaded during the operation of the network. We use the notation *i(width)* for fixed-point and integer as fixed-point arithmetic equals an integer operation followed by a shift. *f(width)* represents floating-point datatype and *b* for binary.

#### Metrics and Units Standardization
To standardize performance reporting, we preferred to report the most common accuracy metric for each task: Overall Accuracy (**OA**) for Classification and Pixel Classification, mean Intersection over Union (**mIoU**) for Segmentation, and mean Average Precision (**mAP**) for Object Detection (**mIoU** would have been preferred, but too few articles reported **mIoU**). When such accuracy is unavailable, we turn to second-choice metrics such as **F1-score** or **SSIM**. Model size, computational Throughput, and Power consumption are converted to MegaBytes **[MB]**, Giga Operation per second **[GOP/s]**, and Watts **[W]**, respectively. Although processing time is a highly relevant metric, especially for real-time solutions, varying image sizes across studies makes direct comparisons impossible. Nevertheless, algorithms processing one pixel at a time, and thus subject to significantly lower latencies, are marked with an asterisk **$^*$**. Latency, when available, in milliseconds (**[ms]**) is preferred over Frames Per Second (**[FPS]**) but is left unconverted due to the common usage of pipelining.

### Space Constraints on Edge Systems
*The section below was originally contained in the manuscript, before comparing FPGAs to other Processing Units (PUs).*
Deploying edge systems in space introduces unique challenges beyond terrestrial applications. Foremost is radiation exposure, where spaceborne equipment is continuously bombarded by radiation, causing Single-Event Effects (SEEs) in onboard electronics **[6]**. These SEEs manifest as Single Event Upsets (SEUs), which are non-destructive soft errors that alter the logic state of memory, or as Single Event Latch-ups (SELs), potentially destructive hard errors requiring a power reset. The frequency of SEEs and their potential to cause operational and functional changes pose significant challenges to reliable operation. Siegle et al. **[7]** provide a comprehensive overview of radiation effects and established mitigation strategies.
From a 2017 NASA report on SmallSats **[8]**:
> Single event effects (SEE) is the disturbance created by single particles hitting the electronics (Nguyen, 2015). Total dose is measured in krad and can affect transistor performance. Single event upsets (SEU) can affect the logic state of memory. A single event latchup (SEL) can affect the output transistors on CMOS logic, potentially causing a high-current state.

Furthermore, extreme temperature variations—from $-150^\circ$C to $+150^\circ$C **[9]**—necessitate sophisticated thermal management. Because vacuum conditions prevent fan-based cooling, electronic components must dissipate heat through radiation, a significantly less efficient method. This constraint underscores the imperative for energy-efficient solutions that minimize heat generation. In addition to radiation and thermal challenges, edge devices must comply with strict Size, Weight, and Power (SWaP) constraints, which directly impact their feasibility for space deployment. In particular, power budgets remain highly limited, typically ranging from $20$W to $95$W for SmallSat payloads **[10]**, reinforcing the need for low-power hardware acceleration. These systems must also endure the extreme conditions of launch, including substantial vibrations **[11]**, without compromising structural integrity. Operating reliably in a vacuum environment requires careful material selection to prevent outgassing, which could degrade performance or contaminate optical sensors.

### Other supplemental material
*@TODO: add description*

### References
**[1]** Hyperspectral Remote Sensing Scenes—Grupo de Inteligencia Computacional. (n.d.). Retrieved November 7, 2024, from https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes
**[2]** MSTAR dataset. (n.d.). Retrieved November 6, 2024, from https://www.sdms.afrl.af.mil/index.php?collection=mstar
**[3]** Xia, G.-S., Bai, X., Ding, J., Zhu, Z., Belongie, S., Luo, J., Datcu, M., Pelillo, M., & Zhang, L. (2018). DOTA: A Large-Scale Dataset for Object Detection in Aerial Images. 3974–3983. https://openaccess.thecvf.com/content_cvpr_2018/html/Xia_DOTA_A_Large-Scale_CVPR_2018_paper.html
**[4]** Lecun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). Gradient-based learning applied to document recognition. Proceedings of the IEEE, 86(11), 2278–2324. Proceedings of the IEEE. https://doi.org/10.1109/5.726791
**[5]** Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). ImageNet Classification with Deep Convolutional Neural Networks. Advances in Neural Information Processing Systems, 25. https://proceedings.neurips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html
**[6]** Lange, K., Fontana, F., Rossi, F., Varile, M., & Apruzzese, G. (2024). Machine Learning in Space: Surveying the Robustness of on-board ML models to Radiation (No. arXiv:2405.02642). arXiv. https://doi.org/10.48550/arXiv.2405.02642
**[7]** Siegle, F., Vladimirova, T., Ilstad, J., & Emam, O. (2015). Mitigation of Radiation Effects in SRAM-Based FPGAs for Space Applications. ACM Comput. Surv., 47(2), 37:1-37:34. https://doi.org/10.1145/2671181
**[8]** NASA, Washington, DC, USA, Tech. Rep. (2015). Small Spacecraft Technology State of the Art. NASA/TP-2015-216648/REV. https://sst-soa.arc.nasa.gov
**[9]** Gordo, P., Frederico, T., Melicio, R., Duzellier, S., & Amorim, A. (2020). System for space materials evaluation in LEO environment. Advances in Space Research, 66(2), 307–320. https://doi.org/10.1016/j.asr.2020.03.024
**[10]** Kothari, V., Liberis, E., & Lane, N. D. (2020). The Final Frontier: Deep Learning in Space. Proceedings of the 21st International Workshop on Mobile Computing Systems and Applications, 45–49. https://doi.org/10.1145/3376897.3377864
**[11]** Jung, I. H., Park, T. W., Seo, J. H., Han, S. W., & Kim, S. H. (2004). Structural Vibration Analysis of Electronic Equipment for Satellite under Launch Environment. Key Engineering Materials, 270–273, 1440–1445. https://doi.org/10.4028/www.scientific.net/KEM.270-273.1440








### Other
*@TODO: Add future supplemental materials*

## Repository instructions
***
### Run the notebooks
If your goal is simply to recreate the figures/tables or to play around with the code analysis. You should be able to simply run the notebooks, once you have created a virtual environment with the required packages:
```bash
conda create -n rs_ml_fpga # @TODO: Python version?
conda activate rs_ml_fpga
pip install -r requirements.txt
```

### Follow a similar workflow
This repository was also created for future researcher interested to recreate such processing pipelines. If this is your case, the instructions below should be a good starting point. While these instructions do not act as a tutorial, we hope they can help the start of your journey 🙃.

#### Exporting records to Zotero
After prompting the research searchbase of your choice, you have to export your results to the bibliographic tool of your choice. 
> I do not have experience with any other tool, but I have never encountered something I could not do in Zotero.
We recommend selecting the RIS file format.

#### Setting up Zotero
For organization's sake, we recommend creating new collections at each step of your processing, for example when importing the records in Zotero.
If you want to collaborate directly on the Zotero collection, have a look at @TODO add link to shared collections
Finally, Zotero's tags have a color system which can come really handy when several authors read the articles.

#### Accessing Zotero's API
Before any coding you should obtain a couple information, mainly: Your private Zotero API Key accessible here @TODO: add link.
To be able to use similar logic as `explore_zotero_API.ipynb`, you will need to store your Zotero API Key in this file `src/Zotero_data_processing/.keys`. It should have a similar format:
```json
Zotero API Key: <your_api_key>
```
You will also need your collection keys @TODO or identifier

#### Fecthing your Zotero's data
It is very likely that by that time, your setup will have differed in some manner. Nevertheless, if you want to run the scripts exactly as they are:
```bash
python ./src/Zotero_data_processing/create_articles_df.py -o data/Dataframes/all_articles.pkl
python ./src/Zotero_data_processing/create_datapoints_df.py -i data/Dataframes/all_articles.pkl -o data/Dataframes/all_datapoints.pkl
```
You can also force the naming of the first scripts with `-o all_articles.pkl` for example.
`create_datapoints_df.py` can also be run with different verbose levels (`-v`, `-vv`, or `-vvv`) to see more details.

> Keep in mind that the second scripts already parses Zotero tags, which will result in an error if your implementqtion does not have exactly the same structure than ours 


##  Acknowledgement
***
I would like to thank Ivica Obadic and Adrian Höhl, for the early tips of the project, especially about PRISMA and Zotero. @TODO refine and GitHub usernames

This repository benefited from the use of GitHub Copilot (o1-preview), which assited by proposing code snippets, especially for `matplotlib` figure rendering.
