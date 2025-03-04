import pandas as pd

import argparse
from pathlib import Path
from tqdm import tqdm
import datetime

from utils import parse_string_parentheses_braces, extract_year_from_string, print_pretty_df

# Quick ANSI color code shortcuts
r = "\033[31m"
y = "\033[33m"
g = "\033[32m"
b = "\033[34m"
e = "\033[0m"

def get_article_main_info_from_tags(tagsList):
    """_summary_
    From the list of tags of an item, return lists with the main information about the article.
    It is used to detect if an item compares several models, possibly on several board/dataset/or even task

    Args:
        tagsList (List[str]): The list of tags (as strings) of an article

    Returns:
        dict[str, list[str]]: Dictionnary with 6 keys: "Board", "Implementation", "Modality", "Models", "Datasets" and "Tasks" and the corresponding list of tags
    """
    parsedData = {
        "Board": [],
        "Implementation": [],
        "Modality": [],
        "Models": [],
        "Datasets": [],
        "Tasks": [],
    }

    for tag in tagsList:
        if tag.startswith("Dataset:"):
            parsedData["Datasets"].append(tag.split("Dataset: ")[1].strip())
        elif tag.startswith("Model:") and tag != "Model: N/A":
            parsedData["Models"].append(tag.split("Model: ")[1].strip())
        elif tag.startswith("Board:"):
            parsedData["Board"].append(tag.split("Board: ")[1].strip())
        elif tag.startswith("Task:"):
            parsedData["Tasks"].append(tag.split("Task: ")[1].strip())
        elif tag.startswith("Implementation:"):
            parsedData["Implementation"].append(
                tag.split("Implementation: ")[1].strip()
            )
        elif tag.startswith("Modality:"):
            parsedData["Modality"].append(tag.split("Modality: ")[1].strip())
    
    def warning_for_multiple_values(key, dict):
        if len(dict[key]) > 1:
            log_debug(f"    {r}Warning{e}: Multiple {key}s detected for {b}{tagsList}{e}")

    warning_for_multiple_values("Board", parsedData)
    warning_for_multiple_values("Implementation", parsedData)
    warning_for_multiple_values("Modality", parsedData)
    return parsedData

