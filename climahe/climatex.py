#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 22:16:11 2020

@author: Daniela Souza de Oliveira

Module to compute Heat Waves and Cold Waves
This algorithm receives a climatic normal and a database in order to calculate Heat Waves and Cold Waves 
using the method of Geirinhas et al.

"""
import pandas as pd
import numpy as np
import datetime
import more_itertools as mit

import matplotlib.pyplot as plt
from datetime import timedelta
from calendar import isleap
    
#-------------------------------------------------------------------------------
## Function to add missing dates in a dataframe. This is done in order to fill
## the dates of all years contained in the dataframe
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
## Function that removes leap day out of the dataframe. It removes the day 29-02
## and also updates this column by decrementing 1 for dates after leap day
##
## :param      df:   Dataframe containing climatic normal/database with column
##                   'DATE' and, optionally, also the column 'DAY365'
## :type       df:   pandas.DataFrame
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
## Function that calculates the percentile of a certain column from the climatic
## normal dataframe. The percentile is calculated for each day of the year, for
## all years in the dataframe, considering a window of a certain size centered
## on the day in question
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
## 0 otherwise. It checks if the maximum temperature is above the Tmax percentile
## (column 'CTX_pct') and the mininum temperaturature is above the Tmin
## percentile (column 'CTN_pct') CTX90pct and CTN90pct were chosen in this code
## (90th percentile)
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
    database.set_index(['DAY365'],inplace=True) #set 'DAY365' column as the index

    for year in database.DATE.dt.year.unique(): #for every year in the database
        df_year = database[database.DATE.dt.year == year]
        df_year.loc[:,'above_pct'] = 0
        mask_hw = (df_year[db_columnMAX] >= df_pct['CTX90pct']) & (df_year[db_columnMIN] >= df_pct['CTN90pct'])
        df_year.loc[mask_hw,'above_pct'] = 1 
        #checks if the value in db_column is equal or higher than the corresponding percentile
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
## 0 otherwise. It checks if the maximum temperature is below the Tmax
## percentile (CTX_pct) and the mininum temperaturature is below the Tmin
## percentile (CTN_pct) CTX10pct and CTN10pct were chosen in this code (10th
## percentile)
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
## :returns:   The database including the column 'below_pct' .
## :rtype:     pandas.DataFrame
##
def get_belowPct(database,df_pct,db_columnMAX,db_columnMIN):
    df_aux=pd.DataFrame()
    database.set_index(['DAY365'],inplace=True)
    
    for year in database.DATE.dt.year.unique():
        df_year = database[database.DATE.dt.year == year]
        df_year.loc[:,'below_pct'] = 0
        mask_cw = (df_year[db_columnMAX] <= df_pct['CTX10pct']) & (df_year[db_columnMIN] <= df_pct['CTN10pct'])
        df_year.loc[mask_cw,'below_pct'] = 1
        #checks if the value in db_column is equal or less than the corresponding percentile
        #column 'below_pct' receives 1 if the condition is satisfied otherwise it receives 0    
        if df_aux is None: # if df_aux is empty
            df_aux = df_year # df_aux receives df_year
        else:
            df_aux=df_aux.append(df_year) # otherwise it appends df_year to df_aux
    
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
## :returns:   database dataframe including column 'HW' or 'CW'
## :rtype:     pandas.DataFrame
##
def get_wave(df_wave,wave_column,pct_column):
    check_pattern = df_wave.rolling(3)[pct_column].apply(lambda x: all(np.equal(x, [1,1,1])),raw=True) #use rolling to check for the pattern 111 in the above_pct/below_pct column
    check_pattern = check_pattern.fillna(False).astype(bool)
    pattern_idx = np.where(check_pattern)[0] #gets the index of the last ocurrence of '1' for each sequence
    
    subset = [range(idx-3+1, idx+1) for idx in pattern_idx] #gets the range of each  wave - the indexes of all 1's ocurrences in a sequence
     
    idx_list = [item for sublist in subset for item in sublist] #converts the subset list of ranges in a list of indexes
    
    idx_list=list(set(idx_list)) #removes the repetitive indexes 
    
    df_wave[wave_column]=0 # create column HW for heatwave or CW for coldwave
    df_wave[wave_column].iloc[idx_list]=1 #stores 1 in the column defined above for the indexes involved in a heat wave

    return df_wave 

#-------------------------------------------------------------------------------
## Checks for Heat Waves on the database according to the Climatic Normal This
## function uses Geirinhas et al. 2018 method. It obtains first a dataframe with
## the percentiles computed from the Climatic Normal according to the defined
## window size (df_pct). Then compares it with the database, to check if the
## maximum and minimum temperatures are above the corresponding percentile. If
## the temperatures are above the threshold, the column 'above_pct' receives 1.
## This column is then used to identify if there are 3 or more consecutive
## extremely warm days (Heat Wave). The column 'HW' then receives 1 for the days
## that are inside of a Heat Wave
##
## Climatic Normal dataframe needs to have at least 'DATE' and 'pct_column'.
## Database dataframe needs to have at least 'DATE' and 'db_column'. IF either
## or one of those dataframes don't have the 'DAY365' column (day of the year
## column), cn_columnDay365 and/or db_columnDay365 parameters must be False,
## otherwise True.
##
## If there are missing DATES on the database, db_complete parameter must be
## False, otherwise True.
##
## In case the df_pct was previously obtained, set df_pct = Dataframe obtained
## and set climatic_normal and pct_columns to None or any value/dataframe.
##
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
## :type       db_columnDay365:   Boolean (True or False)
## :param      db_columnDay365:   Indicates if the database has the Day365/day
##                                of the year column (db_columnDay365 = True) or
##                                not (db_columnDay365 = False - default)
## :type       db_complete:       Boolean (True or False)
## :param      db_complete:       Indicates if the database has missing DATES
##                                (db_complete = False - default) or not
##                                (db_complete = True)
## :type       cn_columnDay365:   Boolean (True or False)
## :param      cn_columnDay365:   Indicates if the climatic normal has the
##                                Day365/day of the year column (cn_columnDay365
##                                = True) or not (cn_columnDay365 = False -
##                                default)
## :type       df_pct:            pandas.DataFrame
## :param      df_pct:            The df pct - in case the dataframe with
##                                percentiles was already obtained, otherwise
##                                set df_pct = None (default)
## :type       percentile_value:  Float
## :param      percentile_value:  The percentile value (0 to 1.0), default = 0.9
## :type       window_size:       Integer
## :param      window_size:       The size of the window used to calculate the
##                                percentile, default = 15 days
##
## :returns:   df_checkHW -> database dataframe including columns 'above_pct'
##             and 'HW' 
##             df_pct -> dataframe with percentiles for each day of the
##             year (1 to 365)
## :rtype:     pandas.DataFrame
##
def check_HeatWave(database,db_columnMAX,db_columnMIN,climatic_normal,pct_columnMAX,pct_columnMIN,db_columnDay365=False,db_complete=False,cn_columnDay365=False,df_pct = None,percentile_value=0.9,window_size=15):
    if not db_complete:#in case db is incomplete - with missing dates
        database=complete_df(database) #add the missing dates without altering original db
    if not db_columnDay365: #in case there is no 'DAY365' column
        database = date_toDay365(database) #add column 'DAY365' to the dataframe
    
    database = drop_leapday(database) #removes leap day from the database
    
    if df_pct is None:
            
        if not cn_columnDay365: #in case there is no 'DAY365' column
            climatic_normal = date_toDay365(climatic_normal) #add column 'DAY365' to the dataframe
      
        climatic_normal = drop_leapday(climatic_normal) #removes leap day from climatic normal

        df_pct = pd.DataFrame() # creates a dataframe to store the percentiles
        df_pct['DAY365']=range(1,366) #creates 'DAY365' column with each row receiving values 1 to 365
        df_pct=df_pct.set_index(['DAY365']) # 'DAY365' is set as index
    
        df_pct['CTX90pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMAX,percentile_value,window_size))
        df_pct['CTN90pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMIN,percentile_value,window_size))
        #column 'percentiles'of df_pct receive the value of percentiles according to pct_column
    
    df_wave = get_abovePct(database,df_pct,db_columnMAX,db_columnMIN) #df_wave receives the database plus 'above_pct' column

    df_checkHW=get_wave(df_wave,'HW','above_pct') #df_checkHW receives the database plus 'above_pct' column and wave_column 'HW' column
    
    return df_checkHW, df_pct


#-------------------------------------------------------------------------------
## Checks for Cold Waves on the database according to the Climatic Normal
##
## Checks for Cold Waves on the database according to the Climatic Normal This
## function uses Geirinhas et al. 2018 method. It obtains first a dataframe with
## the percentiles computed from the Climatic Normal according to the defined
## window size Then compares it with the database, to check if the maximum and
## minimum temperatures are below the corresponding percentile. If the
## temperatures are above the threshold, the column 'below_pct' receives 1. This
## column is then used to identify if there are 3 or more consecutive extremely
## cold days (Cold Wave) The column 'CW' then receives 1 for the days that are
## inside of a Cold Wave
##
## Climatic Normal dataframe needs to have at least 'DATE' and 'pct_column'
## Database dataframe needs to have at least 'DATE' and 'db_column' IF either or
## one of those dataframes don't have the 'DAY365' column (day of the year
## column), cn_columnDay365 and/or db_columnDay365 parameters must be False,
## otherwise True
##
## If there are missing dates on the database, db_complete parameter must be
## False, otherwise True
##
## In case the df_pct was previously obtained, set df_pct = Dataframe obtained
## and set climatic_normal and pct_columns to None or any value/dataframe.
##
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
## :type       db_columnDay365:   Boolean (True or False)
## :param      db_columnDay365:   Indicates if the database has the Day365/day
##                                of the year column (db_columnDay365 = True) or
##                                not (db_columnDay365 = False)
## :type       db_complete:       Boolean (True or False)
## :param      db_complete:       Indicates if the database has missing dates
##                                (db_complete = False) or not (db_complete =
##                                True)
## :type       cn_columnDay365:   Boolean (True or False)
## :param      cn_columnDay365:   Indicates if the climatic normal has the
##                                Day365/day of the year column (cn_columnDay365
##                                = True) or not (cn_columnDay365 = False)
## :type       df_pct:            pandas.DataFrame
## :param      df_pct:            The df pct - in case the dataframe with
##                                percentiles was already obtained and is going
##                                to reused, otherwise set df_pct = None
##                                (default)
## :type       percentile_value:  Float
## :param      percentile_value:  The percentile value (0 to 1.0) - default 0.9
## :type       window_size:       Integer
## :param      window_size:       The size of the window used to calculate the
##                                percentile - default 15 days
##
## :returns:   df_checkCW -> database dataframe including columns 'below_pct'
##             and 'CW' 
##             df_pct -> dataframe with percentiles for each day of the
##             year (1 to 365)
## :rtype:     pandas.DataFrame
##
def check_ColdWave(database,db_columnMAX,db_columnMIN,climatic_normal,pct_columnMAX,pct_columnMIN,db_columnDay365=False,db_complete=False,cn_columnDay365=False,df_pct = None,percentile_value=0.1,window_size=15):
    if not db_complete:#in case db is incomplete - with missing dates
        database=complete_df(database) #add the missing dates without altering original db

    if not db_columnDay365: #in case there is no 'DAY365' column
        database = date_toDay365(database) #add column 'DAY365' to the dataframe
    
    database = drop_leapday(database) #removes leap day from the database
    
    if df_pct is None:
        
        if not cn_columnDay365: #in case there is no 'DAY365' column
            climatic_normal = date_toDay365(climatic_normal) #add column 'DAY365' to the dataframe
                
        climatic_normal = drop_leapday(climatic_normal) #removes leap day from climatic normal

        df_pct = pd.DataFrame() #creates a dataframe to store the percentiles
        df_pct['DAY365']=range(1,366) #creates 'DAY365' column with each row receiving values 1 to 365
        df_pct=df_pct.set_index(['DAY365']) # 'DAY365' is set as index
    
        df_pct['CTX10pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMAX,percentile_value,window_size))
        df_pct['CTN10pct'] = df_pct.index.map(lambda day365_index: get_percentile(climatic_normal,day365_index,pct_columnMIN,percentile_value,window_size))
        
    df_wave = get_belowPct(database,df_pct,db_columnMAX,db_columnMIN) #df_wave receives the database plus 'below_pct' column
    
    df_checkCW=get_wave(df_wave,'CW','below_pct') #df_checkW receives the database plus 'below_pct' column and 'CW' column
    
    return df_checkCW, df_pct

#-------------------------------------------------------------------------------
## Function to obtain the metrics of a Heat/Cold Wave given the database
## dataframe containing the 'HW'/'CW' column that indicates if a day is inside
## of a Heat/Cold Wave or not -> check get_wave function. This function obtains
## the wave duration for each year (HWN) of the database and then computes its
## maximum duration (HWD) and its intensity - sum of wave durations (HWF). These
## metrics are stored in a dataframe which includes the Heat/Cold Wave metrics
## for each year of the database
##
## Also possible to plot the metrics, for a better adjustment of the plots, go
## to function plot_oneMetric
##
## :param      df_checkW:    Database dataframe with 'HW'/'CW' column
## :type       df_checkW:    pandas.DataFrame
## :param      wave_column:  Name of the column containing information about
##                           Heat/Cold Waves
## :type       wave_column:  String
## :param      plot:         If True, function plot_oneMetric is used to plot
##                           all metrics generated
## :type       plot:         Boolean (True or False)
##
## :returns:   df_waveMetrics Dataframe containing wave metrics for each year of
##             the database
## :rtype:     pandas.DataFrame
##
def wave_metrics(df_checkW,wave_column,plot=False):
    counter=0
    wave=[]
    aux_list=[]
    waveDuration=[]
    df_waveMetrics=pd.DataFrame()

    #define names for metricss columns according to wave_column (e.g. HWN or CWN)
    n_waves = wave_column+str('N')
    maxd_waves = wave_column+str('D')
    sum_waves = wave_column+str('F')

    df_waveMetrics['YEAR']=df_checkW.DATE.dt.year.unique() #column 'year' of the df receives the unique years from the database
    df_waveMetrics=df_waveMetrics.set_index(['YEAR'])

    wave_idx = np.flatnonzero(df_checkW[wave_column]) #obtains indices of heat/cold wave days
    for group in mit.consecutive_groups(wave_idx): #select each heat/cold wave event
        wave.append(list(group)) #add event to a list

        # stores in an auxiliar list the year of the event and its length
        aux_list = [df_checkW.DATE.dt.year.iloc[wave[counter][0]],len(wave[counter])] 

        waveDuration.append(aux_list) #stores aux_list in waveDuration list
        counter+=1 #counter is incremented to go for next event

    df_aux = pd.DataFrame(waveDuration) #transform list with heat/cold waves information into a dataframe

    # 0 column of df_aux contains the years
    df_waveMetrics.loc[:,n_waves] = df_aux[0].value_counts().sort_index() #stores HWN/CWN on respective colum - number of events in a year
    df_waveMetrics.loc[:,maxd_waves] = df_aux.groupby(by=0).max() #stores HWD/CWD - longest event duration in a year
    df_waveMetrics.loc[:,sum_waves] = df_aux.groupby(by=0).sum() #stores HWF/CWF - cumulative sum of heat/cold waves in a year
    df_waveMetrics = df_waveMetrics.fillna(value=0) #years that didn't receive values are set to 0
    
    if plot: #if plot == True
        plot_oneMetric(df_waveMetrics,n_waves,n_waves) #plot HWN/CWN
        plot_oneMetric(df_waveMetrics,maxd_waves,maxd_waves) #plot HWD/CWD
        plot_oneMetric(df_waveMetrics,sum_waves,sum_waves) #plot HWF/CWF
    
    return df_waveMetrics

#--------------------------------------------------------------------------------
## Function to obtain the metrics of a Heat/Cold Wave given the database
## dataframe containing the 'HW'/'CW' column that indicates if a day is inside
## of a Heat/Cold Wave or not -> check get_wave function. This function obtains
## the wave duration for each year (HWN) of the database and then computes its
## maximum duration (HWD) and its intensity - sum of wave durations (HWF). These
## metrics are stored in a dataframe which includes the Heat/Cold Wave metrics
## for each year of the database
##
## Also possible to plot the metrics, for a better adjustment of the plots, go
## to function plot_oneMetric
##
## :param      df_checkW:    The df check w
## :type       df_checkW:    { type_description }
## :param      wave_column:  The wave column
## :type       wave_column:  { type_description }
## :param      plot:         The plot
## :type       plot:         boolean
##
## :returns:   { description_of_the_return_value }
## :rtype:     { return_type_description }
##
def wave_seasonMetrics(df_checkW,wave_column,plot=False):
    counter=0
    wave=[]
    aux_list=[]
    waveDuration=[]
    wave_idx = np.flatnonzero(df_checkW[wave_column])
    
    seasons = ['1', '1', '2', '2', '2', '3', '3', '3', '4', '4', '4', '1']
    month_to_season = dict(zip(range(1,13), seasons))
    
    n_waves = wave_column+str('N')
    maxd_waves = wave_column+str('D')
    sum_waves = wave_column+str('F')
        
    for group in mit.consecutive_groups(wave_idx):
        wave.append(list(group))
        if df_checkW.DATE.dt.month.iloc[wave[counter][0]] == 12:
            aux_list = [df_checkW.DATE.dt.year.iloc[wave[counter][0]]+1,
                        df_checkW.DATE.dt.month.iloc[wave[counter][0]],len(wave[counter])]
        else:
            aux_list = [df_checkW.DATE.dt.year.iloc[wave[counter][0]],
                        df_checkW.DATE.dt.month.iloc[wave[counter][0]],len(wave[counter])]
        waveDuration.append(aux_list)
        counter+=1
        
    df_aux = pd.DataFrame(waveDuration, columns =['YEAR','SEASON','waveDuration'])
    df_aux['SEASON'] = df_aux['SEASON'].map(month_to_season)
    df_aux = df_aux.rename(columns = {0:'YEAR',3:'SEASON',2:'waveDuration'})
    
    df_seasonMetrics = pd.DataFrame()
    df_seasonMetrics[n_waves] = df_aux.groupby(['YEAR','SEASON']).size()
    df_seasonMetrics[maxd_waves] = df_aux.groupby(['YEAR','SEASON']).max()
    df_seasonMetrics[sum_waves] = df_aux.groupby(['YEAR','SEASON']).sum()
    
    list_year = df_checkW.DATE.dt.year.unique()
    list_season = ['1','2','3','4']
    idx = tuple([(x, y) for x in list_year for y in list_season])
    dfwave_seasonMetrics = pd.DataFrame(data = df_seasonMetrics, columns=[n_waves, maxd_waves, sum_waves], 
                                        index=pd.MultiIndex.from_tuples(idx, names=['YEAR', 'SEASON']))
    dfwave_seasonMetrics = dfwave_seasonMetrics.fillna(value=0)
    
    if plot:
        plot_oneSeasonMetric(dfwave_seasonMetrics,n_waves,n_waves,lim=4.2,x_interval=None)
        plot_oneSeasonMetric(dfwave_seasonMetrics,maxd_waves,maxd_waves,lim=13)
        plot_oneSeasonMetric(dfwave_seasonMetrics,sum_waves,sum_waves,lim=22.1,x_interval=None)
        
    return dfwave_seasonMetrics
##
## { function_description }
##
## :param      df_metrics:  The df metrics
## :type       df_metrics:  { type_description }
## :param      metric:      The metric
## :type       metric:      { type_description }
## :param      title:       The title
## :type       title:       { type_description }
## :param      lim:         The limit
## :type       lim:         { type_description }
## :param      y_interval:  The y interval
## :type       y_interval:  number
##
## :returns:   { description_of_the_return_value }
## :rtype:     { return_type_description }
##
def plot_oneMetric(df_metrics,metric,title,lim=None,y_interval=5):       
    fig, axes = plt.subplots(figsize=(15,9),dpi=300)
    fig.suptitle(title,fontsize=20)
    
    if metric == 'HWN':
        ylabel ='Number of Heatwaves'
        color ='blue'
    
    elif metric == 'CWN':
        ylabel = 'Number of Coldwaves'
        color ='blue'
           
    elif metric == 'HWD' or 'CWD':
        ylabel ='Number of Days'
        color ='orange'
        
    elif metric == 'HWF' or 'CWF':
        ylabel = 'Number of Days'
        color = 'green'
                 
    axes.bar(df_metrics.index, df_metrics[metric],color=color)
    axes.set_ylabel(ylabel,fontsize=20)
    axes.set_ylim(ymin=0,ymax=lim)

    axes.xaxis.set_ticks(np.arange(df_metrics.index[0],df_metrics.index[-1]+1, y_interval))
    axes.tick_params(axis='both', which='major', labelsize=15)
    axes.grid()
   
    return fig

##
## { function_description }
##
## :param      df_seasonMetrics:  The df season metrics
## :type       df_seasonMetrics:  { type_description }
## :param      metric:            The metric
## :type       metric:            { type_description }
## :param      title:             The title
## :type       title:             { type_description }
## :param      lim:               The limit
## :type       lim:               { type_description }
## :param      x_interval:        The x interval
## :type       x_interval:        number
##
## :returns:   { description_of_the_return_value }
## :rtype:     { return_type_description }
##
def plot_oneSeasonMetric(df_seasonMetrics,metric,title,lim=None,x_interval=2):
    fig, axs = plt.subplots(nrows=2, ncols=2,sharex=False,sharey=False,figsize=(15, 9), dpi=300, gridspec_kw={'hspace': 0.4,'wspace': 0.2})
    fig.suptitle(title,fontsize=20,y=1.02)
    
    axs[0,0].yaxis.set_ticks(np.arange(0, lim, x_interval))
    axs[0,1].yaxis.set_ticks(np.arange(0, lim, x_interval))
    axs[1,0].yaxis.set_ticks(np.arange(0, lim, x_interval))
    axs[1,1].yaxis.set_ticks(np.arange(0, lim, x_interval))
    
    axs[0, 0].grid()
    axs[0, 1].grid()
    axs[1, 0].grid()
    axs[1, 1].grid()
    
    axs[0, 0].tick_params(axis='both', which='major', labelsize=15)
    axs[0, 1].tick_params(axis='both', which='major', labelsize=15)
    axs[1, 0].tick_params(axis='both', which='major', labelsize=15)
    axs[1, 1].tick_params(axis='both', which='major', labelsize=15)
    
    if metric == 'HWN':
        ylabel = 'Number of Heatwaves'
    elif metric == 'CWN':
        ylabel = 'Number of Coldwaves'
    elif metric == 'HWF' or 'CWF':
        ylabel = 'Number of Days'

    elif metric == 'HWD' or 'CWD':
        ylabel = 'Number of Days'
        
         
    axs[0, 0].bar(df_seasonMetrics.index.levels[0],df_seasonMetrics[metric].xs('1', level=1), color='r')
    axs[0, 0].set_title('Summer',fontsize=18)
    axs[0, 0].set_ylabel(ylabel,fontsize=15)
    
    axs[0, 1].bar(df_seasonMetrics.index.levels[0],df_seasonMetrics[metric].xs('4', level=1), color='y')
    axs[0, 1].set_title('Spring',fontsize=18)
    axs[0, 1].set_ylabel(ylabel,fontsize=15)
    
    axs[1, 0].bar(df_seasonMetrics.index.levels[0],df_seasonMetrics[metric].xs('3', level=1), color='b')
    axs[1, 0].set_title('Winter',fontsize=18)
    axs[1, 0].set_ylabel(ylabel,fontsize=15)
    
    axs[1, 1].bar(df_seasonMetrics.index.levels[0],df_seasonMetrics[metric].xs('2', level=1), color='g')
    axs[1, 1].set_title('Autumn',fontsize=18)
    axs[1, 1].set_ylabel(ylabel,fontsize=15)
    
    axs[0,0].set_ylim(ymin=0,ymax=lim)
    axs[0,1].set_ylim(ymin=0,ymax=lim)
    axs[1,0].set_ylim(ymin=0,ymax=lim)
    axs[1,1].set_ylim(ymin=0,ymax=lim)
    
    return fig       
