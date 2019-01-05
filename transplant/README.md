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


_class_ *visualization*

Vous pouvez facilement visualiser et explorer les données dans un notebook. Il est important que `id_patient` soit en colonne dans le *DataFrame*. Nous importerons ici l'integralité du set dynamique: 

  - **import_data**:

```python
import pandas as pd
from transplant.config import *               # import de variables

df = pd.read_csv(PATH_DYNAMIC_CLEAN)

df.tail() # Afficher les données
```
![ECMO](../docs/images/afficher_data.png)

  - **plot_dynamic_features**: Explorer les variables d'un patient

```python
# On reprend notre DataFrame df un peu plus haut
from transplant.visualization.graph import plot_dynamic_features

# On regarde pour le patient n°407 les variables 'B.I.S' et'FR'
plot_dynamic_features(df, 407, ['B.I.S', 'FR'])
```

![ECMO](../docs/images/plot_dynamic_features.png)

- **plot_compare_patient**: Comparer une même variable sur plusieurs patients

```python
# On reprend notre DataFrame df un peu plus haut
from transplant.visualization.graph import plot_compare_patient

# On compare la varible 'FR' sur les patient n°167, 205 et 407
plot_compare_patient(df, 'FR', [167, 205, 407])
```

![ECMO](../docs/images/plot_compare_patient.png)

## Tests

Ce dossier contient les tests unitaires pour certains composants du projet. Pour lancer tous les tests depuis la racine du repo :

```
python -m unittest discover -v transplant/tests
```
