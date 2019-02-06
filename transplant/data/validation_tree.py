import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta

from transplant.data.dataset import Dataset

from transplant.config import (PATH_STATIC_CLEAN, PATH_DYNAMIC_CLEAN,
                               STATIC_CATEGORIES, DYNAMIC_HEADERS)

from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

class Validation:

    ###########
    # Dataset #
    ###########

    def __init__(self, time_offset=30):
        self.time_offset = time_offset

    def get_static(self):
        data = pd.read_csv(PATH_STATIC_CLEAN)
        
        # Drop patient with other_organ_transplantation
        data = data[data.other_organ_transplantation == 0]
        
        # Drop patient with only 1 declampage
        list_patient_1_declampage = data[data.Heure_declampage_cote2.isna()]['id_patient'].unique()
        
        data = data[~data.id_patient.isin(list_patient_1_declampage)]
        dynamic = self.get_dynamic()
        
        data = data[data.id_patient.isin(dynamic['id_patient'])]
        data.reset_index(inplace=True)
        
        return data
    def get_dynamic(self):

        dataset = Dataset()
        data = pd.read_csv(PATH_DYNAMIC_CLEAN, parse_dates=['time'])
        # create bool event on declampage using Dataset function
        data = dataset._get_declampage_event(data)
        # Truncate dynamic file to time_offset before end of operation
        data = data.groupby('id_patient').apply(self._truncate_datetime).reset_index(drop=True)

        return data

    def get_static_id(self, data, id_):

        data = data[data.id_patient==id_]
        return data

    def get_dynamic_id(self, data, id_):

        data = data[data.id_patient==id_]
        return data

    def _truncate_datetime(self, df):
        date_max = df.time.max() - timedelta(minutes=self.time_offset)
        return df[df.time <= date_max]

    #####################
    # General functions #
    #####################

    def get_end_surgery_data_dynamic(self, data, time=15, period=15) : 
        
        """
        Function to apply to the dynamic dataset
        Allow us to focus on what happens *time* minutes after the second declampage is done, 
        during a *period* minutes interval
        Return a dynamic dataset with *period* rows
        """
        date_1 = data[data.declampage_cote2_done==1].time.min() + timedelta(minutes=time)
        date_2 = date_1 + timedelta(minutes=period)
        return data[(data.time >= date_1)&(data.time <= date_2)]

    
    def is_nan(self, data, column, threshold=0.8):
        """
        Function that verifies if more than threshold% of our values are nan
        return True if nan else False
        """
        if data[column].isnull().sum()/len(data[column]) > threshold:
            return True
        return False

    def Sufficient_decline(self, value_at_declampage_2, value_at_fermeture, regle_nan, decline=1/3, epsilon = 0.1):
        """
        For  several tests we will need to know if the levels of a variable decline enough over time.
        For instance, a variable must decrease at least about 1/3 of its value from declampage_2 to fermeture to pass a test
        ie : [value at declampage_2]-[value at fermeture] > 1/3*[value at declampage_2]

        This function test if the decline of a value between the event 'declampage_cote_2' and 'fermeture' is sufficient
        - decline : fraction / [value at declampage_2]-[value at fermeture] > decline*[value at declampage_2]
        - epsilon : "nearly equal"

        return boolean
        """
        if np.isnan(value_at_fermeture) or np.isnan(value_at_declampage_2):
            return regle_nan
        if value_at_fermeture > value_at_declampage_2:
            return False
        delta = value_at_declampage_2 - value_at_fermeture
        if delta > decline*value_at_declampage_2:
            return True
        return np.abs(delta - decline*value_at_declampage_2)<= epsilon



    #################################################################################
    # Test functions used in the ECMO Weaning Test, INO Weaning Test or Niv attempt #
    #################################################################################

    def test_PASm_sup(self, data_dynamic_id_end, regle_nan, obj=60, threshold=85,):
        """
        Test if threshold% of our value (PASm) is > objective /do not take into account PASm = 0
        Return boolean
        True : "at the end of surgery, when PASm not equal 0, at least 90% of the values are > 60"
        """
        non_zeros = data_dynamic_id_end['PASm'][data_dynamic_id_end['PASm']>0].count() 
        nb_ok = data_dynamic_id_end['PASm'][data_dynamic_id_end['PASm']>=obj].count()
        
        if self.is_nan(data=data_dynamic_id_end, column='PASm', threshold=0.8) or non_zeros==0:
            #ne peut pas être negatif ou nul -> sinon problème dans les mesures
            return regle_nan
        
        return (nb_ok/non_zeros)*100>=threshold


    def test_noradrenaline(self, data_static_id, regle_nan, nora_max=1.5, nora_min=1):
        """
        Test if the noradrenaline is sufficiently low :
            > 1.5mg/h --> ko
            < 1mh/h --> ok
            between : see if there is a sufficient decline
        """
        if self.is_nan(data=data_static_id, column='NORAD_fermeture', threshold=0.8):
            return regle_nan
        elif data_static_id['NORAD_fermeture'].values[0] >= nora_max:
            return False
        elif data_static_id['NORAD_fermeture'].values[0] <= nora_min:
             return True
        else : 
            return self.Sufficient_decline(data_static_id['NORAD_declampage_cote_2'].values[0],
                                      data_static_id['NORAD_fermeture'].values[0], regle_nan,
                                      decline=1/3, epsilon = 0.1)

    def test_ratio_pao2_fio2(self, data_static_id, data_dynamic_id_end, obj, regle_nan, threshold=80):
        """
        Verify if the ratio PaO2/FiO2  is high enough
        True : PaO2/FiO2 ratio > obj
        """
        ratios = data_static_id['PaO2_fermeture'].values[0]/(data_dynamic_id_end['FiO2']/100)
        non_zeros = ratios[ratios>0].count()
        nb_ok = ratios[ratios>=obj].count()
        
        if ratios.isnull().sum()/len(ratios) > 0.8 or non_zeros==0:
            return regle_nan
        
        return (nb_ok/non_zeros)*100>=threshold


    def test_PAP_diminution(self, data_dynamic_id_end, regle_nan,  paps_max=50, paps_min=32):
        """
        True : If PAPS, PAPM, PAPD decrease, 
        att: lot of nan for  PAPm -> take PAPs
        """
        if self.is_nan(data=data_dynamic_id_end, column='PAPsys', threshold=0.8):
            return regle_nan
        
        #if the last measure are < paps_min
        if (data_dynamic_id_end.PAPsys.values[-5:]<=paps_min).all():
            return True
        elif(data_dynamic_id_end.PAPsys.values[-5:]>=paps_max).all():
            return False
        else :
            return data_dynamic_id_end.PAPsys.values[-1] < data_dynamic_id_end.PAPsys.values[0]
            #we compate with the value at declamapge_2
            #return Sufficient_decline(data_dyn.PAPsys.values[0],data_dyn.PAPsys.values[-1],decline=1/5, epsilon = 0.1)


    def test_augm_ratio_pao2_fio2(self, data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan, threshold_augm=0):
        """
        Test if ratio sufficiently high or sufficient evolution between the events 'declampage_cote_2' & 'fermeture'
        """
        data = self.get_end_surgery_data_dynamic(data_dynamic_id, time=0, period=10)
        if self.test_ratio_pao2_fio2(data_static_id, data_dynamic_id_end, obj=300, threshold=90, regle_nan=regle_nan):
            return True
         #on regarde à la "fermeture" := fin de l'intervalle de 15 minutes
        ratio_end = data_static_id['PaO2_fermeture'].values[0] / (data_dynamic_id_end['FiO2'].values[-1]/100)
        
        #on regarde au niveau du déclampage 2
        ratio_beg = data_static_id['PaO2_declampage_cote_2'].values[0] / (data['FiO2'].values[0]/100)
        if pd.isna(ratio_end - ratio_beg):
            return regle_nan
        
        return ratio_end - ratio_beg > threshold_augm

    def test_temperature_sup36(self, data_dynamic_id_end, regle_nan, threshold=70):
        """
        Test if threshold% of our value (Temp) is > 36° /do not take into account Temp = 0
        Return boolean
        """
        non_zeros = data_dynamic_id_end.Temp[data_dynamic_id_end.Temp>0].count()
        nb_ok = data_dynamic_id_end['Temp'][data_dynamic_id_end['Temp']>=36].count()
        
        if self.is_nan(data=data_dynamic_id_end, column='Temp', threshold=0.8) or non_zeros==0:
            return regle_nan

        return (nb_ok/non_zeros)*100>=threshold


    def test_NMT_sup(self, data_dynamic_id, regle_nan, obj=50, threshold=90): 
        """
        Test if threshold% of our value (NMTratio) is > 50% /do not take into account Temp = 0
        NE MARCHE PAS POUR BCP DE NOS 'IMMEDIATE_EXTUBATION'
        """
        data = self.get_end_surgery_data_dynamic(data_dynamic_id, time=5, period=25)
        if self.is_nan(data=data, column='NMTratio', threshold=0.8):
            return regle_nan
        
        non_zeros = data_2['NMTratio'][data_2['NMTratio']>0].count()
        nb_ok = data_2['NMTratio'][data_2['NMTratio']>=obj].count() 
        
        if non_zeros==0:
            return False
        return (nb_ok/non_zeros)*100>=threshold


    ##################################################################
    # SPLIT FUNCTIONS that used the results of the test function to  #
    ##################################################################

    def split_ECMO_during_surgery(self, data_static_id):
        """
        Return boolean 
        True : presence of ECMO during surgery
        False : absence of ECMO during surgery
        """
        if data_static_id['ECMO_during_surgery'].values[0]==1:
            return "Node ECMO weaning Test"
        return "Node ratio-100 test"


    def split_ECMO_weaning_test(self, data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan):
        """
        Return boolean 
        """
        sum_True = int(self.test_PASm_sup(data_dynamic_id_end, obj=60, threshold=90, regle_nan=regle_nan)) + \
        int(self.test_noradrenaline(data_static_id, nora_max=1.5, nora_min=1, regle_nan=regle_nan)) + \
        int(self.test_ratio_pao2_fio2(data_static_id, data_dynamic_id_end, obj=200,threshold=80, regle_nan=regle_nan)) + \
        int(self.test_PAP_diminution(data_dynamic_id_end, paps_max=50, paps_min=32,regle_nan=regle_nan))
        if sum_True == 4:
            return "Node INO weaning Test"
        return "Transfer to ICU with ECMO and mechanical ventilation"


    def split_ratio_100(self, data_static_id, data_dynamic_id_end, regle_nan):
        if self.test_ratio_pao2_fio2(data_static_id, data_dynamic_id_end, obj=100,threshold=90, regle_nan=regle_nan) :
            return "Node INO weaning Test"
        return "Transfer to ICU with ECMO and mechanical ventilation"

    def split_INO_weaning_test(self, data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan):
        """
        Return boolean 
        """
        sum_True = int(self.test_augm_ratio_pao2_fio2(data_static_id, data_dynamic_id_end, data_dynamic_id, threshold_augm=0, regle_nan=regle_nan)) + \
        int(self.test_PAP_diminution(data_dynamic_id_end, paps_max=50, paps_min=32, regle_nan=regle_nan))
        if sum_True == 2:
            return "Node ratio-300 test"
        return "Transfer to ICU with mechanical ventilation and iNO therapy"


    def split_ratio_300(self, data_static_id, data_dynamic_id_end,regle_nan):
        if self.test_ratio_pao2_fio2(data_static_id, data_dynamic_id_end, obj=300, threshold=80, regle_nan=regle_nan) :
            return "Node NIV attempt"
        return "Transfer to ICU with mechanical ventilation"

    def split_NIV_attempt(self, data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan, drop_NMT=True):
        """
        Return boolean 
        """
        sum_True = int(self.test_temperature_sup36(data_dynamic_id_end,threshold=90, regle_nan=regle_nan)) + \
        int(self.test_PASm_sup(data_dynamic_id_end, obj=60, threshold=85, regle_nan=regle_nan)) + \
        int(self.test_noradrenaline(data_static_id, nora_max=1.5, nora_min=1,regle_nan=regle_nan)) + \
        int(self.test_ratio_pao2_fio2(data_static_id, data_dynamic_id_end, obj=300, threshold=80, regle_nan=regle_nan))
        if drop_NMT:
            sum_goal=4
        else:
            sum_True=sum_True+int(self.test_NMT_sup(data_dynamic_id,obj=50, threshold=80, regle_nan=regle_nan))
            sum_goal = 5
            
        if sum_True == sum_goal:
            return  "Transfer to ICU with standard oxygen therapy or NIV"
        return "Transfer to ICU with mechanical ventilation"



    ########
    # TREE #
    ########


    def decision_empirique(self,id_patient, data_static, data_dynamic, regle_nan, drop_NMT):

        data_static_id = self.get_static_id(data_static, id_=id_patient)
        data_dynamic_id = self.get_dynamic_id(data_dynamic, id_=id_patient)
        data_dynamic_id_end = self.get_end_surgery_data_dynamic(data_dynamic_id,time=15, period=15)
                                   
        if self.split_ECMO_during_surgery(data_static_id) == "Node ECMO weaning Test":
            if self.split_ECMO_weaning_test(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan) == "Node INO weaning Test":
                if self.split_INO_weaning_test(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan) == "Node ratio-300 test":
                    if self.split_ratio_300(data_static_id, data_dynamic_id_end,regle_nan=regle_nan) == "Node NIV attempt":
                        return self.split_NIV_attempt(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan, drop_NMT=True)
                    else:
                        return self.split_ratio_300(data_static_id, data_dynamic_id_end,regle_nan=regle_nan)
                else : 
                    return self.split_INO_weaning_test(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan)
            else :
                return self.split_ECMO_weaning_test(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan)
            
        else: #Node ratio-100 test"
            if self.split_ratio_100(data_static_id, data_dynamic_id_end,regle_nan=regle_nan) =="Node INO weaning Test":
                if self.split_INO_weaning_test(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan) == "Node ratio-300 test":
                    if self.split_ratio_300(data_static_id, data_dynamic_id_end,regle_nan=regle_nan) == "Node NIV attempt":
                        return self.split_NIV_attempt(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan, drop_NMT=drop_NMT)
                    else:
                        return self.split_ratio_300(data_static_id, data_dynamic_id_end,regle_nan=regle_nan)
                else : 
                    return self.split_INO_weaning_test(data_static_id, data_dynamic_id_end, data_dynamic_id, regle_nan=regle_nan)
            else : 
                return self.split_ratio_100(data_static_id, data_dynamic_id_end,regle_nan=regle_nan)


    ##############              
    # EVALUATION #
    ##############

    def recode_str_leaf_into_binary(self, leaf):
        """ recode the leaves of the tree with immediate_extubation 0/1"""
        if leaf =="Transfer to ICU with standard oxygen therapy or NIV":
            return 1
        return 0

    def get_results_dataframe(self, regle_nan=True, drop_NMT=True):

        data_static = self.get_static()
        data_dynamic = self.get_dynamic()

        data_results=data_static[['id_patient','immediate_extubation']]

        ######################################
        #retrieve target
        dataset = Dataset()
        train, test = dataset.get_static()
        data = pd.concat([train, test])
        ######################################

        data_results = pd.merge(data_results, data[['id_patient','target']], how='left', on='id_patient')

        f = lambda x: self.decision_empirique(id_patient=x, data_static=data_static, data_dynamic=data_dynamic, regle_nan=True, drop_NMT=True)

        result= [f(x) for x in data_results.id_patient.values]

        data_results['result_tree']= result

        binary_result = [self.recode_str_leaf_into_binary(x) for x in data_results.result_tree.values]

        data_results['bianary_result_tree'] = binary_result

        return data_results

    def get_score_and_confusion_matrices_for_immediate_ext(self, data_results):
        
        mat=confusion_matrix(y_true=data_results['immediate_extubation'], y_pred=data_results['bianary_result_tree'])
        mat_pct = (mat/data_results.shape[0])*100
        accuracy = accuracy_score(y_true=data_results['immediate_extubation'], y_pred=data_results['bianary_result_tree'])

        print("accuracy: ", accuracy)
        print ('\n')
        print ("matrice de confusion")
        print(mat)
        print ('\n')
        print ("matrice de confusion en pct")
        print(mat_pct)

    def get_score_and_confusion_matrices_for_target(self, data_results):
        
        mat=confusion_matrix(y_true=data_results['target'], y_pred=data_results['bianary_result_tree'])
        mat_pct = (mat/data_results.shape[0])*100
        accuracy = accuracy_score(y_true=data_results['target'], y_pred=data_results['bianary_result_tree'])

        print("accuracy: ", accuracy)
        print ('\n')
        print ("matrice de confusion")
        print(mat)
        print ('\n')
        print ("matrice de confusion en pct")
        print(mat_pct)







