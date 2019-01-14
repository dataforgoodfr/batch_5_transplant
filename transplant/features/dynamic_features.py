import pandas as pd
import json
import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


class ts_extraction:
	"""
	Compute features on TS for the dynamic dataset

	Input :
		- df, dynamic Dataset
	Output :
		- df, with  new features (prefix _tresh)

	"""
	def __init__(self, df):
		self.df = df

	def f_treshold(self, treshold_json):

		for i in treshold_json.keys():

 			tjson = treshold_json[i]
 			name_new_feature = i
 			serie = self.df[i]
 			cond1 = (serie >= tjson["etendue"][0] ) & (serie < tjson["normalite"][0])
 			cond2 = (serie <= tjson["etendue"][1] ) & (serie > tjson["normalite"][1])

 			self.df[i + "_abnormal_tresh"] = np.where(cond1 | cond2,  1, 0)
 			self.df[i + "_clean_tresh"] = np.where((serie >= tjson["etendue"][0]) & (serie <= tjson["etendue"][1] ),  1, 0)
 			self.df[i + "_normal_tresh"] = np.where((serie >= tjson["normalite"][0]) & (serie <= tjson["normalite"][1] ),  1, 0)
 			self.df[i + "_dirty_tresh"] = np.where((serie <= tjson["etendue"][0]) & ( serie >= tjson["etendue"][1] ),  1, 0)

	def plot_tresh(self, treshold_json ,id_patient = 100, var = "Pmean", title = '') :


		serie = self.df[self.df.id_patient == id_patient ][var]

		y = serie.values
		x = serie.reset_index().index

		fig, ax, = plt.subplots(1, 1, sharex=True)
		ax.plot(x, y , color='black')

		cond1 =  (y <= treshold_json[var]["normalite"][0])
		cond2 = (y >= treshold_json[var]["normalite"][1])

		ax.fill_between(x, y, treshold_json[var]["normalite"][0],  where = cond1, facecolor='red', interpolate=True)
		ax.fill_between(x, y, treshold_json[var]["normalite"][1],  where = cond2, facecolor='red', interpolate=True)
		ax.set_title(title)
		plt.show()
