# -*- coding: utf-8 -*-
"""Bigmart_Sales_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JrknLk9yJ2i8hVu-6Ne6aevRwbEXeg3p

**RETAIL SALES FORECASTING USING MACHINE LEARNING**
by Angela van der Westhuizen

Retail companies are constantly faced with decision making in order to boost sales.
Managers are sometimes expected to forecast sales in order to prepare for demand trends, sales
forecasting is the process of estimating future sales of products or services based on historical data,
market trends, customer behavior, and other factors. Accurate retail sales forecasting can therefore
help retailers with inventory optimization, marketing, pricing, and staffing decisions. This is a Big Mart Dataset with historical Data from 2013 covering 10 different stores with thousands of products, Big Mart wants to maximise their sales and this requires information and analytics to help predict future sales and determine what increase sales and what variables have no effect on sales. However,retail
sales forecasting is challenging due to the complexity and uncertainty of the factors that affect sales, therefore, this project presents an analysis of the Bigmart Sales dataset, aiming to predict the sales of items for the 10 outlets. The dataset is divided into training and testing sets, and the project involves data exploration, cleaning, visualization, and predictive modeling.

**Data Source**
The dataset for this project was sourced from one of the readily available datasets from Kaggle.com.
The data set contains Big Mart sales data for 2013 covering 10 stores with variables such as Item Type, outlet type, outlet size, maximum retail price etc.

1. **Importing Relevant Libraries**
The necessary libraries, such as pandas, numpy, seaborn, and scikit-learn, are imported to facilitate data manipulation, visualization, and machine learning model development.
"""

from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score,cross_val_predict
import matplotlib as plt
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn import metrics
import statsmodels.api as sm
from sklearn.linear_model import Lasso, Ridge

"""2. **Loading Datasets**
The training and testing datasets are loaded into pandas dataframes their shapes are checked to understand the number of records and features in each dataset.
"""

train = pd.read_csv("Train.csv")
test = pd.read_csv("Test.csv")

# checking the shape of train
train.shape

# checking the shape of test
test.shape

train.head(10)

"""**Data exploration and preprocessing**: This step involves exploring the data set, checking for
missing values, outliers, and anomalies, and performing appropriate transformations and feature
engineering.
3.1 Dataset Overview
The first 5 rows of the training dataset are displayed, and the data types and information about missing values are examined. The describe() and info() functions give summaries about the dataset.
"""

train.info()

train.dtypes

""" Data Cleaning
Several steps are taken to clean the data,  including checking for and handling missing values through replacement and imputation.
"""

train.isnull().sum(axis=0)

"""Item_Weight has 1463 and Outlet_Size has 2410 missing values"""

train.describe()

"""DATA VISUALISATION
Creating visuals using Scatter plots, bar charts, boxplots etc. to depict relationships between varibles aswell as show patterns.
"""

plt.scatter(train.Item_Visibility,train.Item_Outlet_Sales)
plt.xlabel("Item Visibility")
plt.ylabel("Item Outlet Sales")
plt.title("Item Visibility vs Item Outlet Sales")

plt.show()

plt.bar(train.Outlet_Identifier,train.Item_Outlet_Sales)
plt.show()

sns.barplot(x='Outlet_Identifier',y='Item_Outlet_Sales', data=train ,palette='magma',capsize = 0.05,saturation = 8,errcolor = 'gray', errwidth = 2,
            ci = 'sd')
plt.show()

""".Top 2 Contributors: Outlet_27 > Outlet_35
    .Bottom 2 Contributors: Outlet 10 & Outlet 19

Analysing sales by Item type
"""

sns.barplot(x='Item_Type',y='Item_Outlet_Sales',data=train,palette='hls',saturation=8)
plt.xticks(rotation=90)
plt.show()

"""#### Using a boxplot to check for outliers for each item type"""

sns.boxplot(x='Item_Type',y='Item_MRP',data=train,palette='Paired',saturation=8)
plt.xticks(rotation=90)
plt.show()

train.Item_Fat_Content.value_counts() # has mismatched factor levels

train.Item_Visibility.value_counts()

train.Outlet_Size.value_counts()

test['Item_Outlet_Sales'] = 1
test.Item_Outlet_Sales.head()

train_copy = train.copy()
test_copy = test.copy()

combined = pd.concat([train,test])
combined.head()

crosstable = pd.crosstab(train['Outlet_Size'],train['Outlet_Type'])
crosstable

train.Outlet_Size.value_counts()

"""Grocery stores are mapped to "small" since most of the fall under that category"""