def extract_metrics(
    article, reportsSeveralModels=False, fullTagModelName=""
):
    """_summary_
    Extracts all systematically reported performance metrics from a DataFrame's row.
    
    Metrics extracted:
    - Latency (in ms or FPS)
    - Task score (e.g., % OA, % F1, % mIoU)
    - Footprint (in MB)
    - Throughput (in GOP/s)
    - Power consumption (in W)
    - Frequency (in MHz)
    - Complexity (in OPs)

    If a metric is missing, i.e., value 'N/A', it is notified and its value is set to an empty string (for clarity when printing).

    Args:
        article (pd.Series): a DataFrame's row (a single article), containing all the data of a model reported in an article.
        reportsSeveralModels (bool, optional): whether the article reports several models or not. Defaults to False.
        fullTagModelName (str, optional): the name of the model with all its info, it is ONLY used when reportsSeveralModels is True.
                                          In which case the tags with the metrics of interest start with "(<backbone>)" or "(<modelName>)". Defaults to "".

    Returns:
        dict[str, str]: Dictionary with 5 keys: "Latency", "Task score", "Footprint", "Throughput" and "Power consumption".
    """
    citationKey = article.name  # The ID of a DataFrame's row, is the name of the Serie
    if reportsSeveralModels:
        if not fullTagModelName:
            raise ValueError(
                f"fullTagModelName should be given when an article reports several models, see {citationKey}"
            )
        else:
            modelName, _, backbone = parse_string_parentheses_braces(fullTagModelName)

    # Define a mapping of clean metric names to their tag prefixes (with ': ')
    metricKeys = {
        "Latency": "Model latency: ",               # in ms, us or  (an '*' symbol means it's per pixel instead of per patch)
        "FPS": "Model FPS: ",                       # in FPS
        "Task score": "Model performance: ",        # in % OA, % F1, % mIoU, etc.
        "Footprint": "Model size: ",                # in MB
        "Throughput": "Model throughput: ",         # in GOP/s
        "Power consumption": "Power consumption: ", # in W
        "Frequency": "Frequency: ",                 # in MHz
        "Complexity": "Model complexity: ",         # in OPs (e.g., '50G OP', '45.67M OP')
    }

    metricsFoundDict = {}
    missingMetricsList = []

    def extract_metric_value(tag, tagPrefix):
        """Helper function to extract metric value from a tag."""
        metricValue = tag[len(tagPrefix):].strip()
        return "" if metricValue.startswith("N/A") else metricValue

    for metric, tagPrefix in metricKeys.items():
        found = False
        for tag in article["Tags"]:
            if tag.startswith(tagPrefix):
                # Check for the parenthesis syntax (for articles reporting several models)
                if reportsSeveralModels:
                    # Extract model name from tag (e.g., '(ModelName)')
                    tagContent = tag[len(tagPrefix):].strip()
                    if tagContent.startswith('('):
                        modelNameInTag = tagContent[1:].split(')')[0].strip()
                        if modelNameInTag == modelName or modelNameInTag == backbone:
                            metricValue = tagContent.split(')', 1)[1].strip()
                            metricsFoundDict[metric] = metricValue
                            found = True
                            break
                    else:
                        # If the tag does not start by the model name, it means its value is 'N/A' or it's the Frequency metric
                        if tag.startswith("Frequency:"):
                            metricValue = extract_metric_value(tag, tagPrefix)
                            metricsFoundDict[metric] = metricValue
                            found = True
                            break
                        else:
                            if 'N/A' in tag: metricValue = 'N/A'

                # If the article does not report several models, the tag is directly the metric value
                else:
                    metricValue = extract_metric_value(tag, tagPrefix)
                    metricsFoundDict[metric] = metricValue
                    found = True
                    break

        if not found:
            metricsFoundDict[metric] = ""
            missingMetricsList.append(metric)
        else: # Specific handling for some metrics
            if metric == "Model performance" and "Acc" in metricsFoundDict[metric]:
                log_debug(f"    {r}Acc metric warning{e}: Model performance was reported as Acc in {b}{citationKey}{e}: {g}{metricsFoundDict[metric]}{e}, replacing it with OA")
                metricsFoundDict[metric] = metricsFoundDict[metric].replace("Acc", "OA")
            # Specific handling for 'Frequency' metric (ensure unit is MHz)
            elif metric == "Frequency" and metricsFoundDict[metric] and not metricsFoundDict[metric].endswith("MHz"):
                log_debug(f"    {r}Frequency unit warning{e}: Frequency in {b}{citationKey}{e} is not in MHz: {g}{metricsFoundDict[metric]}{e}")
            # Specific handling for 'Model complexity' metric (ensure unit is OP)
            elif metric == "Model complexity" and not metricsFoundDict[metric].endswith("OP"):
                log_debug(f"    {r}Model complexity unit warning{e}: Model complexity in {b}{citationKey}{e} does not have 'OP' unit: {g}{metricsFoundDict[metric]}{e}")
            # Specific handling for 'Latency' metric (ensure unit is ms, s, or us)
            elif metric == "Latency":
                valid_units = ["ms", "s", "us", "ms*", "s*", "us*"]
                if metricsFoundDict[metric] and not any(metricsFoundDict[metric].endswith(u) for u in valid_units):
                    log_debug(
                        f"    {r}Latency unit warning{e}: Latency in "
                        f"{b}{citationKey}{e} is not in one of {valid_units}: "
                        f"{g}{metricsFoundDict[metric]}{e}"
                    )
            elif metric == "FPS":
                if metricsFoundDict[metric] and not metricsFoundDict[metric].endswith("FPS"):
                    log_debug(
                        f"    {r}FPS unit warning{e}: FPS in "
                        f"{b}{citationKey}{e} does not end in 'FPS': "
                        f"{g}{metricsFoundDict[metric]}{e}"
                    )

    if missingMetricsList:
        modelIdentifier = modelName if reportsSeveralModels else 'its unique model'
        log_debug(f"    {r}Missing metric warning{e}: {b}{citationKey}{e} misses: {r}{', '.join(missingMetricsList)}{e} metrics for {b}{modelIdentifier}{e}")

    return metricsFoundDict

