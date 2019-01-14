import os
import sys
import glob
import hashlib
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from transplant.config import PATH_DYNAMIC_RAW, PATH_DYNAMIC_CLEAN,\
    PATH_STATIC_RAW, PATH_STATIC_CLEAN, RAW_DYNAMIC_HEADERS, PATTERNS_RAW


PATIENT_TO_DROP = [
    405  # Missing data for static vars:  Survival_days_27_10_2018 = 'xxx'
]


# Dynamic variables methods
#######################################
def load_dynamic_raw(dir_raw, file_pattern):
    '''Load raw files into one single DataFrame'''
    dfs = []
    paths_raw = sorted(glob.glob(os.path.join(dir_raw, file_pattern)))
    if len(paths_raw) == 0:
        raise FileNotFoundError('No files found in %s with file pattern %s'
                                % (dir_raw, file_pattern))
    for path in paths_raw:
        df = pd.read_excel(path, header=None)       # header=None is crucial...
        dfs += split_dynamic_raw_multiple_blocs(df)  # ...for this method
    return pd.concat(dfs, axis=0, ignore_index=True, sort=True)


def split_dynamic_raw_multiple_blocs(df):
    """Split multiple data blocs of a raw Bloc*D4G.xls file loaded
    into a dataframe.

    If you look carefully, you can see that many Bloc*D4G.xls files have
    multiple header rows inside the file followed by new blocs of data...
    ...and the terrible thing is that sometimes the new header is not
    even aligned with the other ones...

    This method simply splits the dataframe into new dataframes with
    proper headers.
    """
    # Detect dynamic header indexes
    def get_header_indexes(min_header):
        return df[df.isin(RAW_DYNAMIC_HEADERS).sum(axis=1) >= min_header].index
    header_idx = get_header_indexes(1)
    # Check: we ensure that it is exactly the same thing to detect the headers
    # looking for at least 1 DYNAMIC_HEADERS or 6 in a row. We choose 6 because
    # the header row with the minimum number of RAW_DYNAMIC_HEADERS was found
    # in Bloc8D4G.xls and has 6 headers. If the check fails, a false positive
    # might have been detected (ex: text cell with a RAW_DYNAMIC_HEADERS).
    assert header_idx.equals(get_header_indexes(6)), "Failed to detect headers"
    # Add last index
    header_idx = list(header_idx) + [len(df)]

    # For each data bloc, extract "df_split" and update its columns
    # with the correct headers
    dfs = []

    for i in range(len(header_idx) - 1):
        df_s = df.loc[header_idx[i]: header_idx[i + 1] - 1].copy()
        df_s.columns = ['id_patient', 'time', 'date', 'foreign_key'] + \
            df_s.iloc[0].tolist()[4:]
        df_s = df_s.loc[:, ~df_s.columns.isna()]  # Remove other NaN columns
        dfs.append(df_s.reset_index(drop=True))
    return dfs


def clean_dynamic_raw(df, df_static):
    '''Clean dynamic raw DataFrame'''
    # Rename some columns
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # Change column order: put [id_patient, time] at first
    df = df.set_index(['id_patient', 'time', 'date', 'foreign_key']). \
        reset_index()

    # Drop corrupted or useless data
    col_to_drop = [col for col in df.columns if col.startswith('Unnamed:')]
    df = df.drop(columns=col_to_drop)
    df = df.dropna(subset=['id_patient', 'time'])
    df = df[~df.id_patient.isin(PATIENT_TO_DROP)]

    # Format dtypes
    df = cast_integers(df)

    # Convert time column to a real datetime.
    # We need to join df_static to retrieve the date and apply
    # a correction if the timestamps pass through midnight
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    df['time'] = pd.to_datetime(
        df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])
    df = df.drop(columns=['date', 'foreign_key'])

    # Checks
    assert (df.id_patient.dtypes == 'int'),\
        "TypeError: Inconsistency in parsed dynamic data: id_patient not int"

    return df


def correct_date_shift(x):
    idx_0h = (x['time'] - x['time'].shift(1)) < timedelta(days=0)  # 0h indexes
    for i in idx_0h.index[idx_0h]:  # loop over all 0h index
        x['time'].loc[i:] = x['time'].loc[i:] + timedelta(days=1)
    return x


# Static variables methods
#######################################
def load_static_raw(dir_raw, file_pattern):
    '''Load raw files into one single DataFrame'''
    paths_raw = glob.glob(os.path.join(dir_raw, file_pattern))
    # Check that there is only one file
    if len(paths_raw) != 1:
        files = [os.path.basename(p) for p in paths_raw]
        print("\nERROR: this script supports only 1 static file, but %d file"
              "(s) were found in %s with file pattern %s: %s"
              % (len(paths_raw), file_pattern, dir_raw, files))
        sys.exit(1)

    df = pd.read_excel(paths_raw[0], sheet_name='ensemble')
    return df


def clean_static_raw(df):
    '''Clean static raw DataFrame'''
    # Rename some columns
    df = df.rename(columns={'numero': 'id_patient'})
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # Drop corrupted or useless data
    df = df.dropna(subset=['id_patient'])  # drop rows with nan in id_patient
    df = df[~df.id_patient.isin(PATIENT_TO_DROP)]

    # Replace null values (date 1900, NF, etc.) by NaNs
    df.loc[df['date_sortie_bloc'] < datetime(2000, 1, 1),
           'date_sortie_bloc'] = np.NaN
    df.replace({'NF': np.NaN}, inplace=True)

    # Format dtypes
    df = cast_integers(df)

    return df


# Common methods
#######################################
def cast_integers(df):
    """Try to cast all columns of a DataFrame to integer"""
    for col in df.columns:
        try:
            if (df[col].astype(int) == df[col]).all():
                df[col] = df[col].astype(int)
        except (ValueError, TypeError):
            pass
    return df


def get_hash_raw_and_build_clean():
    """ Get the md5sum of all the raw files + the current python
    file (__file__)."""
    # Get paths
    dir_raws = os.path.realpath(os.path.join(PATH_STATIC_RAW, '../'))
    paths_raws = glob.glob(os.path.join(dir_raws, '*/*'))
    paths_files_to_hash = paths_raws + [os.path.realpath(__file__)]

    # Hash!
    md5 = hashlib.md5()
    for path in paths_files_to_hash:
        with open(path, 'rb') as f:
            md5.update(f.read())
    return md5.hexdigest()


# Script
#######################################
if __name__ == '__main__':
    print('Building clean csv for static data...')
    df_static = load_static_raw(PATH_STATIC_RAW, PATTERNS_RAW["static"])
    df_static = clean_static_raw(df_static)
    df_static.to_csv(PATH_STATIC_CLEAN, index=False)

    print('Building clean csv for dynamic data...')
    df_dynamic = load_dynamic_raw(PATH_DYNAMIC_RAW, PATTERNS_RAW["dynamic"])
    df_dynamic = clean_dynamic_raw(df_dynamic, df_static)
    df_dynamic.to_csv(PATH_DYNAMIC_CLEAN, index=False)

    print('GREAT SUCCESS!')
