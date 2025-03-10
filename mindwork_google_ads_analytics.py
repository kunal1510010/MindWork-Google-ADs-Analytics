# -*- coding: utf-8 -*-
"""MindWork Google ADs Analytics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1krf0Tl4P3bUUyoQdjo3euB8sHRU-_9lx

# Data Munging

Data wrangling, sometimes referred to as data munging, is the process of transforming and mapping data from one "raw" data form into another format with the intent of making it more appropriate and valuable for a variety of downstream purposes such as analytics.
"""

import pandas as pd  #importing pandas for data processing 
import numpy as np   #importing numpy for mathematical computation


import re            #importing Regular Expressions

    
import spacy         #importing spacy for natural language processing

nlp = spacy.load('en_core_web_sm')  #loading english grammer and rules

from scipy import stats    #importing stats for Chi-Square test


import warnings
warnings.filterwarnings("ignore")

data = pd.read_excel('DFP.xlsx', sheet_name = 'Data')

"""#Task 1

Dataset: ​Google Ad Manager Data ( DFP.xlsx ) 
1. Create the following columns, from the ​Ad_unit_name column in the dataset:

   a. amp_or_non_amp b. story c. position 
 
Example: 1.1 CarToq_ad_first_story_pos_top (122380182)        story = first, position = top, Nonamp  1.2 amp-cartoq-bottom (21684306640)       story = None, position = bottom, Amp
"""

data.head(10)

data.shape

data.tail()

"""### Initialising the columns
  1. Postiton
  2. amp_or_non_amp
  3. story
"""

data['position'] = ''
data['amp_or_non_amp'] = ''
data['story'] = ''

"""### Spliting the text values based on the required positions and storing the data into particular column values"""

for i in range(data.shape[0]):
    if re.findall('amp', data['AD_UNIT_NAME'].iloc[i]):
        data['position'].iloc[i] = data['AD_UNIT_NAME'].iloc[i].split('-')[-1].split(' ')[0]
        data['amp_or_non_amp'].iloc[i] = 'Amp'
        data['story'] = 'None'
    else:
        data['position'].iloc[i] = data['AD_UNIT_NAME'].iloc[i].split('_')[-1].split(' ')[0]
        data['amp_or_non_amp'] = 'Nonamp'
        data['story'] = data['AD_UNIT_NAME'].iloc[i].split('_story')[0].split('_')[-1]

"""## Initialising the function to map dates with days"""

def days(number):
    dic = {1:'Monday',
          2:'Tuesday',
          3:'Wednesday',
          4:'Thursday',
          5:'Friday',
          6:'Saturday',
          7:'Sunday'}
    return dic[number]

"""## Using lambda functions to apply above function on the day data column"""

data['DAY'] = data['DAY'].apply(lambda x:days(x))

data.head(10)

"""## Loading the Actual_eCPM Data set

 Here, eCPM for some data is incorrect, Merge ​Actual_eCPM         data from the other sheet ( Actual_eCPM.csv ) such that new           column for ​Actual_eCPM is created. Create another column        Actual_Revenue​ which is defined as:  Actual_Revenue = Total Impression * Actual_eCPM 
 
(if not provided, take the given revenue in the dataset as           Actual_Revenue to fill the remaining ​Actual_Revenue column       data with it.)  
 
After completing the above 3 tasks save the results as          DFP_solution.csv
"""

actual_epcm = pd.read_csv('Actual_eCPM.csv')

actual_epcm.head()

"""## Merging the Actual_ecpm Dataset with DFP data Set"""

data = pd.merge(actual_epcm, data, on = 'LINE_ITEM_NAME')
data.head()

data['Actual_eCPM'] = data['Actual_eCPM'].replace('-', 0.0)
data['Actual_eCPM'] = data['Actual_eCPM'].apply(lambda x:float(x))

data['eCPM'] = data['eCPM'].replace('-', 0.0)

data['Actual_eCPM'] = data['Actual_eCPM'] + data['eCPM']

data.head()

data['Actual_Revenue'] = data['Actual_eCPM'] * data['Impressions']

"""## Exporting data into csv File"""

data.to_csv('DFP_solution.csv', index = False)

