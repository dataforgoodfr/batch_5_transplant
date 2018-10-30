# batch_5_transplant

## Présentation

L'objectif du projet est d'aider à la décision les médecins de l'hôpital Foch pour trouver le moment opportun pour désactiver l'assistance respiratoire.

Une opération de transplantation se fait en plusieurs phases:

- Anesthésie
- Enlever le premier poumon et remettre le premier nouveau poumon
- Enlever le second poumon et remettre le second nouveau poumon
- Réveil

## Dataset

- Séries temporelles extraites des instruments de mesure du bloc opératoire.
- Marqueurs temporels collectés manuellement lors de la transplantation.

## Foire aux Questions

Nous maintenons une foire aux questions au sein de [ce document partagé](https://docs.google.com/document/d/1d_Tbq-IAW-30KVEQZv_IKozlDDtzy6QnfETXtgBTucw/edit).

## Arborescence 

Vous retrouverez plusieurs dossiers dans ce git:

- `data` : vous retrouverez dans ce dossier l'ensembles des datasets.
- `documentation`: dossier contenant tous les fichiers de documentation.
- `scripts` : dossier contenant les scripts de cleaning et création des tables de dimensions et faits.
- `etudes` : pour chaque étude effectuée merci de mettre vos notebooks dans ce dossier.

## Environnement technique de travail 

- Télécharger anaconda / miniconda selon votre OS [lien](https://www.anaconda.com/download/#macos) version 3.x.

- Mettre en place votre environnement conda

```bash
bash set_env.sh
source activate transplant
```

Si jamais vous souhaitez créer votre propre environnement

```bash
conda create -n transplant python=3.5
conda install pandas
conda install scikit-learn
conda install nb_conda
conda install xlrd
```

Pour faire l'export de votre environnement :

```bash
conda env export | grep -v "^prefix: " > environment_OS.yml
```

Pour activer votre environnement conda:
```bash
source activate transplant
```





