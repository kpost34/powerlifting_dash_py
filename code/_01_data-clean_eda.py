# This script does initial data cleaning/wrangling and performs EDA

# Load Libraries and Set Options====================================================================
## Load libraries
# import os
import numpy as np
import pandas as pd
import inflection
import re
import matplotlib.pyplot as plt
import seaborn as sns




import pickle



# Read in Large Data File, Filter, and Re-Save======================================================
## Data import
# df0 = pd.read_csv('data/openipf-2024-10-12-b58b8e08.csv', low_memory=False)
# 
# 
# ## Filter data
# #get info
# df0.shape #~1.3 million records
# 
# #filter data: men (18+) in 105 Kg weight class in US meets in last 4 years
# df1 = df0.copy()
# df1['year'] = pd.to_datetime(df0['Date']).dt.year
# df2 = df1[(df1['MeetCountry']=="USA") & (df1['Sex']=='M') & (df1['WeightClassKg']=='105') &
#            df1['year'].isin([2021, 2022, 2023, 2024]) & (df1['Age']>=18)]
# df2.shape #~27 K records
# 
# ### Re-save file
# df2.to_csv('data/openipf_2024-10-12_filtered.csv')
# 
# 
# ## Data hygiene
# del df0, df1, df2


# Read in Filtered Data, Objects, and Functions=====================================================
## Data
df = pd.read_csv('data/openipf_2024-10-12_filtered.csv')


## Objects


## Functions



# Initial Cleaning==================================================================================
## Rename first col and convert to snake case
df.rename(columns={'Unnamed: 0': 'id'}, inplace=True)
df.columns = df.columns.map(inflection.underscore).tolist()


### Drop cols (that are the same for all rows) 
#sex (all male), tested (all yes), sanctioned (all yes), parent_federation (all IPF), 
  #meet_country (all USA), weight class (all 105)
df = df.drop(columns=['sex', 'tested', 'sanctioned', 'parent_federation', 'meet_country', 
                      'weight_class_kg'])
df.columns



# Data Checking=====================================================================================
## General info
df.shape #2421 x 38
df.columns
df.index #numeric: 0-2421
df.dtypes
df.head()
df.info()


## Missingness 
df.isnull().sum().sort_values(ascending=False) #0 - ~2421


## Duplicates
print(df.duplicated().sum()) #no duplicate rows



# Secondary Wrangling===============================================================================
## Pivot from wide to long for lifts
#isolate columns
cols_pivot = df.filter(regex='squat|bench|deadlift|^total_kg$').columns
cols_id = df.columns[~df.columns.isin(cols_pivot)].to_list()

#melt DF
df_melt0 = pd.melt(df, id_vars=cols_id, value_vars=cols_pivot, 
                   var_name='lift', value_name='mass_kg')

#remove '_kg' suffix from lift categories 
df_melt0['lift'] = df_melt0['lift'].str.replace(r'_kg$', '', regex=True)


## Re-order columns
#convert col index to list
cols_melt0 = df_melt0.columns.to_list()

#create list of cols to remove and remove them
cols_to_remove = ['year', 'lift', 'mass_kg']
cols_melt = [col for col in cols_melt0 if col not in cols_to_remove]

#insert cols just removed
cols_melt[9:9] = ['lift', 'mass_kg']
cols_melt.insert(20, 'year')

df_melt1 = df_melt0.reindex(columns=cols_melt)
df_melt1.head()


## Convert data types
df_melt1.info()
df_melt2 = df_melt1.copy()

### Categorical variables
#### Convert to categorical type
cols_cat = ['event', 'equipment', 'age_class', 'birth_year_class', 'division', 'lift', 'place', 
            'country', 'state', 'federation', 'meet_state', 'meet_town', 'meet_name']
            
df_melt2[cols_cat] = df_melt1[cols_cat].astype('category')


#### Re-order variables
##### lift
#convert categories to list
lifts_cat = df_melt2['lift'].cat.categories.tolist()

#create new list of cats
lifts_to_remove = ['best3_deadlift', 'best3_squat']
lifts_new_cat = [cat for cat in lifts_cat if cat not in lifts_to_remove]

lifts_new_cat.insert(9, 'best3_deadlift')
lifts_new_cat.insert(14, 'best3_squat')

#use new list as categories
df_melt2['lift'] = df_melt2['lift'].cat.set_categories(lifts_new_cat)

