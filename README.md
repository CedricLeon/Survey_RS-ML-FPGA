# Survey RS-ML-FPGA
### Description
Context

### How to generate the preprocessed data for the Review
#### Get your Zotero information
Keys
#### Run the scripts
```bash
python ./notebooks/Review_ML-RS-FPGA/create_articles_df.py
python ./notebooks/Review_ML-RS-FPGA/create_datapoints_df.py -i data/Review_ML-RS-FPGA/Dataframes/all_articles_<currentTime>.pkl -o data/Review_ML-RS-FPGA/Dataframes/all_datapoints.pkl
```
You can also force the naming of the first scripts with `-i  all_articles.pkl` for example.
#### Use the notebooks
Then you should be able to just run all the notebooks as you like.
If you updated the file names, make sure to update the `pickleName` variable at the beginning.
