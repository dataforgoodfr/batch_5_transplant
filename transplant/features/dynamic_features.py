import pandas as pd
import json
import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from transplant.config import (TRESHOLD_JSON_TS)


class time_serie_fX:
    """
   Compute features on TS for the dynamic dataset
    Input :
      - df [pandasdataframe]: dynamic Dataset
   Output :
      - df [pandas dataframe], with  new features (with prefix)

   """

    def __init__(self, df):
        self.df = df

    def treshold_fX(self, treshold_json=TRESHOLD_JSON_TS):

        for i in treshold_json.keys():

            tjson = treshold_json[i]
            name_new_feature = i
            serie = self.df[i]
            cond1 = ((serie >= tjson["etendue"][0]) & (serie < tjson["normalite"][0]))

            cond2 = (serie <= tjson["etendue"][1]) & (serie > tjson["normalite"][1])

            self.df[i + "_abnormal_treshFx"] = np.where(cond1 | cond2,  1, 0)

            self.df[i + "_clean_treshFx"] = np.where((serie >= tjson["etendue"][0])
                                             & (serie <= tjson["etendue"][1]), 1, 0)
