import pandas as pd
from config.config import *
from parser import Parser
from tqdm import tqdm
import time

parser = Parser()

# Uploading Excel files
files = parser.upload_xls_files()
print("Found {} files ... ".format(len(files)))
print(files)

print('Importing and cleaning Excel files ...')
time.sleep(0.5)

clean_filename = '{}clean_bloc_file.csv'.format(DATA_CLEAN)
df_clean_output = pd.concat([parser.read_xls_files(file) for file in tqdm(files)])

print('Exporting clean file in  {}...'.format(DATA_CLEAN))
df_clean_output.to_csv(clean_filename)

print('Creating the data model in {}...'.format(DATA_MODEL))
# Create data model
parser.split_fact_tables(clean_filename)