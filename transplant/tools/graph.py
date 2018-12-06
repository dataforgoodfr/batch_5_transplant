import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype

import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot



def plot_dynmatic_features(df, id_patient, features_list):
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
        for feature in features_list_clean:
            trace = go.Scatter(x=time,
                        y=data[feature].values,
                        name = feature,
                        yaxis='y1')
            data_graph.append(trace) 
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

    fig = dict(data=data_graph, layout=layout)
    iplot(fig)

