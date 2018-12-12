import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import numpy as np
import seaborn as sns
from sklearn.decomposition import PCA        
import pandas as pd
import geopandas as gpd
import numpy as np
from geopandas.tools import sjoin
import folium
from folium.plugins import MarkerCluster
from folium import IFrame
import shapely
from shapely.geometry import Point
import unicodedata
import pysal as ps




class sanity_check(object): 
    
    def __init__(self, data): 
        self.data = data
        self.numeric_features = self.data.dtypes[(self.data.dtypes == np.dtype(float)) | (self.data.dtypes == np.dtype(int))].index.values
        self.categoric_features = self.data.dtypes[(self.data.dtypes == np.dtype(object))].index.values
    
        
    def full_sc(self) : 
        self.title()
        self.meta_df()
        self.plot_nan_values()
    def title(self):
        display(HTML("<center> <h1> Data quality  check </h1>"))
        
    def meta_df(self): 
        
        display(HTML("<h2> Metadata : </h2>"))
        
        print("the loaded dataset has  {} rows and {}".format(self.data.shape[0], self.data.shape[1]))
        
        display(HTML("<center> <h3> dataset sample </h3>"))
        display(HTML(self.data.head().to_html()))
        
        display(HTML("<center> <h3> columns type </h3>"))
        display(HTML(self.data.dtypes.reset_index().to_html()))
        
        display(HTML("<center> <h3> Full list of features </h3>"))
        display(list(self.data.columns))
                    

        
    def plot_nan_values(self):
        
        display(HTML("<h2> NaN Values : </h2>"))
        (self.data.isnull().sum(axis = 0)/len(self.data)).reset_index().sort_values(0, ascending = False).plot(x = "index" , kind = 'bar')
        plt.xticks(rotation=90)
        plt.title("NaN % for each feature")
        plt.show()
        
        display(HTML("<center> <h3>  </h3>"))
        display((self.data.isnull().sum(axis = 0)/len(self.data)).reset_index().sort_values(0, ascending = False)) 
        