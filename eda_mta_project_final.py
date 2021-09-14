#!/usr/bin/env python
# coding: utf-8

# ### Creation of database in SQLite

# In[1]:


# create database in terminal
'''
sqlite mta_data.db
'''

# add column information to data base in terminal
'''
CREATE TABLE mta_data
(CA TEXT,
UNIT TEXT,
SCP TEXT,
STATION TEXT,
LINENAME TEXT,
DIVISION TEXT,
DATE TEXT,
TIME TEXT,
DESC TEXT,
ENTRIES INTEGER,
EXITS INTEGER,
PRIMARY KEY (CA, UNIT, SCP, STATION, LINENAME, DIVISION, DATE, TIME, DESC, ENTRIES, EXITS));
'''


# ### Scrape data from the MTA website

# In[2]:


# get csv files of all the week i need with python
def get_data(week_nums):
    url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_{}.txt" #url with formatting to fill in the number of the particular week
    dfs = []
    for week_num in week_nums: #for each week
        file_url = url.format(week_num) #format the url so it grabs that week
        dfs.append(pd.read_csv(file_url)) #append to our empty list
    return pd.concat(dfs) #combine files for each week
        
week_nums = [210306, 210313, 210320, 210327, 210403, 210410, 210417, 210424, 210501, 210508, 210515, 210522, 210529]
mta = get_data(week_nums)


# ### Import necessary packages

# In[3]:


from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import datetime

get_ipython().run_line_magic('matplotlib', 'inline')


# ### Data exploration with SQLAlchemy

# In[4]:


# create engine with SQLAlchemy
engine = create_engine("sqlite:////Users/stanguo/NBM_EDA/MTA_EDA_Project/mta_data.db")


# In[5]:


# read database into jupyter
mta = pd.read_sql('SELECT * FROM mta_data;', engine)


# In[6]:


pd.read_sql('SELECT * FROM mta_data GROUP BY STATION ORDER BY ENTRIES;', engine)


# In[7]:


pd.read_sql('SELECT * FROM mta_data WHERE station = "168 ST" GROUP BY linename;', engine)


# In[8]:


pd.read_sql('SELECT station, LENGTH(division) AS "NUMBER_OF_DIVISIONS" FROM mta_data;', engine)


# In[9]:


pd.read_sql('SELECT COUNT(station) linename FROM mta_data GROUP BY station HAVING COUNT(linename) > 3;', engine)


# In[10]:


pd.read_sql('SELECT * FROM mta_data WHERE linename LIKE("%6%");', engine)


# ### Data exploration with Pandas

# In[11]:


# check to see if mta df loads
mta


# In[12]:


# get info about df, show_counts = True is used to display Non_Null Count, all Non_Null Counts are the same,
# means that there are no missing values
mta.info(show_counts = True)


# In[13]:


mta.shape


# In[14]:


mta.columns


# In[15]:


# get the number of rows for each date, .sort_index is used to sort the index in ascending order
mta['DATE'].value_counts().sort_index()


# ### Create a new column titled DATETIME in the MTA dataframe

# In[16]:


mta['DATETIME'] = pd.to_datetime(mta['DATE'] + ' ' + mta['TIME'], format = '%m/%d/%Y %H:%M:%S')
mta


# ### Check for duplicates in our dataframe

# In[17]:


(mta.groupby(['CA', 'UNIT', 'SCP', 'STATION', 'DATETIME'])
 .EXITS.count()
 .reset_index()
 .sort_values('EXITS', ascending = False)
 .head()
)

# looks like there are duplicates, some rows have EXITS values of 2 meaning there are two entries for the EXIT
# value in the mta df


# In[18]:


# get more detail on a duplciate row by setting a filter and locating it
mask_dup = (
    (mta['CA'] == 'N071') &
    (mta['UNIT'] == 'R013') &
    (mta['SCP'] == '00-00-00') &
    (mta['STATION'] == '34 ST-PENN STA') &
    (mta['DATETIME'].dt.date == datetime.datetime(2021, 4, 8).date())
)

# locate filter
mta[mask_dup].head(10)

# from the results, it seems that duplicated rows with 2 EXITS entries have a DESC value of RECOVR AUD


# In[19]:


# check how many rows have a DESC value of RECOVR AUD
mta['DESC'].value_counts()


# In[20]:


mta_drop = mta.drop_duplicates(subset = ['CA', 'UNIT', 'SCP', 'STATION', 'DATETIME'])
mta_drop = mta_drop[mta_drop['DESC'] == 'REGULAR'] # **
mta_drop.head(10)


# In[21]:


# it seems that the duplicates have been dropped but to make sure, we check the number of
# unique values in the DESC column
mta_drop['DESC'].nunique()


# In[22]:


# within the new filter where the dupes have been dropped, check for duplicates
(mta_drop.groupby(['CA', 'UNIT', 'SCP', 'STATION', 'DATETIME'])
 .EXITS.count()
 .reset_index()
 .sort_values('EXITS', ascending = False)
 .head()
)


# ### Get maximum exits per day for each unique turnstile around the city

# In[23]:


# create a new df called mta_dailymax from mta_drop df to get the max entries per day, per turnstile
mta_dailymax = (mta_drop.groupby(['CA', 'UNIT', 'SCP', 'STATION', 'DATE'], as_index = False)
                .EXITS.max()
               )

mta_dailymax

# mta_dailymax results reads as following: for this specific turnstile at this specific station, regardless of time
# the max number of exits is 'X'