dic = {'Grocery Store':'Small'}
s = train.Outlet_Type.map(dic)

train.Outlet_Size= train.Outlet_Size.combine_first(s)
train.Outlet_Size.value_counts()

train.isnull().sum(axis=0)

#checking for location type
crosstable = pd.crosstab(train.Outlet_Size,train.Outlet_Location_Type)
crosstable

dic = {"Tier 2":"Small"}
s = train.Outlet_Location_Type.map(dic)
train.Outlet_Size = train.Outlet_Size.combine_first(s)
train.Outlet_Size.value_counts()

train.isnull().sum(axis=0)

train.Item_Identifier.value_counts().sum()

#Fill missing values of weight of Item According to means of Item Identifier
train['Item_Weight']=train['Item_Weight'].fillna(train.groupby('Item_Identifier')['Item_Weight'].transform('mean'))
train.isnull().sum()

train[train.Item_Weight.isnull()]

# List of item types
item_type_list = train.Item_Type.unique().tolist()
item_type_list

# grouping based on item type and calculating mean of item weight
Item_Type_Means = train.groupby('Item_Type')['Item_Weight'].mean()

Item_Type_Means

# Mapiing Item weight to item type mean
for i in item_type_list:
    dic = {i:Item_Type_Means[i]}
    s = train.Item_Type.map(dic)
    train.Item_Weight = train.Item_Weight.combine_first(s)

Item_Type_Means = train.groupby('Item_Type')['Item_Weight'].mean()

train.isnull().sum()

Item_Type_Means

"""**Missing values for item_weight have been imputed**"""

train.Item_Weight.isnull().any() # no missing values

"""### Imputing for item visibility

Item visibility cannot be 0 and should be treated as missing values and imputed
"""

train.Item_Visibility.value_counts().head() # There are 526 values with 0 Item visibility

"""**Imputing with mean of item_visibility of particular item identifier category as some items may be more visible and some less."""

# Replacing 0's with NaN
train.Item_Visibility.replace(to_replace=0.000000,value=np.NaN,inplace=True)
# Now fill by mean of visbility based on item identifiers
train.Item_Visibility = train.Item_Visibility.fillna(train.groupby('Item_Identifier')['Item_Visibility'].transform('mean'))

train.Item_Visibility.value_counts().head()

train.isnull().sum()

"""Standardising and renaming fat content levels to make it uniform for each level. eg lf and low fat will both be low fat"""

train.Item_Fat_Content.value_counts()

train.Item_Fat_Content.replace(to_replace=["LF","low fat"],value="Low Fat",inplace=True)
train.Item_Fat_Content.replace(to_replace="reg",value="Regular",inplace=True)

train.Item_Fat_Content.value_counts()

train['Outlet_Year'] = (2013 - train.Outlet_Establishment_Year)

train.head()

"""### Encoding Categorical Variables"""

var_cat = train.select_dtypes(include=[object])
var_cat.head()

#Convert categorical into numerical
var_cat = var_cat.columns.tolist()
var_cat = ['Item_Fat_Content',
 'Item_Type',
 'Outlet_Size',
 'Outlet_Location_Type',
 'Outlet_Type']

var_cat

train['Item_Type_New'] = train.Item_Identifier
train.Item_Type_New.head(10)

train.Item_Type_New.replace(to_replace="^FD*.*",value="Food",regex=True,inplace=True)
train.Item_Type_New.replace(to_replace="^DR*.*",value="Drinks",regex=True,inplace=True)
train.Item_Type_New.replace(to_replace="^NC*.*",value="Non-Consumable",regex=True,inplace=True)

train.head()

le = LabelEncoder()

train['Outlet'] = le.fit_transform(train.Outlet_Identifier)
train['Item'] = le.fit_transform(train.Item_Type_New)
train.head()

for i in var_cat:
    train[i] = le.fit_transform(train[i])

train.head()

#Visualizing Correlation
corrmat = train.corr()
corrmat

f,ax = plt.subplots(figsize = (15,10))
sns.heatmap(corrmat,annot=True,ax=ax,cmap="YlGnBu",linewidths=0.1,fmt=".2f",square=True)
plt.show()

"""# Predictive Modelling"""

predictors=['Item_Fat_Content','Item_Visibility','Item_Type','Item_MRP','Outlet_Size','Outlet_Location_Type','Outlet_Type','Outlet_Year',
            'Outlet','Item','Item_Weight']

seed = 240
np.random.seed(seed)

X = train[predictors]
y = train.Item_Outlet_Sales

X.head()

y.head()

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size = 0.25,random_state = 42)