#place
places_new_cat = list(range(1, 47)) + ['DD', 'DQ', 'G']
places_new_cat = [str(cat) for cat in places_new_cat]

df_melt2['place'] = df_melt2['place'].cat.set_categories(places_new_cat)


### Date variable
df_melt2['date'] = pd.to_datetime(df_melt2['date'])


## Data hygiene
del df_melt1



# Exploratory Data Analysis=========================================================================
df_melt2.columns
df_melt2.info()


## Numbers of competitions by categorical variable/integer (univariate)--------------------
### Pandas
#sorted values
df_melt2.groupby('event')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('equipment')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('age_class')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('birth_year_class')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('division')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('lift')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('place')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('country')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('state')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('federation')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('meet_state')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('meet_town')['id'].nunique().sort_values(ascending=False)
df_melt2.groupby('meet_name')['id'].nunique().sort_values(ascending=False)

#plots
df_melt2.groupby('year')['id'].nunique().plot(kind='bar')
plt.show()
plt.close()

df_melt2.groupby('event')['id'].nunique().sort_values(ascending=False).plot(kind='bar')
plt.show()
plt.close()

df_melt2.groupby('age_class')['id'].nunique().plot(kind='bar')
plt.show()
plt.close()


### Seaborn
#functionalize this process
def make_barplot_ncomps(df, var, sort=False, tilt=False):
  #build DF of counts
  s_n = df.groupby(var)['id'].nunique()
  
  #sort values in descending order by n
  if sort:
    s_n.sort_values(ascending=False, inplace=True)
  
  #make barplot
  sns.barplot(x=s_n.index, y=s_n, order=s_n.index)
  
  #tilt x tickmarks
  if tilt:
    plt.xticks(rotation=90)
    
  #add labels
  plt.xlabel(var, fontsize=14)
  plt.ylabel("Number of competitions", fontsize=14)
  plt.show()
  plt.close()

#### event
#hard-coded
s_event_ids = df_melt2.groupby('event')['id'].nunique().sort_values(ascending=False)

sns.barplot(x=s_event_ids.index, y=s_event_ids, order=s_event_ids.index)
plt.show()
plt.close()

#by function
make_barplot_ncomps(df_melt2, 'event', sort=True)

#### year
make_barplot_ncomps(df_melt2, 'year', sort=True)

#### age_class
make_barplot_ncomps(df_melt2, 'age_class', sort=False, tilt=True)

#### equipment
make_barplot_ncomps(df_melt2, 'equipment')

#### federation
make_barplot_ncomps(df_melt2, 'federation', sort=True, tilt=True)


### Numerical only (univariate)--------------------
df_melt2.info()
#age, bodyweight_kg, mass_kg, dots, wilks, glossbrenner, goodlift

#create function
def make_hist(df, var, lift=pd.NA, col='darkblue'):
  #convert to DF of unique records of variable
  if var=='mass_kg':
    df1 = df[df['lift']==lift]
  else:
    df1 = df[['id', var]].drop_duplicates()
  
  #plot histogram
  sns.histplot(x=var, color=col, data=df1)
  plt.xlabel(var, fontsize=14)
  plt.ylabel('Count', fontsize=14)
  plt.show()
  plt.close()


#### age
#hard-coded
df_age = df_melt2[['id', 'age']].drop_duplicates()
sns.histplot(x='age', color='darkblue', data=df_age)
plt.xlabel('age', fontsize=14)
plt.ylabel('Count', fontsize=14)
plt.show()
plt.close()

#by function
make_hist(df_melt2, 'age')
make_hist(df_melt2, 'bodyweight_kg', col='darkred')
make_hist(df_melt2, 'dots', col='darkgreen')
make_hist(df_melt2, 'wilks', col='purple')
make_hist(df_melt2, 'glossbrenner', col='darkorange')
make_hist(df_melt2, 'goodlift', col='turquoise')

#lifts
make_hist(df_melt2, var='mass_kg', lift='best3_bench', col='brown')
make_hist(df_melt2, var='mass_kg', lift='best3_deadlift', col='seagreen')
make_hist(df_melt2, var='mass_kg', lift='best3_squat', col='red')
make_hist(df_melt2, var='mass_kg', lift='total', col='violet')


## Bivariate numerical relationships--------------------
df_melt2.info()

#age, bodyweight_kg, mass_kg, dots, wilks, glossbrenner, goodlift

