# Transplant - Machine learning canvas

The following data science canvas give a clear overview of challenges and issues that will be faced to develop and deploy the machine learning model.

### Ideas & Specs

#### Context

Who will use the predictive system / who will be affected by it? Provide some background.

```
Anesthetist will use the predictive model as a guidance tool to decide if a patient must be immediately extubate after a lung transplantation. 
Patient will directly be affected by this decision (infection, death)
```

#### Value proposition

What are we trying to do? E.g. spend less time on X, increase Y...
increase the rate of total premium customers

```
Faster patient recovery after lung transplantation, patient spends less time in hospital (more confortable)
```

#### Data sources
Where do/can we get data from? (internal database, 3rd party API, etc.)
The following data sources have been identified for this use case

```
Preo - intra - postoperative data 
```

[full dataset description](https://github.com/dataforgoodfr/batch_5_transplant/blob/master/data/README.md)

#### Problems
Questions to predict the answer (in plain english)

```
Should I immediately extubate a patient after a LT ? 
```

#### target
Explain how to compute the target
```
In dataset dim_patient

IE = immediate_extubation
SE = secondary_extubation

case 1 : if IE == 1 and SE == 1 : IE has not been successfull
case 2 : if IE == 1 and SE == 0 : IE has been successfull
case 3 : if IE == 0 and SE == 0 : no IE on the patient
case 4 : if IE == 0 and SE == 1 : autoextubation (patient extubate himself)

We should focus on case 1 and 2 (135 patients)

case 1 : 16 patients 
case 2 : 119 patients 

target == 0 : IE has not been successfull
target  == 1 : IE has been successfull

``` 
#### Type of problems
e.g. Binary classification (XGboost, RF, Naive Bayes classifier…)

```
Binary classification

Small data : very simple algorithm, with few parameters (Naive Bayes, SVM) to avoid overfitting (no boosting, no deep learning)
Unbalanced target : sampling method or outliers detection algorithm (One class SVM)
Interpretability : to have an impact on Dr decisions the predictive model must be simple to interpret (avoid blackbox effect)
```

#### output

```
For a new patient : a probability => chance for an IE to be successfull
``` 

####  Performance evaluation
Domain-specific / bottom-line metrics for monitoring performance in production

```
TBD later
```

#### Prediction accuracy metrics (e.g. MSE if regression; % accuracy, #FP for classification)

```
Impact of FP and FN is asymetric
Accuracy metric should penalize model with large proportion of FALSE POSITIVE

custom cost function #FP 

```


#### Offline performance evaluation method (e.g. cross-validation or simple training/test split)

```
Cross validation
```

#### Baseline
What is an alternative way of making predictions (e.g. manual rules based on feature values)?

```
Decision tree (cf: Dr Antoine Roux)
```

#### Dataset

How do we collect data (inputs and outputs)? How many data points?

```
135 data points 
```

#### Features

Used to represent inputs and extracted from data sources above. Group by types and mention key features if too many to list all.

```
so far .. 

dim_patient : age, sex, .. 
context : hours of transplantation, month .. 
dim_donor : disease, sex, age, length ... 
fct_ table : features extraction from time series 
```

### Deployments

#### Using predictions

When do we make predictions and how many?

```
One predictions for each new patient at the end of the lung transplantation.
```

Learning predictive models
When do we create/update models? With which data / how much?
Define metrics to monitore the model : e.g accuracy

```
Update the model for each new data point (patient) in the dataset 
```

Criteria for deploying model (e.g. minimum performance value — absolute, relative to baseline or to previous model)

```
TBD - later
```

[Louis Dorard  © 2015, Machine Learning Canvas](http://www.louisdorard.com/)

