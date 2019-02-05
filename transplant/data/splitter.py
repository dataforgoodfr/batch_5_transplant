import pandas as pd


def get_post_last_declampage_data(df_dynamic, nb_min_chir=10):
    """
    Return dynamic value after last declampage.
    Dynamic's data are only for multi declampage operation.
    Features will be renamed as "NAME"+"_post"
    Input :
        - df_dynamic [DataFrame] : dynamic data
        - nb_min_chir [int] : Number of minute of last operation
            declampage. More minute is less data post declampage
    Return :
        - DataFrame : split of dynamic data
    """

    # Take only data where declampage 2 is already done
    declampage_df = \
        df_dynamic[df_dynamic['declampage_cote2_done'] == 1].copy()

    # Look for date of last declampage by patient
    date_last_declampage_by_patient = \
        declampage_df.groupby('id_patient', as_index=False)['time'].min()
    # Rename
    date_last_declampage_by_patient.columns = ['id_patient',
                                               'time_last_declampage']

    # Merge last date of declampage with data with 2 declampage
    declampage_df = declampage_df.merge(date_last_declampage_by_patient,
                                        on='id_patient')

    # Create a lag on date last declampage by patient
    declampage_df['time_last_declampage'] = \
        declampage_df['time_last_declampage'] + \
        pd.Timedelta(minutes=nb_min_chir)

    # select only post last declampage with a lag on time_last_declampage
    post_declampage_df = \
        declampage_df[declampage_df['time'] >=
                      declampage_df['time_last_declampage']].copy()

    # Drop non usefull columns
    post_declampage_df.drop(['time_last_declampage', 'declampage_cote1_done',
                             'declampage_cote2_done'], axis=1, inplace=True)

    # Renaming columns
    for col in post_declampage_df.columns:
        if col not in ['id_patient', 'time']:
            post_declampage_df.rename(columns={col: col+"_post"},
                                      inplace=True)

    return post_declampage_df


def get_pre_last_declampage_data(df_dynamic, duration=90):
    """
    Return dynamic value before last declampage
    Features will be renamed as "NAME"+"_pre"
    Input :
        - df_dynamic [DataFrame] : dynamic data
        - duration [int] : number of minute we take before last declampage.
            More duration is more data before last declampage.
            No data before first declampage.
    Return :
        - DataFrame : split of dynamic data
    """

    # First declampage_cote1_done is Done, Second is in preparation
    declampage_df = \
        df_dynamic[(df_dynamic['declampage_cote1_done'] == 1) &
                   (df_dynamic['declampage_cote2_done'] == 0)].copy()

    # Look for date of last declampage by patient
    date_last_declampage_by_patient = \
        declampage_df.groupby('id_patient', as_index=False)['time'].max()
    # Rename
    date_last_declampage_by_patient.columns = ['id_patient',
                                               'time_last_declampage']

    # Merge last date of declampage with data with 2 declampage
    declampage_df = declampage_df.merge(date_last_declampage_by_patient,
                                        on='id_patient')

    # Create a lag on date last declampage by patient (pre last declampage)
    declampage_df['time_last_declampage'] = \
        declampage_df['time_last_declampage'] - \
        pd.Timedelta(minutes=duration)

    # select only pre data on last declampage with a lag
    # on time_last_declampage
    pre_declampage_df = \
        declampage_df[declampage_df['time'] >=
                      declampage_df['time_last_declampage']].copy()

    # Drop non usefull columns
    pre_declampage_df.drop(['time_last_declampage', 'declampage_cote1_done',
                            'declampage_cote2_done'], axis=1, inplace=True)

    # Renaming columns
    for col in pre_declampage_df.columns:
        if col not in ['id_patient', 'time']:
            pre_declampage_df.rename(columns={col: col+"_pre"},
                                     inplace=True)

    return pre_declampage_df


def get_baseline_patient_data(df_dynamic, duration=90):
    """
    Return dynamic value before last declampage
    Input :
        - df_dynamic [DataFrame] : dynamic data
        - duration [int] : number of minute we take before last declampage.
            More duration is more data before last declampage.
            No data before first declampage.
    Return :
        - DataFrame : split of dynamic data
    """

    # Before first declampage
    declampage_df = df_dynamic[df_dynamic['declampage_cote1_done'] == 0]

    # Look for date of before 1st declampage
    date_before_declampage_by_patient = \
        declampage_df.groupby('id_patient',
                              as_index=False)['time'].max()
    # Rename
    date_before_declampage_by_patient.columns = ['id_patient',
                                                 'time_before_declampage']

    # Merge last date of declampage with data with 2 declampage
    declampage_df = declampage_df.merge(date_before_declampage_by_patient,
                                        on='id_patient')

    # Create a lag on date last declampage by patient (pre last declampage)
    declampage_df['time_before_declampage'] = \
        declampage_df['time_before_declampage'] - \
        pd.Timedelta(minutes=duration)

    # select only pre data on last declampage with a lag
    # on time_before_declampage
    baseline_data_df = declampage_df[declampage_df['time'] >=
                                     declampage_df['time_before_declampage']]

    return baseline_data_df


def make_split_operation(dynamic_df, baseline_duration=90,
                         pre_duration=90, post_chir_duration=20):
    """
    Split dynamic's data into 3 dataframe :
    - baseline_data_df : Before first declampage duration = baseline_duration
    - pre_declampage_df : Before second declampage duration = pre_duration
    - post_declampage_df : After seconde declampage nb_min_chir = post_chir_duration

    Input:
         - dynamic_df [DataFrame] : dynamic's data
         - baseline_duration : number of time between first line and first declampage
         - pre_duration : number of time between  first line and 2nd declampage
         - post_chir_duration : number of time of 2nd declampage operation.
                                More is less data.

    Ouput :
        - baseline_data_df [DatFrame]
        - pre_declampage_df [DatFrame]
        - post_declampage_df [DatFrame]
    """

    baseline_data_df = \
        get_baseline_patient_data(dynamic_df,
                                  duration=baseline_duration)
    pre_declampage_df = \
        get_pre_last_declampage_data(dynamic_df,
                                     duration=pre_duration)
    post_declampage_df = \
        get_post_last_declampage_data(dynamic_df,
                                      nb_min_chir=post_chir_duration)

    return baseline_data_df, pre_declampage_df, post_declampage_df