# @TODO: I'm unsatisfied with the format of the extracted details for the accelerator.
# I decided to return a dict with all the tags found, because that's the most flexible.
# But in the future I'd like to make a distinction between DPU and classic RTL/HLS accelerators.
# @TODO: There is also a "bug", for pitonakCloudSatNet1FPGABasedHardwareAccelerated2022 for example, I reused the (<model_name>) mechanic, 
# because the reported models use different Precision, I have to account for that in the extraction.
def extract_accelerator_design(article, articleMainInfo, reportsSeveralModels=False, fullTagModelName=""):
    """_summary_
    Extracts the accelerator design details from the tags of an article.
    If an article reports several models, the parentheses syntax ("<tagNme>: (<modelName>) <value>") is checked for each tag.

    Details extracted:
    - Design: what models are supported ('Library', 'Various kernels', 'Model Specific', etc.)
    - Memory: where is the model stored ('On-chip', 'Off-chip', etc.)
    - Precision: what precision is used ('Original', 'Fixed (16)', 'Mixed', etc.)
    - Resource Utilization: how much resources are used ('Low', 'Average', or 'High')
    - Optimizations: a list of optimizations applied ('Multiple PEs', 'Advanced Dataflow', 'DSP double rate', etc.)

    If the implementation is made using Vitis AI, the tags are different:
    - DPU Config: the parallelism of the DPU ('B1024', 'B4096', etc.)
    - DPU Core: number of instances of the DPU (1, 2, or 3)
    - DPU Util: how much of the DPU is used (in %)
    - DPU Optimizations: a list of optimizations applied ('DSP double rate', 'UltraRAM', etc.)
    - The Precision is also reported and the same.

    Args:
        article (pd.Series): a DataFrame's row (a single article), containing all the data of a model reported in an article.
        articleMainInfo (dict[str, list[str]]): a dictionary with 6 keys: "Board", "Implementation", "Modality", "Models", "Datasets" and "Tasks".

    Returns:
        dict[str, list[str]]: List of the tags and their values
    """
    if reportsSeveralModels:
        if not fullTagModelName:
            raise ValueError(
                f"fullTagModelName should be given when an article reports several models, see {article.name}"
            )
        else:
            modelName, _, backbone = parse_string_parentheses_braces(fullTagModelName)
    
    detailsKeys = {
        "Design": "FPGA Design: ",
        "Memory": "FPGA Mem: ",
        "Precision": "FPGA Prec: ",
        "Optimizations": "FPGA Opt: ",
        "FPGA Util": "FPGA Util: ",
        "DPU Config": "DPU Config: ",
        "DPU Core": "DPU Core: ",
        "DPU Util": "DPU Util: ",
        "DPU Optimizations": "DPU Opt: ",
    }

    detailsFoundDict = {}
    tags = article["Tags"]
    
    # Check if the implementation is Vitis AI
    is_vitis_ai = any(impl == "Vitis AI" for impl in articleMainInfo["Implementation"])

    # Initialize detailsFoundDict with keys and default values
    for key in detailsKeys.keys():
        if key in ["Optimizations", "DPU Optimizations"]:
            detailsFoundDict[key] = []
        else:
            detailsFoundDict[key] = ""

    # Go through the tags and extract values
    for tag in tags:
        for key, tagPrefix in detailsKeys.items():
            if tag.startswith(tagPrefix):
                tagContent = tag[len(tagPrefix):].strip()
                if reportsSeveralModels and tagContent.startswith('('):
                    modelNameInTag = tagContent[1:].split(')')[0].strip()
                    if modelNameInTag == modelName or modelNameInTag == backbone:
                        # print(f"In {article.name}, for Model {fullTagModelName}, {tagPrefix}: {tagContent}")
                        tagContent = tagContent.split(')', 1)[1].strip()
                    else:
                        continue
                if key in ["Optimizations", "DPU Optimizations"]:
                    # Handle multiple optimizations
                    optimizations = [opt.strip() for opt in tagContent.split(',')]
                    detailsFoundDict[key].extend(optimizations)
                else:
                    detailsFoundDict[key] = tagContent
                break  # Found the tag, move to the next

    return detailsFoundDict

