## Classes

Les classes de ce dossier vous permette d'accéder à des fonctions standardisées pour construire et évaluer vos modèles.

- `DataSet`: accéder aux données sources, deux fonctions:

Variables:  
  training: False / True
  test: False / True

Fonctions:
  - `get_static`: retourne un `DataFrame` des données statiques des patients ainsi que la variable target.
  - `get_dynamic(time_offset)`: retourne un `DataFrame` des données dynamiques par patient et timestamp. L'historique s'arrête `time_offset` minutes avant la sortie du bloc.
  - `get_dynamic_features(time_offset)`: retourne un dataframe caractérisant les valeurs dynamiques à `time_offset` avant la sortie du bloc.
  - `get_full_data(time_offset)`: merge de `static` and `dynamic_feature`. Cette fonction retourne un `DataFrame` où chaque ligne correspond à un id_patient et dont les colonnes sont l'ensemble des variables statiques et des features dynamiques à `time_offset` avant la sortie du bloc.

- `Evaluation`:

  - `get_evaluation_data`: retourne un `DataFrame` composé de l'ensemble des données statiques et dynamiques à 30 minutes avant la sortie du bloc, sans variable target.
  - `evaluate_prediction(y)`: affiche des indicateurs de performance du modèle. `y` correspond à un `DataFrame` composé des variables `id_patient`, `prediction`.
