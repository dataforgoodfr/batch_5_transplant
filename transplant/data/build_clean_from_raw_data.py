import os
import glob
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from transplant.config import PATH_DYNAMIC_RAW, PATH_DYNAMIC_CLEAN,\
    PATH_STATIC_RAW, PATH_STATIC_CLEAN, DYNAMIC_HEADERS


PATIENT_TO_DROP = [
    405  # Missing data for static vars:  Survival_days_27_10_2018 = 'xxx'
]


# Dynamic variables methods
#######################################
def load_dynamic_raw(path_dynamic_raw):
    '''Load raw files into one single DataFrame'''
    dfs = []
    paths_dynamic_raw = glob.glob(os.path.join(path_dynamic_raw, '*.xls'))
    assert(len(paths_dynamic_raw)) > 0,\
        'No files found in %s' % path_dynamic_raw
    for path in sorted(paths_dynamic_raw):
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
    # We assume that the header rows have at least 5 dynamic headers.
    header_idx = df[df.isin(DYNAMIC_HEADERS).sum(axis=1) > 5].index
    header_idx = list(header_idx) + [len(df)]  # Add last index

    # For each data bloc, extract "df_split" and update its columns
    # with the correct headers
    dfs = []
    for i in range(len(header_idx) - 1):
        df_s = df.loc[header_idx[i]: header_idx[i + 1] - 1].copy()
        df_s.columns = ['id_patient', 'time'] + df_s.iloc[0].tolist()[2:]
        df_s = df_s.loc[:, ~df_s.columns.isna()]  # Remove other NaN columns
        dfs.append(df_s.reset_index(drop=True))
    return dfs


def clean_dynamic_raw(df, df_static):
    '''Clean dynamic raw DataFrame'''
    # Rename some columns
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # Change column order: put [id_patient, time] at first
    df = df.set_index(['id_patient', 'time']).reset_index()

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
    df = df.merge(df_static[['id_patient', 'date_transplantation']])
    df['time'] = pd.to_datetime(
        df['date_transplantation'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])
    df = df.groupby('id_patient').apply(correct_date_shift)
    df = df.drop(columns=['date_transplantation'])

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
def load_static_raw(path_static_raw):
    '''Load raw files into one single DataFrame'''
    path_static_raw = glob.glob(os.path.join(path_static_raw, '*.xlsx'))
    assert len(path_static_raw) == 1, '%d file found in %s instead of 1'\
        % (len(path_static_raw), path_static_raw)

    df = pd.read_excel(path_static_raw[0], sheet_name='ensemble')
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


# Script
#######################################
if __name__ == '__main__':
    print('Building clean csv for static data...')
    df_static = load_static_raw(PATH_STATIC_RAW)
    df_static = clean_static_raw(df_static)
    df_static.to_csv(PATH_STATIC_CLEAN, index=False)

    print('Building clean csv for dynamic data...')
    df_dynamic = load_dynamic_raw(PATH_DYNAMIC_RAW)
    df_dynamic = clean_dynamic_raw(df_dynamic, df_static)
    df_dynamic.to_csv(PATH_DYNAMIC_CLEAN, index=False)

    print('GREAT SUCCESS!')
