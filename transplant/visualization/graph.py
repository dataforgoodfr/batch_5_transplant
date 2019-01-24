import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot



def plot_dynamic_features(df, id_patient, features_list, display_declampage=False):
    """
    Plot a dynamic graph of patient from medical measuring instrument.
    Work only in notebook.
    Display only numerical features
    
    Input : 
        - df [DataFrame] : Muse have features [['id_patient', 'time']]
        - id_patient [int] : Id patient
        - features_list [list] : list of features you want to analyse
        
    Ouput : 
        - Display a plotly graph
    """
    
    init_notebook_mode(connected=True)
    
    # Check params
    
    if not isinstance(features_list, list):
        raise Exception("""'features_list' must be a list. \n Example features_list=['FC', 'FIN2O'] 
              ou \n features_list=DYNAMIC_CATEGORIES['neurology'])""")
    
    if not isinstance(id_patient, int):
        raise Exception("""'id_patient' must be a int. \n Example id_patient=314""")
    
    data = df[df['id_patient'] == id_patient]
    
    if display_declampage == True:
        # Check if there is a declampage_cote1 event
        if data.declampage_cote1_done.nunique() > 1: 
            date_declampage_1 = data[data['declampage_cote1_done'] == 1]['time'].min()
            declampage_features = [date_declampage_1]
        # Check if there is a declampage_cote2 event
        if data.declampage_cote2_done.nunique() > 1: 
            date_declampage_2 = data[data['declampage_cote2_done'] == 1]['time'].min()
            declampage_features = [date_declampage_1, date_declampage_2]
    
    if len(data) ==0:
        raise Exception("""No data for this id_patient""")
    
    
    try:
        time = data['time']
    except:
        raise Exception("""DataFrame need to have time feature ('time')""")
    
    if len(features_list) != 0:
        
        # Init list of trace
        data_graph = []
        
        # Remove nonusefull features
        features_list = [feature for feature in features_list if feature not in(['time', 'id_patient'])]
        
        # Take only numerical features
        features_list_clean = []
        for feature in features_list:
            if is_numeric_dtype(df[feature]):
                features_list_clean.append(feature)
                
        if len(features_list_clean) == 0:
            raise Exception("""No numeric data is this DataFrame""")
        
        # Create trace for data_graph
        max_y_value = 0 # Looking for max Y value
        for feature in features_list_clean:
            trace = go.Scatter(x=time,
                        y=data[feature].values,
                        name = feature,
                        yaxis='y1')
            data_graph.append(trace) 
            
            if max_y_value < data[feature].max():
                max_y_value = data[feature].max()
    else:
        raise Exception("""No data for this id_patient""")
        
    # Design graph
    layout = dict(
        title='Analyse du patient ' + str(id_patient),
        xaxis=dict(
            rangeslider=dict(
                visible = True
            ),
            type='date'
        ),
        yaxis=dict(
            title='Mesures'
        )
    )
    
    if display_declampage == True:
        shapes = []
        for i in range(0, len(declampage_features)):
            shapes.append({
                            'type': 'line',
                            'x0': declampage_features[i],
                            'y0': 0,
                            'x1': declampage_features[i],
                            'y1': max_y_value,
                            'line': {
                                'color': 'black',
                                'dash' : 'dot',
                                'width': 2}
            })
        layout['shapes'] = shapes
    
    fig = dict(data=data_graph, layout=layout)
    iplot(fig)

def plot_compare_patient(df, feature_to_analyse, patient_list):
    """
    Plot a dynamic graph to compare patient on One feature
    Work only in notebook.
    Display only numerical features
    
    Input : 
        - df [DataFrame] : Muse have features [['id_patient']]
        - feature_to_analyse [string] : Name of numerical feature
        - patient_list [list] : list of patient you want to compare
        
    Ouput : 
        - Display a plotly graph
    """
    
    init_notebook_mode(connected=True)
    
    # Check params
    
    if not isinstance(feature_to_analyse, str):
        raise Exception("""feature_to_analyse muse be a string - Example 'ETCO2' """)
        
    if feature_to_analyse not in df.columns:
        raise Exception("""feature_to_analyse is not in the DataFrame""")
        
    if not is_numeric_dtype(df[feature_to_analyse]):
        raise Exception("""feature_to_analyse must be numeric""")
    
    if not isinstance(patient_list, list):
        raise Exception("""'patient_list' must be a list - Example [304, 305, 405]""")
    
    
    data = df[df['id_patient'].isin(patient_list)]
    
    if len(data) ==0:
        raise Exception("""No data for these patients""")
    
    # Init list of trace
    data_graph = []
    
    for patient in patient_list:
        data_temp = data[data['id_patient'] == patient].copy()
        if len(data_temp) == 0:
            pass
        
        trace = go.Scatter(x=data_temp.reset_index(drop=True).index,
                            y=data_temp[feature_to_analyse].values,
                            name = str(patient),
                            yaxis='y1')
        data_graph.append(trace)
    # Design graph
    layout = dict(
        title='Comparaison de patient sur la mesure ' + feature_to_analyse,
        xaxis=dict(
            rangeslider=dict(
                visible = True
            ),
        ),
        yaxis=dict(
        title='Mesure'
        )
    )

    fig = dict(data=data_graph, layout=layout)
    iplot(fig)

def plot_analyse_factory(df, pca, hue=False, kmean=None):
    """
    Plotting result from tools.analyse_factory.analyse_factory()

    Input : 
        - df [DataFrame] : Muse have features [['id_patient']]
        - pca [sklearn.decomposition.PCA] : PCA already fit
        - hue [Bool] : Using cluster to plot differents colors
        - kmean [sklearn.kmean] : Kmean already fit. hue must be True
        
    Ouput : 
        - Display a plotly graph
    """
    
    init_notebook_mode(connected=True)

    color_list = ['#6ac1a5', '#fa8d67', '#8ea1c9']
    
    pca_expl = round(pca.explained_variance_ratio_[0:2].sum(), 2)
    
    if hue == False:
        # Create a trace
        trace = go.Scatter(
            x = df['pca_1'].values,
            y = df['pca_2'].values,
            mode = 'markers',
            text=df["id_patient"].tolist()
        )

        data = [trace]
    else:
        data = []
        for cluster in sorted(df['cluster'].unique()):
            df_temp = df[df['cluster'] == cluster]
            trace = go.Scatter(x = df_temp['pca_1'].values,
                                y = df_temp['pca_2'].values,
                                mode = 'markers',
                                marker=dict(color=color_list[cluster]),
                                name = 'cluster_'+str(cluster),
                                text=df_temp["id_patient"].tolist()
                              )
            data.append(trace) 

        if kmean:

            centroids = kmean.cluster_centers_
            center = go.Scatter(x=centroids[:, 0],
                                y=centroids[:, 1],
                                showlegend=False,
                                mode='markers', 
                                text='centroid',
                                marker=dict(
                                        size=10,
                                        opacity = 0.4,
                                        symbol=17,
                                        color='black'))
            data.append(center)
    
    # Design graph
    layout = dict(
        title='Analyse de feature PCA explain (first 2 components) : ' + str(pca_expl),
        height=400,
        #colorscale='Set3',
        xaxis=dict(
            title='pca_1'
        ),
        yaxis=dict(
            title='pca_2'
        )
    )
    
    fig = dict(data=data, layout=layout)
    iplot(fig)