"""Identify the best-performing Ad position in terms of eCPM and          revenue, separately in amp and non-amp case. ( hint : while           merging the data keep in mind that [ eCPM = Actual Revenue *             1000 / Total Impressions ] and [ CTR = clicks / Total            impressions] , aggregating directly won’t help.)  Submit this result as ​Adpos.csv"""

amp = data[data['amp_or_non_amp'] == 'Amp']
non_amp = data[data['amp_or_non_amp'] == 'Nonamp']

amp.sort_values(by = ['Actual_Revenue', 'Actual_eCPM'], 
                ascending = False,
                inplace = True)

amp.head()

non_amp.head()

pd.concat([amp, non_amp]).to_csv('Adpos.csv', index = False)

"""# Task 2

**Statistical Analysis: Dataset: ​Google Ad Manager Data ( DFP.xlsx )** 
In this task, we want to test your familiarity with different statistical and              modeling concepts.  1. Analyze the dataset in as many ways possible ways, including          multivariate analysis, to generate insights for predictive       modeling. (Other suggestions for analysis – [ Correlation,        Covariance, ANOVA, Regression analysis, Hypothesis testing:      Student’s t-test, chi-square test (Generate Null and Alternate        hypothesis and find the significant relation)].
"""

data.describe()

data.isnull().sum()

data.corr()

chi2_stat, p_val, dof, ex = stats.chi2_contingency(data[['Actual_eCPM','Tags_served','Impressions','Clicks','CTR','Revenue','eCPM','Actual_Revenue']])

print("===Chi2 Stat===")
print(chi2_stat)
print("\n")
print("===Degrees of Freedom===")
print(dof)
print("\n")
print("===P-Value===")
print(p_val)
print("\n")
print("===Contingency Table===")
print(ex)

data.cov()

"""#Task 3

Text Processing and Sentiment Analysis: Dataset: ​Review data ( Review_Data_All.xlsx ) 
 1. Basic Text Processing (Case Conversions, Punctuation      Removal, Stop word Removal, Stemming, Lemmatization)
 2. Top 10 High-frequency words 
 3. Use a polarity score for the cleaned review data to calculate the            Percentage of Positive and Negative Reviews. (use polarity        score threshold of 0 to classify positive and negative)
 4. Identify Most Positive, Most Negative and a Neutral review         based on the score 
 5. Use Polarity score of 0 to classify reviews Positive and          Negative. Use this as the target variable. [Binary Encode] 
 6. Use logistic regression to identify the words with high         coefficients value.
"""

reviews = pd.read_excel('Review_Data_All.xlsx', sheet_name = 'Review Data')

reviews.head()

def natural_language(text):
    text = text.lower()
    text = re.sub('[0-9]*','',text)
    docx = nlp(text)
    temp = []
    for i in docx:
        if i.is_stop!=True and i.is_punct!=True:
            temp.append(i.lemma_)
    return ' '.join(temp)

reviews['cleaned_text'] = reviews['Review Paragarph'].apply(lambda x:natural_language(x))

words = ' '.join(reviews['cleaned_text'].values.tolist())
words = words.split(' ')
words = [x for x in words if x]

dic = {}
for i in words:
    if i not in dic.keys():
        dic[i] = 1
    else:
        dic[i] = dic[i] + 1

temp = pd.DataFrame()
temp['words'] = dic.keys()
temp['count'] = dic.values()
temp.sort_values(by = 'count', ascending = False, inplace = True)
temp = temp.head(10)
temp

reviews['Rating'] = reviews['Rating'].apply(lambda x:int(x))

reviews['nature'] = ''
for i in range(reviews.shape[0]):
    if reviews['Rating'].iloc[i] >= 4:
        reviews['nature'].iloc[i] = 'Positive'
    elif reviews['Rating'].iloc[i] <= 2:
        reviews['nature'].iloc[i] = 'Negative'
    elif reviews['Rating'].iloc[i] == 3:
        reviews['nature'].iloc[i] = 'Neutral'
    else:
        pass

print('Number of Positive Reviews: ', reviews[reviews['nature'] == 'Positive'].shape[0])
print('Number of Negative Reviews: ', reviews[reviews['nature'] == 'Negative'].shape[0])
print('Number of Neutral Reviews: ', reviews[reviews['nature'] == 'Neutral'].shape[0])