### Develop function
def make_scatter(df, varx='mass_kg', vary='mass_kg', liftx=pd.NA, lifty=pd.NA, 
                 pt_col='darkblue', line_col='green'):
  #scenario 1: both vars are 'mass_kg'
  if varx=='mass_kg' and vary=='mass_kg':
    df1 = df[df['lift'].isin([liftx, lifty])]
    df2 = df1[['id', 'lift', 'mass_kg']].pivot(index='id', columns='lift', values='mass_kg')
    
    sns.lmplot(x=liftx, y=lifty, ci=95, data=df2,
             scatter_kws={'color': pt_col,
                          'alpha': 0.2},
             line_kws={'color': line_col})
    plt.xlabel(liftx, fontsize=14)
    plt.ylabel(lifty, fontsize=14)
    plt.show()
    plt.close()
  #scenarios 2-4: either 0 or 1 var is 'mass_kg'
  else:
    if varx=='mass_kg':
      df1 = df[df['lift']==liftx]
      df2 = df1[['id', varx, vary]]
      labx = liftx
      laby = vary
    elif vary=='mass_kg':
      df1 = df[df['lift']==lifty]
      df2 = df1[['id', varx, vary]]
      labx = varx
      laby = lifty
    else:
      df2 = df[['id', varx, vary]].drop_duplicates()
      labx = varx
      laby = vary
      
    sns.lmplot(x=varx, y=vary, ci=95, data=df2,
               scatter_kws={'color': pt_col,
                            'alpha': 0.2},
               line_kws={'color': line_col})
    plt.xlabel(labx, fontsize=14)
    plt.ylabel(laby, fontsize=14)
    plt.show()
    plt.close()
  

#### Hard-coded
#age-wilks
df_age_wilks = df_melt2[['id', 'age', 'wilks']].drop_duplicates()
sns.lmplot(x='age', y='wilks', ci=95, data=df_age_wilks,
           scatter_kws={'color': 'darkblue',
                        'alpha': 0.2},
           line_kws={'color': 'green'})
plt.xlabel('age', fontsize=14)
plt.ylabel('wilks', fontsize=14)
plt.show()
plt.close()


#by function
make_scatter(df_melt2, varx='age', vary='wilks')
make_scatter(df_melt2, varx='bodyweight_kg', vary='dots')

make_scatter(df_melt2, liftx='best3_bench', lifty='best3_squat')
make_scatter(df_melt2, varx='age', lifty='best3_bench')

make_scatter(df_melt2, liftx='best3_bench', vary='bodyweight_kg')



## Bivariate categorical-numerical relationships--------------------
df_melt2.info()
#categorical: event, equipment, age_class, birth_year_class, division, lift, place, country, state,
  #federation, year (integer but categorical), meet_state, meet_town, meet_name

#numerical: age, bodyweight_kg, mass_kg, dots, wilks, glossbrenner, goodlift

### Create function
def make_boxplot(df, varx, vary='mass_kg', lifty=pd.NA):
  if vary=='mass_kg':
    df1 = df[df['lift']==lifty]
    df2 = df1[['id', varx, vary]]
    laby = lifty + '_kg'
  else:
    df2 = df[['id', varx, vary]].drop_duplicates()
    laby = vary
    
  sns.boxplot(x=varx, y=vary, data=df2)
  plt.xlabel(varx, fontsize=14)
  plt.ylabel(laby, fontsize=14)
  plt.show()
  plt.close()



### Hard-coded
#event-age
df_event_age = df_melt2[['id', 'event', 'age']].drop_duplicates()
sns.boxplot(x='event', y='age', data=df_event_age)
plt.show()
plt.close()


### By function
make_boxplot(varx='event', vary='age', df=df_melt2)
make_boxplot(varx='equipment', vary='wilks', df=df_melt2)
make_boxplot(varx='equipment', lifty='best3_bench', df=df_melt2)
make_boxplot(varx='federation', lifty='total', df=df_melt2)
make_boxplot(varx='year', vary='age', df=df_melt2)



# TO DO:
#1) Move the custom functions to a separate script and import them into this script
#2) Modify functions to accept a year filter (with default being no filter for all years)
#3) Began to build dashboard
  #1. Options
    #Toggle by year: 2021-2024 or all
    #Toggle by lift: best3_bench, best3_deadlift, best3_squat, and total
  #2. Top border (2)
    #Max [lift]: 
    #Min [lift]:
  #3. Plots (4)
    #Upper left: histogram
    #Upper right: boxplot with equipment
    #Lower left: scatterplot with age
    #Lower right: scatterplot with wilks

 