def get_hardcoded_articles(citationKey, nameUsedInArticle):
    """
    Returns specific 'Dataset', 'Task', and 'Application' for certain articles.
    """
    # Both articles test several models on several datasets: YOLO for DOTA, and VGG16 and ResNet-34 for NWPU-RESISC45
    if citationKey in ["yanAutomaticDeploymentConvolutional2022a", "niAlgorithmHardwareCoOptimization2023"]:
        if "YOLO" in nameUsedInArticle:
            return {
                "Dataset": "DOTAv1.0 {Object Detection}",
                "Task": "Object detection",
                "Application": "Diverse",
            }
        else:
            return {
                "Dataset": "NWPU-RESISC45 {Classification}",
                "Task": "Classification",
                "Application": "Landcover/Land use",
            }
    else:
        return None
    
def check_article_validity(articleMainInfo, citationKey):
    """
    Checks the validity of an article's main information.
    Raises a ValueError with an appropriate message if invalid.
    """
    if len(articleMainInfo["Board"]) > 1:
        error_message = f"- {y}(SKIP){e}: {b}{citationKey}{e} has multiple boards: {b}{articleMainInfo['Board']}{e}"
        raise ValueError(error_message)
    if len(articleMainInfo["Modality"]) > 1:
        error_message = f"- {y}(SKIP){e}: {b}{citationKey}{e} has multiple modalities: {b}{articleMainInfo['Modality']}{e}"
        raise ValueError(error_message)
    if "???" in articleMainInfo["Models"]:
        error_message = f"- {y}(SKIP){e}: {b}{citationKey}{e} has unspecified models."
        raise ValueError(error_message)

def process_article(citationKey, article):

    articleMainInfo = get_article_main_info_from_tags(article["Tags"])
    check_article_validity(articleMainInfo, citationKey)
    log_debug(""); log_debug(f"Main information: {articleMainInfo}")

    modelsFromArticle = []
    nbModels = len(articleMainInfo["Models"])
    nbDatasets = len(articleMainInfo["Datasets"])
    log_info(f"- {y}(Processing){e} {b}{citationKey}{e} reports {r}{nbModels}{e} models.")

    for i, model in enumerate(articleMainInfo["Models"]):
        nameUsedInArticle, nameCorrespondingModel, backbone = parse_string_parentheses_braces(model)

        # Check for specific articles that require overridden info
        specificInfo = get_hardcoded_articles(citationKey, nameUsedInArticle)
        if specificInfo:
            dataset = specificInfo["Dataset"]
            task = specificInfo["Task"]
            application = specificInfo["Application"]
        # Use default values
        else:
            if nbDatasets == 1:
                dataset = articleMainInfo["Datasets"][0]
            elif nbDatasets == nbModels and i < nbDatasets:
                dataset = articleMainInfo["Datasets"][i]
            else:
                raise ValueError(f"    - {y}(SKIP){e} Missing dataset for model {nameUsedInArticle}")

            if len(articleMainInfo["Tasks"]) == 1:
                task = articleMainInfo["Tasks"][0].split("(")[0].strip()
                application = articleMainInfo["Tasks"][0].split("(")[1][:-1].strip()
            elif len(articleMainInfo["Tasks"]) == nbModels and i < len(articleMainInfo["Tasks"]):
                task = articleMainInfo["Tasks"][i].split("(")[0].strip()
                application = articleMainInfo["Tasks"][i].split("(")[1][:-1].strip()
            else:
                raise ValueError(f"    - {y}(SKIP){e} Missing task/application for model {nameUsedInArticle}")

        main_info = {
            "BBT Citation Key": citationKey,
            "Model": nameUsedInArticle,
            "Equivalent model": nameCorrespondingModel,
            "Backbone": backbone,
            "Modality": articleMainInfo["Modality"][0],
            "Dataset": dataset,
            "Task": task,
            "Application": application,
            "Board": articleMainInfo["Board"][0],
            "Implementation": articleMainInfo["Implementation"][0],
            "Publication year": extract_year_from_string(article["Date"]),
        }

        performance_metrics = extract_metrics(
            article,
            reportsSeveralModels=(nbModels > 1),
            fullTagModelName=model,
        )
        fpga_accelerator = extract_accelerator_design(
            article,
            articleMainInfo, # unused so far
            reportsSeveralModels=(nbModels > 1),
            fullTagModelName=model
        )

        modelsFromArticle.append(main_info | performance_metrics | fpga_accelerator)

        log_info(
            f"      - {b}{nameUsedInArticle}{e} ({backbone}) on {b}{dataset}{e} with performance: {r}{list(performance_metrics.values())}{e}."
        )

    return modelsFromArticle