X_train.shape

X_train.tail()

X_test.shape

y_train.tail()

y_test.tail()

y_train.shape

y_test.shape

lm = LinearRegression()

model = lm.fit(X_train,y_train)
predictions = lm.predict(X_test)

predictions[:5]

"""## Plotting the model"""

plt.scatter(y_test,predictions)
plt.show()

#Accuracy Score
print("Linear Regression Model Score:",model.score(X_test,y_test))

original_values = y_test

#Root mean squared error
rmse = np.sqrt(metrics.mean_squared_error(original_values,predictions))

print("Linear Regression R2 score: ",metrics.r2_score(original_values,predictions))

print("Linear Regression RMSE: ", rmse)

"""**Linear Regression wihtout cross validation:**

    Linear Regression R2 score:  0.505
    Linear Regression RMSE:  1168.37

    
"""

# Linear Regression with statsmodels
x = sm.add_constant(X_train)
results = sm.OLS(y_train,x).fit()
results.summary()

predictions = results.predict(x)
predictions.head()

predictionsDF = pd.DataFrame({"Predictions":predictions})
joined = x.join(predictionsDF)
joined.head()

"""### Performing Croass Validation"""

# Perform 6-fold cross validat
score = cross_val_score(model,X,y,cv=5)
print("Linear Regression Cross Validated Score: ",score)

#Predicting with cross_val_predict
predictions = cross_val_predict(model,X,y,cv=6)
predictions[:5]

plt.scatter(y,predictions)
plt.show()

"""### Using KFold Validation"""

def calc_metrics(X_train, y_train, X_test, y_test, model):
    '''fits model and returns the RMSE for in-sample error and out-of-sample error'''
    model.fit(X_train, y_train)
    train_error = calc_train_error(X_train, y_train, model)
    validation_error = calc_validation_error(X_test, y_test, model)
    return train_error, validation_error

def calc_train_error(X_train, y_train, model):
    '''returns in-sample error for already fit model.'''
    predictions = model.predict(X_train)
    mse = metrics.mean_squared_error(y_train, predictions)
    rmse = np.sqrt(mse)
    return mse

def calc_validation_error(X_test, y_test, model):
    '''returns out-of-sample error for already fit model.'''
    predictions = model.predict(X_test)
    mse = metrics.mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    return mse

kf = KFold(n_splits=10,random_state=(None))
kf.get_n_splits(X)

print(kf)

alphas = [1e-4, 1e-3, 1e-2, 1e-1, 1, 1e1]
for alpha in alphas:
    train_errors = []
    validation_errors = []
    for train_index,val_index in kf.split(X_train,y_train):
        X_train,X_val = X.iloc[train_index],X.iloc[val_index]
        y_train,y_val = y.iloc[train_index],y.iloc[val_index]

        # Instantiate Model
        lasso_model = Lasso(alpha=alpha,fit_intercept=True,random_state=77)

        #Caculate Errors
        train_error,val_error = calc_metrics(X_train,y_train,X_val,y_val,lasso_model)

        # append to list
        train_errors.append(train_error)
        validation_errors.append(val_error)
    # generate report

    print('alpha: {:6} | mean(train_error): {:7} | mean(val_error): {}'.
          format(alpha,
                 round(np.mean(train_errors),4),
                 round(np.mean(validation_errors),4)))

"""### Random Forest Regressor"""

rf = RandomForestRegressor(random_state=43)

rf.fit(X_train,y_train)

predictions = rf.predict(X_test)
predictions[:5]

rmse = np.sqrt(metrics.mean_squared_error(y_test,predictions))
rmse

print(metrics.r2_score(y_test,predictions))

results = pd.DataFrame({'Actual':y_test,'Predicted':predictions})
results.head()

"""### Randorm Forest Regression with kfold validation score
    RMSE: 882
    R2 Score: 0.717
    
"""

plt.figure(figsize=(15,7))
plt.scatter(y_test, predictions, s=20)
plt.title('RandomForestRegressor',fontsize=20)
plt.xlabel('Actual Sales',fontsize=15)
plt.ylabel('Predicted Sales',fontsize=15)
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='r', linewidth = 4)
plt.tight_layout()

"""# References

[Model Tuning Reference](https://dziganto.github.io/cross-validation/data%20science/machine%20learning/model%20tuning/python/Model-Tuning-with-Validation-and-Cross-Validation/)

[Towards Data Science](http://towardsdatascience.com/)

[Sklearn Documentation](https://scikit-learn.org/stable/)

[Stackoverflow](https://stackoverflow.com/)


"""

