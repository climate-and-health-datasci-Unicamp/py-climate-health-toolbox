# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 21:52:54 2020

@author: Daniela Souza de Oliveira

Module to compute Heat Waves and Cold Waves
This algorithm receives a climatic normal and a database in order to calculate Heat Waves and Cold Waves
using the method of Geirinhas et al.

"""
import pandas as pd
import numpy as np
import datetime
import more_itertools as mit
from datetime import timedelta
from calendar import isleap
    
#-------------------------------------------------------------------------------
## Function to add missing dates in a dataframe 
## This is done in order to fill the dates of all years contained in the dataframe
##
## :param      df:   Dataframe containing the database
## :type       df:   pandas.DataFrame
##
## :returns:   df Completed dataframe
## :rtype:     pandas.DataFrame
##
def complete_df(df):
    df=df.set_index('DATE')
    year1=df.index.year.min() # identify first year of the dataframe
    year2=df.index.year.max() # identify last year of the dataframe
    begin_date = datetime.date(year1,1,1) # define first date of df according to year1
    end_date = datetime.date(year2,12,31) # define last date of df according to year2
    date_index = pd.date_range(start=begin_date, end=end_date) # creates a date range between begin_date and end_date
    
    df=df.reindex(date_index) # reindex df without missing its original content
    
    df.index.name='DATE' # rename the index as 'DATE'
    
    df=df.reset_index()
        
    return df # returns complete df

#-------------------------------------------------------------------------------
## Function that removes leap day out of the dataframe 
## IF df contains only the column 'DATE', it removes the day 29-02 
## IF df contains also the column 'DAY365', this function also updates this column by decrementing 1 for dates
## after leap day
##
## :param      df:             Dataframe containing climatic normal/database
##                             with column 'DATE' and, optionally, also the column 'DAY365'
## :type       df:             pandas.DataFrame
##
## :returns:   df with leap day removed
## :rtype:     pandas.DataFrame
##
def drop_leapday(df):
    df=df.set_index(['DATE']) 
    
    for year in df.index.year.unique(): 
        if (isleap(year)): #checks if there is a leap year
            df = df[~((df.index.month==2) & (df.index.day==29))] #removes leap day
            begin_date = datetime.date(year,3,1) 
            end_date = datetime.date(year,12,31)
            df.loc[begin_date:end_date,['DAY365']]-=1 #decrement 1 from the days after the leap day
            
    df=df.reset_index()
            
    return df

#-------------------------------------------------------------------------------
## This function converts a date to a day of the year and stores it in the
## column 'DAY365'
##
## :param      df:   Dataframe containing the database
## :type       df:   pandas.DataFrame
##
## :returns:   df Dataframe incluing the column 'DAY365'
## :rtype:     pandas.DataFrame
##
def date_toDay365(df):
    df['DAY365']=df['DATE'].dt.dayofyear #creates the column 'DAY365' storing the day of the year for the corresponding date

    return df

#-------------------------------------------------------------------------------
## Function that converts day of the year and year to a date
##
## :param      day365:  Day of the year
## :type       day365:  Integer (1 to 365)
## :param      year:    The year
## :type       year:    Integer
##
## :returns:   new_date, corresponding date
## :rtype:     datetime.date
##
def day365_toDate(day365, year):
    new_date = datetime.date(year, 1, 1) + datetime.timedelta(day365-1)
           
    return new_date

#-------------------------------------------------------------------------------
## Function that calculates the percentile of a certain column from the climatic normal dataframe 
## The percentile is calculated for each day of the year, for all years in the dataframe, 
## considering a window of a certain size centered on the day in question
##
## :type       climatic_normal:   pandas.DataFrame
## :param      climatic_normal:   The climatic normal with 'DATE', pct_column
##                                and 'DAY365' column
## :type       day365_index:      Integer
## :param      day365_index:      The day365 index
## :type       pct_column:        String
## :param      pct_column:        Name of the column from the climatic normal
##                                used to calculate the percentile
## :type       percentile_value:  Float
## :param      percentile_value:  The percentile value (0 to 1.0)
## :type       window_size:       Integer
## :param      window_size:       The size of the window used to calculate the
##                                percentile (e.g. 15)
##
## :returns:   Climatic normal including a column with the percentile values
## :rtype:     pandas.DataFrame
##
def get_percentile(climatic_normal,day365_index,pct_column,percentile_value,window_size):
    pct_window = None #empty percentile window
    
    window_delta_amount = (window_size-1)/2 # obtains the interval of days before and after the day in question
    window_delta = timedelta(days=window_delta_amount) #transforms the interval of days in a timedelta allowing date operations
    
    climatic_normal=climatic_normal.set_index(['DATE']) #sets the index of the climatic normal on the column 'DATE'
           
    for year in climatic_normal.index.year.unique():
        current_date = day365_toDate(day365_index,year) #gets the current date based on the day365 and the year
        begin_date = current_date - window_delta #calculates the initial date of the window centered on current_date
        end_date = current_date + window_delta #calculates the final date of the window centered on current_date
        aux = climatic_normal.loc[begin_date:end_date] #extracts the window of the days from the climatic normal dataframe
        if pct_window is None: # if pct_window is empty
            pct_window = aux #pct_window receives 'aux' directly
        else:
            pct_window = pct_window.append(aux) #otherwise it appends 'aux' to pct_window
    return pct_window[pct_column].quantile(percentile_value)  #after extracting the window centered on the current_date for all years of the dataframe
    #it calculates the percentile of the window based on the pct_column

#-------------------------------------------------------------------------------
## This function checks if the values from a column of the database are above
## the values of the percentiles dataframe obtained from the get_percentile
## function, if a value is above the pct, the column 'above_pct' receives 1 and
## 0 otherwise 
## It checks if the maximum temperature is above the Tmax percentile (column 'CTX_pct') 
## and the mininum temperaturature is above the Tmin percentile (column 'CTN_pct') 
## CTX90pct and CTN90pct were chosen in this code (90th percentile)
##
## :param      database:      The database with 'DATE','db_column' and 'DAY365'
##                            column (in case it doesn't have this column, check
##                            date_toDay365 function)
## :type       database:      pandas.DataFrame
## :param      df_pct:        The df pct - dataframe with the percentiles
## :type       df_pct:        pandas.DataFrame
## :param      db_columnMAX:  The column of the database with maximum
##                            temperatures to be compared with CTX_pct
## :type       db_columnMAX:  String
## :param      db_columnMIN:  The column of the database with minimum
##                            temperatures to be compared with CTN_pct
## :type       db_columnMIN:  String
##
## :returns:   The database including the column 'above_pct' .
## :rtype:     pandas.DataFrame
##
def get_abovePct(database,df_pct,db_columnMAX,db_columnMIN):
    df_aux=pd.DataFrame()
    database=database.set_index(['DAY365']) #set 'DAY365' column as the index
    for year in database.DATE.dt.year.unique(): #for every year in the database
        df_year = database[database.DATE.dt.year == year]
        df_year['above_pct'] = np.where(((df_year[db_columnMAX] >= df_pct['CTX90pct']) & (df_year[db_columnMIN] >= df_pct['CTN90pct'])), 1, 0) #checks if the value in db_column is equal or higher than the corresponding percentile
        #column 'above_pct' receives 1 if the condition is satisfied otherwise it receives 0
        if df_aux is None: #if df_aux is empty
            df_aux = df_year #df_aux receives df_year
        else:
            df_aux=df_aux.append(df_year) #otherwise it appends df_year to df_aux
    
    df_aux=df_aux.reset_index()
    
    return df_aux

#-------------------------------------------------------------------------------
## This function checks if the values from a column of the database are below
## the values of the percentiles dataframe obtained from the get_percentile
## function, if a value is below the pct, the column 'below_pct' receives 1 and
## 0 otherwise
## It checks if the maximum temperature is below the Tmax percentile (CTX_pct) 
## and the mininum temperaturature is below the Tmin percentile (CTN_pct) 
## CTX10pct and CTN10pct were chosen in this code (10th percentile)
##
## :param      database:      The database with 'DATE','db_column' and 'DAY365'
##                            column (in case it doesn't have this column, check
##                            date_toDay365 function)
## :type       database:      pandas.DataFrame
## :param      df_pct:        The df pct - dataframe with the percentiles
## :type       df_pct:        pandas.DataFrame
## :param      db_columnMAX:  The column of the database with maximum temperatures to be compared with CTX_pct
## :type       db_columnMAX:  String
## :param      db_columnMIN:  The column of the database with minimum temperatures to be compared with CTN_pct
## :type       db_columnMIN:  String
##
## :returns:   The database including the column 'below_pct' . 
## :rtype:     pandas.DataFrame
##
def get_belowPct(database,df_pct,db_columnMAX,db_columnMIN):
    df_aux=pd.DataFrame()
    database=database.set_index(['DAY365'])
    for year in database.DATE.dt.year.unique():
        df_year = database[database.DATE.dt.year == year]
        df_year['below_pct'] = np.where(((df_year[db_columnMAX] <= df_pct['CTX10pct']) & (df_year[db_columnMIN] <= df_pct['CTN10pct'])), 1, 0) #checks if the value in db_column is equal or less than the corresponding percentile
        #column 'below_pct' receives 1 if the condition is satisfied otherwise it receives 0    
        if df_aux is None: #if df_aux is empty
            df_aux = df_year #df_aux receives df_year
        else:
            df_aux=df_aux.append(df_year) #otherwise it appends df_year to df_aux
            
    df_aux=df_aux.reset_index()
    
    return df_aux

#-------------------------------------------------------------------------------
## Function that checks heat/cold wave pattern in the column
## 'above_pct'/'below_pct', it verifies if there are 3 consecutive values
## above/below a certain percentile the column 'HW'/'CW' receives 1 for the days
## inside of a HW or CW and zero otherwise
##
## :type       df_wave:      pandas.DataFrame
## :param      df_wave:      Database dataframe containg column 'above_pct' or
##                           'below_pct'
## :type       wave_column:  String
## :param      wave_column:  Name of the column that is going to store information about Heat/Cold Waves (e.g. 'HW' or 'CW')
##
## :type       extremeDays_column:  String
## :param      extremeDays_column:  Name of the column that indicates days with extreme temperature ('above_pct' or 'below_pct')
##
## :returns:   database dataframe including column 'HW' or 'CW'
## :rtype:     pandas.DataFrame
##
def get_wave(df_wave,wave_column,extremeDays_column):
    check_pattern = df_wave.rolling(3)[extremeDays_column].apply(lambda x: all(np.equal(x, [1,1,1])),raw=True) #use rolling to check for the pattern 111 in the above_pct/below_pct column
    check_pattern = check_pattern.sum(axis = 1).astype(bool)
    pattern_idx = np.where(check_pattern)[0] #gets the index of the last ocurrence of '1' for each sequence
    
    subset = [range(idx-3+1, idx+1) for idx in pattern_idx] #gets the range of each  wave - the indexes of all 1's ocurrences in a sequence
     
    idx_list = [item for sublist in subset for item in sublist] #converts the subset list of ranges in a list of indexes
    
    idx_list=list(set(idx_list)) #removes the repetitive indexes 
    
    df_wave[wave_column]=0 # create column HW for heatwave or CW for coldwave
    df_wave[wave_column].iloc[idx_list]=1 #stores 1 in the column defined above for the indexes involved in a heat wave

    return df_wave 

#-------------------------------------------------------------------------------
## Checks for Heat Waves on the database according to the Climatic Normal This
## function uses Geirinhas et al. method It obtains first a dataframe with the
## percentiles computed from the Climatic Normal according to the defined window
## size Then compares it with the database, to check if the maximum and minimum
## temperatures are above the corresponding percentile If the temperatures are
## above the threshold, the column 'above_pct' receives 1 This column is then
## used to identify if there are 3 or more consecutive extremely warm days (Heat
## Wave) The column 'HW' then receives 1 for the days that are inside of a Heat
## Wave
##
## Climatic Normal dataframe needs to have at least 'DATE' and 'pct_column'
## Database dataframe needs to have at least 'DATE' and 'db_column' IF either or
## one of those dataframes don't have the 'DAY365' column (day of the year
## column), cn_columnDay365 and/or db_columnDay365 parameters must be 0,
## otherwise 1
##
## If there are missing dates on the database, db_complete parameter must be 0,
## otherwise 1
##
## :type       climatic_normal:   pandas.DataFrame
## :param      climatic_normal:   The climatic normal
## :type       pct_columnMAX:     String
## :param      pct_columnMAX:     Name of the column from the climatic normal
##                                used to calculate the percentile for maximum
##                                temperatures
## :type       pct_columnMIN:     String
## :param      pct_columnMIN:     Name of the column from the climatic normal
##                                used to calculate the percentile for minimum
##                                temperatures
## :type       cn_columnDay365:   Integer (0 or 1)
## :param      cn_columnDay365:   Indicates if the climatic normal has the
##                                Day365/day of the year column (cn_columnDay365
##                                = 1) or not (cn_columnDay365 = 0)
## :type       database:          pandas.DataFrame
## :param      database:          The database
## :type       db_columnMAX:      String
## :param      db_columnMAX:      Name of the column of the database with
##                                maximum temperatures to be compared with
##                                CTX_pct
## :type       db_columnMIN:      String
## :param      db_columnMIN:      Name of the column of the database with
##                                minimum temperatures to be compared with
##                                CTN_pct
## :type       db_columnDay365:   Integer (0 or 1)
## :param      db_columnDay365:   Indicates if the database has the Day365/day
##                                of the year column (db_columnDay365 = 1) or
##                                not (db_columnDay365 = 0)
## :type       db_complete:       Integer (0 or 1)
## :param      db_complete:       Indicates if the database has missing dates
##                                (db_complete = 0) or not (db_complete = 1)
## :type       percentile_value:  Float
## :param      percentile_value:  The percentile value (0 to 1.0)
## :type       window_size:       Integer
## :param      window_size:       The size of the window used to calculate the
##                                percentile exp
##
## :returns:   df_checkHW -> database dataframe including columns 'above_pct'
##             and 'HW'
## :rtype:     pandas.DataFrame
##
def check_HeatWave(climatic_normal,pct_columnMAX,pct_columnMIN,cn_columnDay365,database,db_columnMAX,db_columnMIN,db_columnDay365,db_complete,percentile_value,window_size):
    
    if not db_complete:#in case db is incomplete - with missing dates
        database=complete_df(database) #add the missing dates without altering original db

    if not cn_columnDay365: #in case there is no 'DAY365' column
        climatic_normal = date_toDay365(climatic_normal) #add column 'DAY365' to the dataframe
    if not db_columnDay365: #in case there is no 'DAY365' column
        database = date_toDay365(database) #add column 'DAY365' to the dataframe

    climatic_normal = drop_leapday(climatic_normal) #removes leap day from climatic normal
    database = drop_leapday(database) #removes leap day from the database    

    df_pct = pd.DataFrame() #creates a dataframe to store the percentiles
    df_pct['DAY365']=range(1,366) #creates 'DAY365' column with each row receiving values 1 to 365
    df_pct=df_pct.set_index(['DAY365']) # 'DAY365' is set as index

    df_pct['CTX90pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMAX,percentile_value,window_size))
    df_pct['CTN90pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMIN,percentile_value,window_size))
    #column 'percentiles'of df_pct receive the value of percentiles according to pct_column

    df_wave = get_abovePct(database,df_pct,db_columnMAX,db_columnMIN) #df_wave receives the database plus 'above_pct' column
    
    df_checkHW=get_wave(df_wave,'HW','above_pct') #df_checkHW receives the database plus 'above_pct' column and wave_column 'HW' column
    
    return df_checkHW


#-------------------------------------------------------------------------------
## Checks for Cold Waves on the database according to the Climatic Normal
##
## Checks for Cold Waves on the database according to the Climatic Normal This
## function uses Geirinhas et al. method It obtains first a dataframe with the
## percentiles computed from the Climatic Normal according to the defined window
## size Then compares it with the database, to check if the maximum and minimum
## temperatures are below the corresponding percentile If the temperatures are
## above the threshold, the column 'below_pct' receives 1 This column is then
## used to identify if there are 3 or more consecutive extremely cold days (Cold
## Wave) The column 'CW' then receives 1 for the days that are inside of a Cold
## Wave
##
## Climatic Normal dataframe needs to have at least 'DATE' and 'pct_column'
## Database dataframe needs to have at least 'DATE' and 'db_column' IF either or
## one of those dataframes don't have the 'DAY365' column (day of the year
## column), cn_columnDay365 and/or db_columnDay365 parameters must be 0,
## otherwise 1
##
## If there are missing dates on the database, db_complete parameter must be 0,
## otherwise 1
##
## :type       climatic_normal:   pandas.DataFrame
## :param      climatic_normal:   The climatic normal
## :type       pct_columnMAX:     String
## :param      pct_columnMAX:     Name of the column from the climatic normal
##                                used to calculate the percentile for maximum
##                                temperatures
## :type       pct_columnMIN:     String
## :param      pct_columnMIN:     Name of the column from the climatic normal
##                                used to calculate the percentile for minimum
##                                temperatures
## :type       cn_columnDay365:   Integer (0 or 1)
## :param      cn_columnDay365:   Indicates if the climatic normal has the
##                                Day365/day of the year column (cn_columnDay365
##                                = 1) or not (cn_columnDay365 = 0)
## :type       database:          pandas.DataFrame
## :param      database:          The database
## :type       db_columnMAX:      String
## :param      db_columnMAX:      Name of the column of the database with
##                                maximum temperatures to be compared with
##                                CTX_pct
## :type       db_columnMIN:      String
## :param      db_columnMIN:      Name of the column of the database with
##                                minimum temperatures to be compared with
##                                CTN_pct
## :type       db_columnDay365:   Integer (0 or 1)
## :param      db_columnDay365:   Indicates if the database has the Day365/day
##                                of the year column (db_columnDay365 = 1) or
##                                not (db _columnDay365 = 0)
## :type       db_complete:       Integer (0 or 1)
## :param      db_complete:       Indicates if the database has missing dates
##                                (db_complete = 0) or not (db_complete = 1)
## :type       percentile_value:  Float
## :param      percentile_value:  The percentile value (0 to 1.0)
## :type       window_size:       Integer
## :param      window_size:       The size of the window used to calculate the
##                                percentile exp
##
## :returns:   df_checkCW -> database dataframe including columns 'below_pct'
##             and 'CW'
## :rtype:     pandas.DataFrame
##
def check_ColdWave(climatic_normal,pct_columnMAX,pct_columnMIN,cn_columnDay365,database,db_columnMAX,db_columnMIN,db_columnDay365,db_complete,percentile_value,window_size):
    
    if not db_complete:#in case db is incomplete - with missing dates
        database=complete_df(database) #add the missing dates without altering original db

    if not cn_columnDay365: #in case there is no 'DAY365' column
        climatic_normal = date_toDay365(climatic_normal) #add column 'DAY365' to the dataframe
    if not db_columnDay365: #in case there is no 'DAY365' column
        database = date_toDay365(database) #add column 'DAY365' to the dataframe

    climatic_normal = drop_leapday(climatic_normal) #removes leap day from climatic normal
    database = drop_leapday(database) #removes leap day from the database

    df_pct = pd.DataFrame() #creates a dataframe to store the percentiles
    df_pct['DAY365']=range(1,366) #creates 'DAY365' column with each row receiving values 1 to 365
    df_pct=df_pct.set_index(['DAY365']) # 'DAY365' is set as index

    df_pct['CTX10pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMAX,percentile_value,window_size))
    df_pct['CTN10pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMIN,percentile_value,window_size))
    
    df_wave = get_belowPct(database,df_pct,db_columnMAX,db_columnMIN) #df_wave receives the database plus 'below_pct' column
    
    df_checkCW=get_wave(df_wave,'CW','below_pct') #df_checkW receives the database plus 'below_pct' column and 'CW' column
    
    return df_checkCW

#-------------------------------------------------------------------------------
## Function to obtain the metrics of a Heat/Cold Wave given the database dataframe containing the 'HW'/'CW' column
## that indicates if a day is inside of a Heat/Cold Wave or not -> check get_wave function
## This function obtains the wave duration for each year (HWN) of the database and then computes its maximum duration (HWD)
## and its intensity - sum of wave durations (HWF)
## These metrics are stored in a dataframe which includes the Heat/Cold Wave metrics for each year of the database
## :param      df_checkW:    Database dataframe with 'HW'/'CW' column
## :type       df_checkW:    pandas.DataFrame
## :param      wave_column:  Name of the column containing information about Heat/Cold Waves
## :type       wave_column:  String
##
## :returns:   df_waveMetrics Dataframe containing wave metrics for each year of the database
## :rtype:     pandas.DataFrame
##
def wave_metrics(df_checkW,wave_column):
    counter=0 
    waveDuration=[]
    df_waveMetrics=pd.DataFrame()
    n_waves = wave_column+str('N')
    maxd_waves = wave_column+str('D')
    sum_waves = wave_column+str('F')
    df_waveMetrics['YEAR']=df_checkW.DATE.dt.year.unique() #column 'year' of the df receives the years from the database
    df_waveMetrics=df_waveMetrics.set_index(['YEAR']) #column 'year' is set as index
    for year in df_checkW.DATE.dt.year.unique():
        df_year = df_checkW[df_checkW.DATE.dt.year == year] #auxiliar dataframe to store the current year
        wave_idx = np.flatnonzero(df_year[wave_column]) #gets the indexes of the days involved in a Heat/Cold wave
        for group in mit.consecutive_groups(wave_idx): #according to the indexes it separates each heat/cold wave in a group
            counter+=1 #counts the number of groups - number of Heat/Cold waves
            waveDuration.append(len(list(group))) #stores the duration of waves in a list
        df_waveMetrics.loc[year,n_waves]=counter #stores in the df the number of waves
        if not waveDuration: #in case there in no heat/cold wave
            df_waveMetrics.loc[year,maxd_waves]=0 #store 0 as the maximum duration
            df_waveMetrics.loc[year,sum_waves]=0 #store 0 as the sum of durations
        else:
            df_waveMetrics.loc[year,maxd_waves]=max(waveDuration) #stores in the df the maximum wave duration
            df_waveMetrics.loc[year,sum_waves]=sum(waveDuration) #stores in the df the sum of wave durations
        counter=0 #reinitialize the counter
        waveDuration=[] #reinitialize the list
    
    return df_waveMetrics


