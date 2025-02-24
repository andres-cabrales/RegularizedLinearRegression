# -*- coding: utf-8 -*-
"""Taller Regularized Linear Regression 2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/164IgHwSb6T3zz6x0rk7vPH0GdQea559s
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.diagnostic import het_breuschpagan
from sklearn.model_selection import train_test_split, RepeatedKFold
from sklearn.model_selection import KFold
import statsmodels.api as sm
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import Lasso
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import GridSearchCV

df = pd.read_csv('https://raw.githubusercontent.com/4GeeksAcademy/regularized-linear-regression-project-tutorial/main/demographic_health_data.csv')
df

df.info()

df.columns

df.describe()

df[df.duplicated()]

df.duplicated().sum()

"""**MIRAMOS SI LA TABLA TIENE ELEMENTOS NULOS**"""

print(df.isnull().sum())

df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False)

"""**BUSCAMOS LAS COLUMNAS TIPO OBJECT**"""

encontrando_object = [col for col in df.columns if df[col].dtype == 'object']
print(encontrando_object)

"""**CREAMOS DATA FRAME CON COLUMNAS NUMERICAS SOLAMENTE**"""

# Seleccionando columnas numericas
df_num = df.select_dtypes(include=[np.number])
#Nuestra variable objetivo es anycondition_number y aplicamos la correlación

correlacion = df_num.corr()['Heart disease_number'].sort_values(ascending=False)
#Filtramos variables con correlación mayor a 0.80
relevantes = correlacion[correlacion > 0.80]
relevantes

"""**SCALER ESTANDARIZA LOS DATOS DEL DATA FRAME DF_NUM**"""

scaler = StandardScaler()
estandarizado = scaler.fit_transform(df_num)

# Crear un nuevo DataFrame con las variables escaladas
df_scaled = pd.DataFrame(estandarizado)
df_scaled["Heart disease_number"] = df["Heart disease_number"]

"""**X SON LAS VARIABLES INDEPENDIENTES** -
**Y ES LA VARIABLE DEPENDIENTE O DE INTERES**
"""

# Trabajare con todas las variables ya que es vital no perder informacion, esto afectaria mi regresion, se eliminan solo las variables que tienen extrema relacion con la variable de interes
y = df_num['Heart disease_number']
X = df_num.drop('Heart disease_number', axis = 1)
X = X.loc[:, ~X.columns.str.contains('heart', case=False)]

"""**DIVIDIMOS EL DATAFRAME EN TRAIN Y TEST**"""

# Dividimos  el Dataframe en Train y Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# Alpha controla la intensidad de la regularización en la regresión, Si alpha = 0, no hay regularización, y ElasticNet se comporta como una regresión lineal estándar
alphas = [0.0001, 0.001, 0.01, 0.1, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]

#lrs representa l1_ratio, que controla el equilibrio entre Ridge (L2) y Lasso (L1). 0 < l1_ratio < 1 → Combinación de Ridge y Lasso, controlando la mezcla de ambas penalizaciones.
lrs = [0, 0.5, 1]
errors = {}

kfold = RepeatedKFold(n_splits=5, n_repeats=3, random_state=123)
for alpha in alphas:
    errors[alpha] = {}
    for lr in lrs:
        fold_errors = []
        model = ElasticNet(alpha=alpha, l1_ratio=lr, random_state=42)
        for train_idx, test_idx in kfold.split(X_train):
            X_train_fold, X_test_fold = X_train.iloc[train_idx], X_train.iloc[test_idx]
            y_train_fold, y_test_fold = y_train.iloc[train_idx], y_train.iloc[test_idx]
            model.fit(X_train_fold, y_train_fold)
            fold_errors.append(mean_squared_error(y_test_fold, model.predict(X_test_fold)))
        errors[alpha][lr] = np.mean(fold_errors)

best_alpha, best_lr = min(
    ((a, l) for a in alphas for l in lrs),
    key=lambda pair: errors[pair[0]][pair[1]]
)
best_model = ElasticNet(alpha=best_alpha, l1_ratio=best_lr, random_state=123)
best_model.fit(X_train, y_train)
final_preds = best_model.predict(X_test)
final_mse = mean_squared_error(y_test, final_preds)
print(f"Mejor alpha: {best_alpha}, Mejor l1_ratio: {best_lr}")
print(f"Error cuadrático medio en test: {final_mse}")

ridge_cv = RidgeCV(alphas=alphas, cv=5)
ridge_cv.fit(X_train, y_train)

lasso_model = Lasso(alpha=0.1)
lasso_model.fit(X_train, y_train)
lasso_preds = lasso_model.predict(X_test)
lasso_mse = mean_squared_error(y_test, lasso_preds)
print(f"Lasso MSE: {lasso_mse}")

y_pred = ridge_cv.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Error Cuadrático Medio (MSE) en validación: {mse}")
print(f"Coeficiente de Determinación (R²) en validación: {r2}")