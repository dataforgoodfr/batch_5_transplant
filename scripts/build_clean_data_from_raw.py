import os
import glob
import pandas as pd
from transplant.config import PATH_DYNAMIC_RAW, PATH_DYNAMIC_CLEAN, PATH_STATIC_RAW, PATH_STATIC_CLEAN


# Dynamic variables methods
#######################################
def load_dynamic_raw(path_dynamic_raw):
    '''Load raw files into one single DataFrame'''
    dfs = []
    paths_dynamic_raw = glob.glob(os.path.join(path_dynamic_raw, '*.xls'))
    assert(len(paths_dynamic_raw)) > 0,\
        'No files found in %s' % path_dynamic_raw
    for path in sorted(paths_dynamic_raw):
        dfs.append(pd.read_excel(path, skiprows=[2]))
    return pd.concat(dfs, sort=True)


def clean_dynamic_raw(df):
    '''Clean dynamic raw DataFrame'''
    # Rename some columns
    df = df.rename(columns={'Unnamed: 0': 'id_patient', 'Unnamed: 1': 'time'})
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # Change column order: put [id_patient, time] at first
    df = df.set_index(['id_patient', 'time']).reset_index()

    # Drop useless data
    col_to_drop = [col for col in df.columns if col.startswith('Unnamed:')]
    df = df.drop(columns=col_to_drop)
    df = df.dropna(subset=['id_patient'])  # drop rows with nan in id_patient

    # Format dtypes
    df['id_patient'] = df['id_patient'].astype(int)

    return df


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

    # Drop useless data
    df = df.dropna(subset=['id_patient'])  # drop rows with nan in id_patient

    # Format dtypes
    df['id_patient'] = df['id_patient'].astype(int)

    return df


# Script
#######################################
if __name__ == '__main__':
    print('Building clean csv for static data...')
    df = load_static_raw(PATH_STATIC_RAW)
    df = clean_static_raw(df)
    df.to_csv(PATH_STATIC_CLEAN, index=False)

    print('Building clean csv for dynamic data...')
    df = load_dynamic_raw(PATH_DYNAMIC_RAW)
    df = clean_dynamic_raw(df)
    df.to_csv(PATH_DYNAMIC_CLEAN, index=False)

    print('GREAT SUCCESS!')