def log_info(msg):
    if VERBOSITY >= 1: print(msg)
def log_debug(msg):
    if VERBOSITY >= 2: print(msg)
def log_dataframe(df):
    if VERBOSITY >= 3:
        print_pretty_df(df)
        print(f"{r}The Datfarme being very wide, it is recommended to redirect the script output to a file.{e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract all experiments from each individual article.")
    parser.add_argument("--input", "-i", type=str, help="Path of the input Dataframe with the articles.")
    parser.add_argument("--output", "-o", type=str, help="Output path for the pickled Dataframe.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity. Use multiple -v for higher verbosity. 3 is the highest: prints everything, including the full Dataframe created.")
    args = parser.parse_args()

    VERBOSITY = args.verbose if args.verbose else 0
    if VERBOSITY == 0:
        print("Verbosity: [NONE] Minimal info.")
    elif VERBOSITY == 1:
        print("Verbosity: [INFO] Normal verbose info.")
    else:
        print("Verbosity: [DEBUG] Full debug info.")

    # Paths management
    if not args.input:
        raise ValueError("An input path is required.")
    if args.output:
        allDatapointsPath = Path(args.output)
        allDatapointsPath.parent.mkdir(parents=True, exist_ok=True)
    else:
        allDfPaths = Path(__file__).parent.parent.parent / "data" / "Review_ML-RS-FPGA" / "Dataframes"
        allDatapointsPath = allDfPaths / f"all_datapoints_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"

    log_debug(f"Dataframe read from path: {args.input}")
    articlesDf = pd.read_pickle(args.input)
    
    # Main processing loop
    listOfModelsFromArticle = []
    nbArticlesProcessed = 0

    for citationKey, article in articlesDf.iterrows():
        modelsReportedInArticle = process_article(citationKey, article)
        if modelsReportedInArticle:
            listOfModelsFromArticle.extend(modelsReportedInArticle)
            nbArticlesProcessed += 1
        else:
            raise ValueError(f"{y}(SKIPPED){e}: {b}{citationKey}{e} did not report any model.") # Should not happen, errors are raised earlier, but ... you never know 😅

    # Create the DataFrame
    allModelsDF = pd.DataFrame(listOfModelsFromArticle)
    print(f"A total of {r}{len(allModelsDF)}{e} models were extracted from the {b}{nbArticlesProcessed}{e} processed articles.")
    allModelsDF.to_pickle(allDatapointsPath)
    print(f"Dataframe saved at: {allDatapointsPath}.")
    
    log_dataframe(allModelsDF)
