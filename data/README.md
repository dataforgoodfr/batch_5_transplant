## Dataset

Le dataset contient les données relatives à 412 transplantations pulmonaires ayant été réalisées par les équipes de l'hôpital Foch depuis Janvier 2012.

Elles sont issues de la collecte manuelle d'information de la part des équipes médicales, ou de l'export automatique d'instruments de mesure lors de l'opération.

Il est éclaté en ([Star Schema](https://en.wikipedia.org/wiki/Star_schema)) et contient:

- `dim_patient.csv`
- `dim_donor.csv`
- `fct_haemodynamic.csv`
- `fct_neurology.csv`
- `fct_respiratory.csv`
- `fct_temperature.csv`

### dim_patient

Cette table contient une ligne pour chacun des 412 patient du set. On peut joindre cette table aux autres en utilisant la clé `id_patient`.

| Colonne | Unité | Description | Etendue | Normalité |
| --------| ----- | ----------- | ------- | -------- |
| id_patient | clé | identifiant unique d'une patient | | |
| age | années | âge du patient | | |
| body_mass_index | | Indicateur d'obésité | 13 - 50 | 17 - 25 |

[A finir de compléter]


### dim_donor

Cette table contient une ligne par donneur de poumon. Il y a une relation 1:1 avec la table patient.


| Colonne | Unité | Description | Etendue | Normalité |
| --------| ----- | ----------- | ------- | -------- |
| id_patient | clé | identifiant unique d'une patient | | |
| age_donor | années | âge du donneur | | |
| sex_donor | | Sexe du donneur |  |  |
| body_mass_index | | Indicateur d'obésité du donneur | 13 - 50 | 17 - 25 |

etc..

### fct_haemodynamic

Mesure des capacités haemodynamique du patient. Chaque ligne correspond à une mesure prise chaque minute par les instruments de mesure lors de l'opération.

| Colonne | Unité | Description | Etendue | Normalité |
| --------| ----- | ----------- | ------- | -------- |
| id_patient | clé | identifiant unique d'une patient | | |
| time | HH:MM | timestamp de la mesure | | |
| DC | L/min | Debit cardiaque. | 0,5 - 10 | 2 - 5. < 2 anormalité |
| FC | /min | fréquence cardiaque | 0 - 220 | 50 - 90 | > 120 alerte  <br/> > 150 anomalie cardiologique <br/> < 30 anomalie cardiologique  <br/> 0 Arrêt cardiaque Si TAS effondrée|
| PAPdia | mmHg | Pression artérielle pulmonaire diastolique | 0 - 65 | 14 - 35 | possible 0 si absente|
| PAPmoy | mmHg | Pression artérielle moyenne  | 0 - 65 | 20 - 35 | |
| PAPsys | mmHg | pression artère pulmonaire systolique | 0 - 120 | 25 - 40 | > 50 danger <br/> si valeur = ou > PAS s recours à une assistance externe|
| PASd | mmHg | Pression artérielle pulmonaire diastolique | 0 - 65 | 14 - 35 | |
| PASm | mmHg | Pression artérielle moyenne  | 0 - 65 | 20 - 35 | > 60 objectif pendant l'opératioin <br/> < 40 sévérité de la situation |
| PASs | mmHg | pression artérielle systolique | 0 - 320 | 80 -140 | < 70 sévérité|
| PNId | mmHg | Pression non invasive diastolique | 0 - 65 | 14 - 35 | |
| PNIm | mmHg | pression non invasive moyenn | 0 - 65 | 20 - 35 | > 60 objectif pendant l'opération <br/> < 40 sévérité de la situation |
| PNIs | mmHg | pression non invasive systolique | 0 - 320 | 80 - 140 | < 70 sévérité |

### fct_respiratory

Mesure des capacités respiratoires du patient. Chaque ligne correspond à une mesure prise chaque minute par les instruments de mesure lors de l'opération.

| Colonne | Unité | Description | Etendue | Normalité |
| --------| ----- | ----------- | ------- | -------- |
| id_patient | clé | identifiant unique d'une patient | | |
| time | HH:MM | timestamp de la mesure | | |
| ETCO2 | % | CO2 expiré = marqueur d'équilibre général | 0 - 100 | 3 - 5.5 | <3 severite  <br/> >6 difficulté ventilatoire |
| ETO2 | % | Oxygène expiré | 21 - 100 | 35 - 60 | > 60 si besoin|
| FICO2 | % | Fraction inspirée en CO2 | 0 - 5 | 1 - 3 | non informatif |
| FIN2O | % | fraction inspirée en N20 | 0 - 60 |  | 0 Foch|
| FiO2 | % | fraction inspirée en Oxygène | 21- 100 | 21 - 50 | > 80 si oxygénation difficile|
| FR | /min | fréquence respiratoire | 0 - 60 | 12 - 24 | < 12 problème sévère <br/> > 35 difficultés au bloc|
| FR(ecg) | /min | fréquence respiratoire | 0 -  60 | 12 - 24 | < 12 problème respiratoire <br/> > 35 difficulté au bloc ne considérer que si colonne O absente ou = 0 source depuis l'Electrocardiogramme|
| MAC |  | Concentration alvéolaire moyenne | 0 - 3 | 1 - 2 | 0 si anesthésie intra veineuse|
| PEEPtotal | cmH2O | pression expiratoire positive | 0 - 20 | 4 - 8 | > 8 poumon pathologique|
| Pmax | cmH2O | pression maximale | 0 - 65 | 25 -  40 | > 40 poumon anormal|
| Pmean | cmH2O | Pression moyenne | 0 - 40 | 8 - 25 | > 30 poumon pathologique|
| Pplat | cmH2O | pression plateau | 0 - 40 | 8 - 25 | > 30 poumon pathologique|
| RR(co2) | /min | respiratory rate | 0 - 60 | 12 - 24 | < 12 problème sévère <br/> > 35 difficultés au bloc |
| SpO2 | % | Saturation pulsée en oxygène | 0 - 100 | 92 - 100 | < 90 événement notable <br/> < 80 événement grave |
| SvO2 (m) | % | saturation veineuse en oxygène | 0 - 100 | 75 - 88 | > 92 problable malposition du capteur <br/> < 60 gravité sévère|
| VT | ml | volume respiratoire |  |  | |

### fct_neurology

Mesure des capacités neurologiques du patient. Chaque ligne correspond à une mesure prise chaque minute par les instruments de mesure lors de l'opération.

| Colonne | Unité | Description | Etendue | Normalité |
| --------| ----- | ----------- | ------- | -------- |
| id_patient | clé | identifiant unique d'une patient | | |
| time | HH:MM | timestamp de la mesure | | |
| B.I.S |  | profondeur du sommeil index bispectral | 0 - 100 | 40 - 60 | > 70 mémorisation <br/> < 40 sommeil trop profond  <br/> 0 artefact si BIS SR 0 <br/> 0 valeur à considérer si BIS SR>0|
| BIS SR | % | EEG plat | 0 - 100 | 0 | > 10 anormal|
| ET Des. | % | Agent sedatif | 1 - 12 |  | rarement utilisé dans la transplantation|
| ET Sevo. | % | Agent sedatif | 1 - 6 |  | rarement utilisé dans la transplantation|
| NMT TOF |  | relaxation musculaire Train of For | 0 - 4 | 0 - 1 | 0 voir colonne S <br/> > 3 pour réveil possible|
| NMTratio | % | relaxation musculaire ratio | 0 - 100 | 0 - 100 | valeur si 4 à la colonne R <br/> > 50% réveil possible|

### fct_temperature

Mesure de la température du patient. Chaque ligne correspond à une mesure prise chaque minute par les instruments de mesure lors de l'opération.

| Colonne | Unité | Description | Etendue | Normalité |
| --------| ----- | ----------- | ------- | -------- |
| id_patient | clé | identifiant unique d'une patient | | |
| time | HH:MM | timestamp de la mesure | | |
| Temp | °C | température | 0 - 50 | 34 - 37 | > 38 infection débutante|
