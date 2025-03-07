# Survey RS-ML-FPGA
### Description
Context

### How to generate the preprocessed data for the Review
#### Get your Zotero information
If you want to use similar logic and use `explore_zotero_API.ipynb`, you will need to store your Zotero API Key in this file `src/.keys`. It should have a similar format:
```json
Zotero API Key: <your_api_key>
```
Collection keys
#### Run the scripts
```bash
python ./src/Zotero_data_processing/create_articles_df.py
python ./src/Zotero_data_processing/create_datapoints_df.py -i data/Dataframes/all_articles_<currentTime>.pkl -o data/Dataframes/all_datapoints.pkl
```
You can also force the naming of the first scripts with `-i  all_articles.pkl` for example.
`create_datapoints_df.py` can also be run with different verbose levels (`-v`, `-vv`, or `-vvv`) to see more details.
#### Use the notebooks
Then you should be able to just run all the notebooks as you like.
If you updated the file names, make sure to update the `pickleName` variable at the beginning.