# In[24]:


# using mta_dailymax, for each turnstile see previous day's exits
mta_dailymax[['PREV_DATE', 'PREV_EXITS']] = (mta_dailymax.groupby(['CA', 'UNIT', 'SCP', 'STATION'])
                                             [['DATE', 'EXITS']]
                                             .shift(1)
                                            )
mta_dailymax


# In[25]:


# drop the first row containing NaN
# exits are in order bc we sorted by exits.max
mta_dailymax.dropna(subset = ['PREV_DATE'], inplace = True)
mta_dailymax


# In[26]:


# check to see which rows where unique daily turnstile exits are less than previous daily exits
neg_exit_change = (mta_dailymax['EXITS'] < mta_dailymax['PREV_EXITS'])
mta_dailymax[neg_exit_change]


# In[27]:


# 218 turnstiles have PREV_EXITS greater than EXITS
(mta_dailymax[mta_dailymax['EXITS'] < mta_dailymax['PREV_EXITS']]
 .groupby(["CA", "UNIT", "SCP", "STATION"])
 .size()
)


# In[28]:


# fix the counter issue from above line
def get_daily_counts(row, max_counter):
    counter = row['EXITS'] - row['PREV_EXITS']
    if counter < 0:
        counter = -counter
    if counter > max_counter:
        #print(row["ENTRIES"], row["PREV_ENTRIES"])
        counter = min(row['EXITS'], row['PREV_EXITS'])
    if counter > max_counter:
        # Check it again to make sure we're not still giving a counter that's too big
        return 0
    return counter

mta_dailymax['DAILY_EXITS'] = mta_dailymax.apply(get_daily_counts, axis = 1, max_counter = 1000000)


# ### Get total number of exits for each station over the three-month period

# In[29]:


mta_daily_sum = mta_dailymax.groupby(['STATION'])[['DAILY_EXITS']].sum().reset_index().rename(columns = {'DAILY_EXITS' : 'SUM_DAILY_EXITS'})
busiest = mta_daily_sum.sort_values('SUM_DAILY_EXITS', ascending = False).head(6)
busiest


# In[35]:


x = busiest.STATION
y = busiest.SUM_DAILY_EXITS

sns.barplot(x = x, y = y, data = busiest)
sns.set(style = 'ticks')
plt.title('Busiest Subway Stations in NYC (Exits) 03/06/2021 - 05/29/2021')
plt.xlabel('Total Exits')
plt.xticks(rotation = 90)
plt.ylabel('Station')
plt.ticklabel_format(style = 'plain', axis = 'y')
plt.savefig('busiest_mta_stations.png');


# ### Get total number of exits for each station on each day of the week over the three-month period

# In[31]:


# create new column in mta_dailymax titled 'DAY_OF_WEEK'
mta_dailymax['DAY_OF_WEEK'] = pd.to_datetime(mta_dailymax['DATE']).dt.weekday
mta_dailymax


# In[32]:


# select top 5 busiest stations from sns plot
# we don't use '34 ST-HERALD SQ' because it is too close in proximity to '34 ST-PENN STA'
# 'GRD CNTRL-42 ST' will takes its place

busiest_sta = ((mta_dailymax['STATION'] == '34 ST-PENN STA') |
               (mta_dailymax['STATION'] == '23 ST') |
               (mta_dailymax['STATION'] == '125 ST') |
               (mta_dailymax['STATION'] == '86 ST') |
               (mta_dailymax['STATION'] == 'GRD CNTRL-42 ST')
              )
                
days = {0 : 'Mon', 1 : 'Tue', 2 : 'Wed', 3 : 'Thu', 4 : 'Fri', 5 : 'Sat', 6: 'Sun'}

mta_dailymax_total = (mta_dailymax[busiest_sta].groupby(['STATION', 'DAY_OF_WEEK'])
                      [['DAILY_EXITS']].sum()
                      .reset_index()
                      .rename(columns = {'DAILY_EXITS' : 'TOTAL_DAILY_EXITS'}))

mta_dailymax_total['DAY_OF_WEEK'] = mta_dailymax_total['DAY_OF_WEEK'].map(days)
mta_dailymax_total


# In[33]:


x = mta_dailymax_total['DAY_OF_WEEK']
y = mta_dailymax_total['TOTAL_DAILY_EXITS']

sns.lineplot(x = x, y = y, hue = mta_dailymax_total['STATION'], data = mta_dailymax_total)
sns.set(style = 'ticks')
plt.title('Top 5 Busiest Subway Stations in NYC By Day (Exits) - 03/06/2021 to 05/29/2021')
plt.xlabel('Day')
plt.ylabel('Total Exits')
plt.legend()
plt.ticklabel_format(style = 'plain', axis = 'y')


# In[34]:


# plot top five busiest stations on each day of the week
x = mta_dailymax_total['DAY_OF_WEEK']
y = mta_dailymax_total['TOTAL_DAILY_EXITS']

sns.barplot(x = x, y = y, hue = mta_dailymax_total['STATION'] ,data = busiest)
sns.set(style = 'ticks')
plt.legend()
plt.title('Top 5 Busiest Subway Stations in NYC By Day (Exits) - 03/06/2021 to 05/29/2021')
plt.xlabel('Total Exits')
plt.ylabel('Day')
plt.ticklabel_format(style = 'plain', axis = 'y')
plt.savefig('busiest_mta_stations_day.png');

