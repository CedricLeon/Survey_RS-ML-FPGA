from pyzotero import zotero
import pandas as pd

import argparse
from pathlib import Path
from tqdm import tqdm
import datetime
import sys
import os

# Append the parent directory (which contains utils/) to the Python path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.utils import get_total_in_dict_of_lists, parse_string_to_dict


def initialize_zotero_API(libraryID: str, libraryType: str) -> zotero.Zotero:
    currentDir = Path(__file__).parent
    api_key = open(currentDir / ".keys").read().split(":")[1].strip()
    return zotero.Zotero(libraryID, libraryType, api_key)

def get_all_articles_in_collection(zoteroAPI: zotero.Zotero, collectionKey: str) -> list:
    # Add search paprameters to select only conference papers and journal articles
    # /!\ Ideally I just want to NOT select notes and attachments, but I did not find the API syntax to do so
    zoteroAPI.add_parameters(itemType="conferencePaper || journalArticle")
    # Fetch all the items in the library (Without the limitation of 100 items per request)
    items = zoteroAPI.everything(zoteroAPI.collection_items(collectionKey))
    print(f"{len(items)} items fetched from collection {collectionKey}.")
    return items

def filter_screened_articles(articlesInCollection: list) -> tuple[list, dict]:
    exclusionCriteria = {}
    keysArticlesInSurvey = []
    for item in tqdm(articlesInCollection):
        # Print the item's title and type
        # print(f"{r}{item['data']['itemType']}{e}")
        # print(f" - {b}{item['data']['title']}{e}")
        # print(f'Item Type: {item["data"]["itemType"]} | Key: {item["data"]["key"]}')

        tags = item["data"].get("tags", [])
        isExcluded = False
        for tag in tags:
            tag = tag["tag"] # Each Zotero tag is a dictionary with a "tag" key
            if tag.startswith("Excluded: "):
                if tag not in exclusionCriteria:
                    exclusionCriteria[tag] = []

                exclusionCriteria[tag].append(item["data"]["key"])
                isExcluded = True
                break

        if not isExcluded:
            keysArticlesInSurvey.append(item["data"]["key"])
    return keysArticlesInSurvey, exclusionCriteria

def fetch_articles_data(zoteroAPI: zotero.Zotero, keys: list[str]) -> pd.DataFrame:
    """_summary_
    Get the title, DOI, URL, abstract, date, item type and citation key, as well the list of authors and tags of each article which key is in the provided list.

    Args:
        zoteroAPI (zotero.Zotero): The Zotero API where to get the articles
        keys (list[str]): List of keys of the articles to fetch

    Returns:
        Dataframe: A DataFrame containing each article's: title, DOI, URL, abstract, date, item type and citation key, as well the list of authors and tags
    """
    articlesData = []
    print(f"Fetching data for {len(keys)} articles...")

    for key in tqdm(keys):
        data = zoteroAPI.item(key)["data"]

        title = data.get("title", "")
        doi = data.get("DOI", "")
        url = data.get("url", "")
        abstractNote = data.get("abstractNote", "")
        date = data.get("date", "")
        itemType = data.get("itemType", "")
        extra = parse_string_to_dict(data.get("extra", ""))

        # print(f" Extracting \"{extra['Citation Key']}\"...")

        # If KeyError: 'firstName', it's likely Zotero imported the publisher, e.g. "IEEE", as an author.
        # To solve that, I usually switch it to "Editor" or delete it in Zotero.
        authorsList = [
            f"{author['firstName']} {author['lastName']}"
            for author in data.get("creators", [])
            if author["creatorType"] == "author"
        ]

        tags = [tag["tag"] for tag in data.get("tags", [])]

        articlesData.append(
            {
                "BBT Citation Key": extra["Citation Key"],
                "Title": title,
                "List": authorsList,
                "DOI": doi,
                "URL": url,
                "Tags": tags,
                "Abstract Note": abstractNote,
                "Date": date,
                "Item Type": itemType,
                "Zotero Key": key,
            }
        )

    df = pd.DataFrame(articlesData)
    df.set_index("BBT Citation Key", inplace=True)

    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Save articles data from the Zotero API to a DataFrame.")
    parser.add_argument("--collection", "-c", type=str, help="Key of the Zotero collection where to get the articles.")
    parser.add_argument("--output", "-o", type=str, help="Output path for the pickle file.")
    args = parser.parse_args()

    # Initialize the API
    groupLibraryID = "5602981"
    userLibraryID = "8968938"
    zoteroAPI = initialize_zotero_API(groupLibraryID, "group")
    # Key of the group "2. Studies included in review" collection: 'PEWYQYGG'
    zoteroCollectionKey = args.collection if args.collection else 'PEWYQYGG'

    # Paths to save Dataframes
    if args.output:
        allArticlesPath = Path(args.output)
        allArticlesPath.parent.mkdir(parents=True, exist_ok=True)
    else:
        allDfPaths = Path(__file__).parent.parent.parent / "data" / "Dataframes"
        allArticlesPath = allDfPaths / f"all_articles_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pkl"
    
    articlesInCollection = get_all_articles_in_collection(zoteroAPI, zoteroCollectionKey)

    # Each article excluded by the screening process was tagged with the corresponding Exclusion Criteria
    keysArticlesInSurvey, exclusionCriteria = filter_screened_articles(articlesInCollection)

    totalNbExcluded = get_total_in_dict_of_lists(exclusionCriteria)
    print(f"Total number of items excluded: {totalNbExcluded}.")
    for tag, keys in exclusionCriteria.items():
        print(f' -  {len(keys):>3} items excluded for: "{tag[10:]}"')

    print(f"{totalNbExcluded} excluded items + {len(keysArticlesInSurvey)} selected for review" \
          f" = {len(articlesInCollection)} total items in the review collection")
    assert totalNbExcluded + len(keysArticlesInSurvey) == len(articlesInCollection)

    # Fetch the data and create a DataFrame
    allArticlesDF = fetch_articles_data(zoteroAPI, keysArticlesInSurvey)
    allArticlesDF.to_pickle(allArticlesPath)
    print(f"The data of the screened articles was pickled and saved here: {allArticlesPath}.")
    # print(articlesDF)
