#This script contains functions to help with plotting for the dashboard

# Load Packages=====================================================================================
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt




# EDA Functions=====================================================================================
## Make barplot
def make_barplot_ncomps(df, var, year=pd.NA, sort=False, tilt=False):
  #filter by year (if applicable)
  if pd.notna(year):
    df = df[df['year']==year]
  
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
  

## Make histogram
def make_hist(df, var, year=pd.NA, lift=pd.NA, col='darkblue'):
  #filter by year if populated
  if pd.notna(year):
    df = df[df['year']==year]
    
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


## Make scatterplot
def make_scatter(df, year=pd.NA, varx='mass_kg', vary='mass_kg', liftx=pd.NA, lifty=pd.NA, 
                 pt_col='darkblue', line_col='green'):
  #filter DF by year if populated
  if pd.notna(year):
    df = df[df['year']==year]
  
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


## Make boxplot
def make_boxplot(df, varx, vary='mass_kg', lifty=pd.NA, year=pd.NA):
  #filter DF by year if populated
  if pd.notna(year):
    df = df[df['year']==year]
  
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


















