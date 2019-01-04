## Classes

Les classes de ce dossier vous permette d'accéder à des fonctions standardisées pour construire et évaluer vos modèles.

_class_ *Dataset*

La classe `Dataset` vous permet d'accéder aux données statiques et dynamiques des patients. Elle est utile pour explorer les données ou constituer un training set standardisé pour développer un modèle.

_Variables_

- **time_offset**: Détermine le moment (en minutes) auquel les données dynamiques seront tronquées. Par exemple, un `time_offset` à 30 signifie que les données dynamiques seront arrêtées 30 minutes avant la dernière mesure enregistrée par les instruments de mesure.

_Fonctions_

  - **get_static**: retourne un `tuple` composé des dataframes `training` et `test` basé sur les données statiques des patients. La colonne `target` est  ajoutée au dataframe `training`. Usage:

  ```python

  from transplant.data.dataset import Dataset

  dataset = Dataset()

  train, test = dataset.get_static()

  ```

  - **get_dynamic**: retourne un `tuple` composé des datframes `training` et `test` basé sur les données  dynamiques des patients. Notez que les données sont filtrées à `time_offset` minutes avant la sortie du bloc. Usage:

  ```python

  from transplant.data.dataset import Dataset

  dataset = Dataset(time_offset=30)

  train, test = dataset.get_dynamic()

  ```

  - **get_dynamic_features**: retourne un dataframe caractérisant les valeurs dynamiques à `time_offset` avant la sortie du bloc.
  - **get_merge_data**: merge de `static` and `dynamic_feature`. Cette fonction retourne un `DataFrame` où chaque ligne correspond à un patient. Les colonnes correspondent à l'ensemble des variables statiques et dynamiques à `time_offset` avant la sortie du bloc.

_class_ *Evaluation*

  - **get_test_data**: retourne un `DataFrame` composé de l'ensemble des données statiques et dynamiques à 30 minutes avant la sortie du bloc.
  - **evaluate_prediction(y)**: affiche des indicateurs de performance du modèle. `y` correspond à un `DataFrame` composé des variables `id_patient` et `prediction`.


## Tests

Ce dossier contient les tests unitaires pour certains composants du projet. Pour lancer tous les tests depuis la racine du repo :

```
python -m unittest discover -v transplant/tests
```
