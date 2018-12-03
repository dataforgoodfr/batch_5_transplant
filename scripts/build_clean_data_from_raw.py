import os
import glob
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from transplant.config import PATH_DYNAMIC_RAW, PATH_DYNAMIC_CLEAN,\
    PATH_STATIC_RAW, PATH_STATIC_CLEAN


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
        dfs.append(pd.read_excel(path, skiprows=[2]))
    return pd.concat(dfs, sort=True)


def clean_dynamic_raw(df, df_static):
    '''Clean dynamic raw DataFrame'''
    # Rename some columns
    df = df.rename(columns={'Unnamed: 0': 'id_patient', 'Unnamed: 1': 'time'})
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # Change column order: put [id_patient, time] at first
    df = df.set_index(['id_patient', 'time']).reset_index()

    # Drop corrupted or useless data
    col_to_drop = [col for col in df.columns if col.startswith('Unnamed:')]
    df = df.drop(columns=col_to_drop)
    df = df.dropna(subset=['id_patient'])  # drop rows with nan in id_patient
    df = df[~df.id_patient.isin(PATIENT_TO_DROP)]

    # Format dtypes
    df['id_patient'] = df['id_patient'].astype(int)

    # Convert time column to a real datetime.
    # We need to join df_static to retrieve the date and apply
    # a correction if the timestamps pass through midnight
    df = df.merge(df_static[['id_patient', 'date_transplantation']])
    df['time'] = pd.to_datetime(
        df['date_transplantation'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])
    df = df.groupby('id_patient').apply(correct_date_shift)
    df = df.drop(columns=['date_transplantation'])

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

    # Replace wrong dates in date_sortie_bloc by NaNs
    df_static.loc[df_static['date_sortie_bloc'] < datetime(2000, 1, 1),
                  'date_sortie_bloc'] = np.NaN

    # Format dtypes
    df['id_patient'] = df['id_patient'].astype(int)
    df['Survival_days_27_10_2018'] = \
        df['Survival_days_27_10_2018'].astype(int)

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
