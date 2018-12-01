## Classes

Les classes de ce dossier vous permette d'accéder à des fonctions standardisées pour construire et évaluer vos modèles.

_class_ *Dataset*

La classe `Dataset` vous permet d'accéder aux données statiques et dynamiques des patients. Elle est utile pour explorer les données ou constituer un training set standardisé pour développer un modèle.

_Variables_

- `train`: `False` ou `True`. Détermine si la classe `Dataset` à renvoyer est le training set sur lequel le modèle sera entrainé.
- `test`: `False` ou `True`. Détermine si la classe `Dataset` à renvoyer est le test set sur lequel le modèle sera évalué.
- `time_offset`: Détermine le moment (en minutes) auquel les données dynamiques seront tronquées. Par exemple, un `time_offset` à 30 signifie que les données dynamiques seront arrêtées 30 minutes avant la sortie du bloc.

_Fonctions_

  - `get_static`: retourne un `DataFrame` des données statiques des patients. Une colonne `target` y est ajoutée et permet de déterminer la variable à prédire. A noter que la valeur de target sera `NaN` dans le cas où la variable `test` est égale à `True`.
  - `get_dynamic`: retourne un `DataFrame` des données dynamiques par patient et timestamp à `time_offset` avant la sortie du bloc.
  - `get_dynamic_features`: retourne un dataframe caractérisant les valeurs dynamiques à `time_offset` avant la sortie du bloc.
  - `get_merge_data`: merge de `static` and `dynamic_feature`. Cette fonction retourne un `DataFrame` où chaque ligne correspond à un patient. Les colonnes correspondent à l'ensemble des variables statiques et dynamiques à `time_offset` avant la sortie du bloc.

_`Evaluation`_

  - `get_test_data`: retourne un `DataFrame` composé de l'ensemble des données statiques et dynamiques à 30 minutes avant la sortie du bloc.
  - `evaluate_prediction(y)`: affiche des indicateurs de performance du modèle. `y` correspond à un `DataFrame` composé des variables `id_patient` et `prediction`.

## Example

Afin d'utiliser ces fonctions, il vous suffit d'instancier les classes, puis d'appeler votre fonction:

```python

from dataset import Dataset

#initialize class Dataset
dataset = Dataset()

dataset.train = True
dataset.test = False
dataset.time_offset = 30

#call a function of interest
training_set = dataset.get_merge_data()

```
