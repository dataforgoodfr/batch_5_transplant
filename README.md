# batch_5_transplant

## Présentation

Projet de prédiction de transplantation pulmonaire en partenariat avec l'hôpital Foch.

L'objectif du projet est d'aider à la décision les médecins de l'hôpital Foch pour trouver le moment opportun pour désactiver l'assistance respiratoire.

Une opération de transplantation se fait en plusieurs phases:

- Anesthésie
- Enlever le premier poumon et remettre le premier nouveau poumon
- Enlever le second poumon et remettre le second nouveau poumon
- Réveil

## Dataset

- Séries temporelles extraites des instruments de mesure du bloc opératoire.
- Marqueurs temporels collectés manuellement lors de la transplantation. 

## Dictionnaire des variables:

- `timestamp`: Export des données issues de différents appareils réalisé chaque minute.
- `id_patient`: Identifiant anonyme d'un patient.
- `B.I.S`: Profondeur du sommeil. Index bispectral. Indicateur de 0 à 100. Normalité [40, 60]
`BIS SR`:
- DC
- ET Des.
- ET Sevo.
- ETCO2
- ETO2
- FC
- FICO2
- FIN2O
- FiO2
- FR
- FR(ecg)
- MAC
- NMT TOF
- NMTratio
- PAPdia
- PAPmoy
- PAPsys
- PASd
- PASm
- PASs
- PEEPtotal
- Pmax
- Pmean
- PNId
- PNIm
- PNIs
- Pplat
- RR(co2)
- SpO2
- SvO2 (m)
- Temp
- VT
