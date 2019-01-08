import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

def analyse_feature_by_patient(df, feature):
    """
    Create a DataFrame groupby on id_patient.

    Aggregate feature on min / max / mean / median / std/ var / skew / 25 percent
    75 percent / 95 percent

    Input : 
      - df [DataFrame]
      - featute [string] - feature name
    """
    data = df.groupby('id_patient', as_index=False)[feature].agg({'min': 'min',
                                                              'max' : 'max',
                                                              'mean' : 'mean',
                                                              'median' : 'median',
                                                              'std' : 'std',
                                                              'var' : 'var',
                                                              'skew' : 'skew',
                                                              '25%' : lambda x: x.quantile(0.25),
                                                              '75%' : lambda x: x.quantile(0.75),
                                                              '95%' :  lambda x: x.quantile(0.95)
                                                             })
    return data

def create_pca_feature(feature_analysis):
    """
    
  	Use PCA to on feature_analysis DataFrame (from analyse_feature_by_patient() )

    If there is no data for a patient (NaN), filling by 0
  	Create 2 features on DataFrame
  		- pca_1 : pca 1
  		- pca_2 : pca 2

  	Input : 
  		- feature_analysis [DataFrame]
  	Output :
  		- feature_analysis [DataFrame]
  		- pca (fit PCA)
    """
    
    use_full_col = [col for col in feature_analysis.columns if col != 'id_patient']
    
    X = feature_analysis[use_full_col].copy()

    X.fillna(0, inplace=True)

    scaler = StandardScaler()
    X_scale = scaler.fit_transform(X)
    
    pca = PCA(n_components=0.9)
    X_pca = pca.fit_transform(X_scale)

    feature_analysis['pca_1'] = X_pca[:,0]
    feature_analysis['pca_2'] = X_pca[:,1]
    
    return feature_analysis, pca, X_pca


def create_cluster(feature_analysis, X_pca):
    """

    """

    kmean = KMeans(n_clusters=3, random_state=2018)
    kmean.fit(X_pca)

    feature_analysis['cluster'] = kmean.labels_
    return feature_analysis, kmean


def run_pca(df, feature, cluster=False):
    """
	  Call analyse_feature_by_patient & create_pca_feature

	   Input : 
		   - df [DataFrame]
		    - featute [string] - feature name
        - cluster [Bool] - Create cluster
	   Ouput : 
		    - feature_analysis [DataFrame]
  		- pca (fit PCA)
	 """
    feature_analysis = analyse_feature_by_patient(df, feature)
    feature_analysis, pca, X_pca = create_pca_feature(feature_analysis)
    if cluster==True:
        feature_analysis, kmean = create_cluster(feature_analysis, X_pca)
        return feature_analysis, pca, X_pca, kmean
    else:
      return feature_analysis, pca, X_pca

