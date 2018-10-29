import pandas as pd

# Read clean_bloc_files csv
data = pd.read_csv('../data/clean_data/clean_bloc_files.csv')

data.columns = map(str.lower, data.columns)
data.columns = data.columns.str.replace(' ', '_')
data.columns = data.columns.str.replace('(', '_')
data.columns = data.columns.str.replace(')', '')
data.columns = data.columns.str.replace('.', '')

# Map columns to each fct group

neurology = [
    'id_patient', 'time', 'bis', 'bis sr',
    'et_des', 'et_sevo', 'nmt_tof', 'nmtratio'
    ]
haemodynamic = [
    'id_patient', 'time', 'dc', 'fc', 'papdia',
    'papmoy', 'papsys', 'pasd', 'pasm', 'pass', 'pnid', 'pnim', 'pnis'
    ]
respiratory = [
    'id_patient', 'time', 'etco2', 'eto2', 'fico2', 'fin2o', 'fio2', 'fr',
    'fr_ecg', 'mac', 'peeptotal', 'pmax', 'pmean', 'pplat', 'rr_co2',
    'spo2', 'svo2__m', 'vt'
    ]
temperature = ['id_patient', 'time', 'temp']

map_fields = {
    'neurology': neurology,
    'haemodynamic': haemodynamic,
    'respiratory': respiratory,
    'temperature': temperature
    }

for name, array in map_fields.items():
    df = data[data.columns.intersection(array)]
    filename = '../data/clean_data/model/fct_{}.csv'.format(name)
    df.to_csv(filename)
