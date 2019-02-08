import pandas as pd
from transplant.config import PATH_STATIC_CLEAN


def get_good_bad_result(result):
    """
    Split result from analyse_prediction into 2 DataFrame.
    All our good prediction (in good DataFrame) and all our
    mistake in bad
    Input :
        - result [DataFrame]: from analyse_prediction()
    Ouput :
        - good [DataFrame]: Good result by our model
        - bad [DataFrame]: Bad result by our model
    """

    good = result[result['prediction'] == result['target']]
    bad = result[result['prediction'] != result['target']]
    return good, bad


def get_info_patient_operation(id_patient):
    """
    To understand what happend to a patient in reality
    It could be OK :
        - Succès A
        - Succès B
    It could be a fail and why is it a fail
    Input :
        - id_patient [str]: patient's ID
    Return :
        None
    """

    static_clean = pd.read_csv(PATH_STATIC_CLEAN)
    static_clean = static_clean[static_clean['id_patient'] == id_patient]

    if len(static_clean[(static_clean.immediate_extubation == 1) &
                        (static_clean.secondary_intubation == 0)]) > 0:
        print("Succès A: le patient a été extubé immédiatement à la fin du \n\
              bloc opératoire et n'a pas été réintubé par la suite.")
    elif len(static_clean[(static_clean.immediate_extubation == 0) &
                          (static_clean.secondary_intubation == 0) &
                          (static_clean.LOS_first_ventilation < 2) &
                          (static_clean.Survival_days_27_10_2018 >= 2)]) > 0:
        print("Succes B: Le patient n'a pas été extubé immédiatement à la fin \n\
              du bloc opératoire, n'a pas été réintubé par la suite et est \n\
              resté moins de 48h sous assistance, durée pendant laquelle il \n\
              n'est pas décédé.")
    else:
        print("FAIL")
        if len(static_clean[static_clean.LOS_first_ventilation >= 2]) > 0:
            var_LOS_first_ventilation = \
                static_clean.LOS_first_ventilation.values[0]
            print("LOS_first_ventilation : " + str(var_LOS_first_ventilation))
        else:
            var_survival = \
                static_clean.Survival_days_27_10_2018.values[0]
            print("Survival_days_27_10_2018 : " + str(var_survival))


def analyse_prediction(model, X_test, y_test, features_list):
    """
    Return prediction (Bool + proba) & target.
    Input :
        - Model [Scikit.estimator]: model already fit
        - X_test [DataFrame]: Test set (with all data) to get id_patient
        - y_test [pandas.Serie]: target of our test set
        - features_list [list]: list of feature to predict result
    Ouput :
        - result [DataFrame]: with all features (original)
            - Prediction of our model
            - Probability of our model
            - Our target (reality)
    """
    patient_list = X_test['id_patient']
    result = X_test[features_list].copy()
    result['prediction'] = model.predict(X_test)
    result['proba'] = model.predict_proba(X_test)[:, 1]
    result['target'] = y_test
    result['id_patient'] = patient_list
    return result
