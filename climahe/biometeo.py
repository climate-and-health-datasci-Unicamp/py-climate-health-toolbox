'''
Created on Mon Oct 19 13:39:25 2020

@author: João Luís Carvalho de Abreu

Module to develop some convertions and mainly compute some biometereological indexes.
This algorithm currently includes the following indexes: Wet-Bulb Globe Temperature (WBGT), Apparent Temperature (AT), 
Wind Chill (WC), Heat Index (HI), Thom Discomfort Index (DI), Humidex and Relative Strain Index (RSI).

Each function was developed based on different sources and its parameters can vary due to the location where it's
applied to.

'''

import numpy as np


#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert a temperature from degrees farenheit to degrees celsius.
##
## :param 		TF: temperature in °F
## :type 		TF: Float
##
## :returns 	TC: rounded temperature in °C
## :rtype 		TC: Float
##

def farenheit_to_celsius(TF):
  TC = (TF - 32)*(5/9)
  return round(TC, 4)

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert a temperature from degrees celsius to degrees farenheit.
##
## :param 		TC: temperature in °C
## :type 		TC: Float
##
## :returns 	TF: rounded temperature in °F
## :rtype 		TF: Float
##

def celsius_to_farenheit(TC):
  TF = (9/5)*TC + 32
  return round(TF, 4)

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert a temperature from degrees celsius to degrees kelvin.
##
## :param 		TC: temperature in °C
## :type 		TC: Float
##
## :returns 	TK: rounded temperature in K
## :rtype 		TK: Float
##

def celsius_to_kelvin(TC):
  TK = TC + 273.15
  return round(TK, 4)

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert a temperature from degrees kelvin to degrees celsius.
##
## :param 		TK: temperature in K
## :type 		TK: Float
##
## :returns 	TC: rounded temperature in °C
## :rtype 		TC: Float
##

def kelvin_to_celsius(TK):
  TC = TK - 273.15
  return round(TC, 4)

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert a temperature from degrees farenheit to degrees kelvin.
##
## :param 		TF: temperature in °F
## :type 		TF: Float
##
## :returns 	TK: rounded temperature in K
## :rtype 		TK: Float
##

def farenheit_to_kelvin(TF):
  TK = (TF - 32)*(5/9) + 273.15
  return round(TK, 4)

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert a temperature from degrees kelvin to degrees farenheit.
##
## :param 		TK: temperature in K
## :type 		TK: Float
##
## :returns 	TF: rounded temperature in °F
## :rtype 		TF: Float
##

def kelvin_to_farenheit(TK):
  TF = (9/5)*(TK - 273.15) + 32
  return round(TF, 4)

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the saturated vapor pressure of an environment based on a temperature input.
##
## ATTENTION: This function just computes the saturated vapor pressure for celsius unit. If the farenheit unit is
## chosen, the function will automatically convert the input value and return the saturated vapor pressure based on
## the converted value.
## 
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	svp: rounded saturated vapor pressure in Pa
## :rtype 		svp: Float or String ("NA": not applicable)
## 
## Source: HUANG, J. A simple accurate formula for calculating saturation vapor pressureof water and ice. Journal of 
## Applied Meteorology and Climatology, v. 57, n. 6, p.1265–1272, 2018.
##

def sat_vap_pressure(T, degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)

  svp = []
  for i in T:
    if (degrees != "celsius" and degrees != "farenheit"):
      svp.append("NA")

    else:
      if i > 0:
        svp.append(round(np.exp(34.494-(4924.99/(i+237.1)))/((i+105)**1.57),6))
	  
      else:
        svp.append(round(np.exp(43.494-(6545.8/(i+278)))/((i+868)**2),6))

  if (degrees != "celsius" and degrees != "farenheit"):
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")

  return svp

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the actual vapor pressure of an environment based on a temperature and a relative humidity input. 
##
## ATTENTION: This function just computes the saturated vapor pressure for celsius unit. If the farenheit unit is
## chosen, the function will automatically convert the input value and return the saturated vapor pressure based on
## the converted value.
##
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		rh: relative humidity in %
## :type 		rh: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	avp: rounded actual vapor pressure in Pa
## :rtype 		avp: Float or String ("NA": not applicable)
##

def act_vap_pressure(T, rh, degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)

  avp = rh*sat_vap_pressure(T)/100
  avp = round(avp, 6)

  if (degrees != "celsius" and degrees != "farenheit"):
    avp = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")

  return avp

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert two differente moisture units. From relative humidity to dew point temperature.
##
## ATTENTION: This function can compute the apparent temperature for either celsius or farenheit unit. However,
## the convertion's formula applied in this program is just valid for celsius unit. In other words, there isn't 
## any regression applied to this formula, so for the farenheit choice the program will just convert the values
## at the beggining and at the end of the function call.
##
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		rh: relative humidity in %
## :type 		rh: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: Float
##
## :returns 	Td: rounded dew point temperature in °C or °F
## :rtype 		Td: Float or String ("NA": not applicable)
##
## Source: converted from the Weathermetrics R library 
##         Link: https://github.com/geanders/weathermetrics/blob/master/R/heat_index.R
##

def relative_humidity_to_dewpoint(T, rh, degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)

  Td = np.power(rh/100, 1/8)*(112 + 0.9*T) - 112 + 0.1*T
 
  if degrees == "farenheit":
  	Td = celsius_to_farenheit(Td)

  Td = round(Td)

  if (degrees != "celsius" and degrees != "farenheit"):
    Td = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")

  return Td

#-------------------------------------------------------------------------------------------------------------------------#
## Function to convert two differente moisture units. From dew point temperature to relative humidity.
## 
## ATTENTION: This function just computes the saturated vapor pressure for celsius unit. If the farenheit unit is
## chosen, the function will automatically convert the input value and return the saturated vapor pressure based on
## the converted value.
## 
## :param 		Td: dew point temperature (°C or °F)
## :type 		Td: Float
## :param 		T: air temperature (°C or °F)
## :type 		T: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	rh: rounded relative humidity in %
## :rtype 		rh: Float or String ("NA": not applicable)
##
## Source: converted from the Weathermetrics R library 
##         Link: https://github.com/geanders/weathermetrics
##

def dewpoint_to_relative_humidity(T, Td, degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)
    Td = farenheit_to_celsius(Td)
  
  x = (112 - 0.1*T + Td)/(112 + 0.9*T)
  rh = 100*np.power(x, 8)
  rh = round(rh, 6)

  if (degrees != "celsius" and degrees != "farenheit"):
    rh = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")  

  return rh

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the apparente temperature index for a certain environment based on the following inputs:
## temperature, vapor pressure, environment condition, wind speed and degree unit.
##
## ATTENTION: This function can compute the apparent temperature for either celsius or farenheit unit. However,
## the apparent temperature's formula applied in this program is just valid for celsius unit. In other words, there
## isn't any regression applied to this formula, so for the farenheit choice the program will just convert the values
## at the beggining and at the end of the function call.
##
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		P: vapor pressure in kPa
## :type 		P: Float
## :param 		ws: wind speed at approximately 10m aobve the ground (in m/s), defaut = 0
## :type 		ws: Float
## :param 		condition: conditions the index can be applied to (indoors or shade), defaut = indoors
## :type 		condition: String
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	at: rounded apparent temperature in °C or °F
## :rtype 		at: Float or String ("NA": not applicable)
##
## Source: STEADMAN, R. G. A universal scale of apparent temperature.Journal of Climateand Applied Meteorology, v. 23, 
## n. 12, p. 1674–1687, 1984.
##

def apparent_temperature(T, P, ws = 0, condition = "indoors",  degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)
  
  if condition == "indoors":
    at = -1.3 + 0.92*T +2.2*P

    if (degrees == "farenheit"):
      at = celsius_to_farenheit(at)

    at = round(at, 6)
  
  elif condition == "shade":
    at = -2.7 + 1.04*T + 2*P - 0.65*ws

    if (degrees == "farenheit"):
      at = celsius_to_farenheit(at)
    
    at = round(at, 6)

  if (condition != "indoors" and condition != "shade"):
    at = "NA"
    print("Invalid condition. Choose between either 'indoors' or 'shade'")

  if (degrees != "celsius" and degrees != "farenheit"):
    at = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")
  
  return at

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the wind chill index (Steadman version) based on the air temperature and on the wind speed for 
## either the metric or the american unit system.
##
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		ws: wind speed at 10m from the ground (in the chosen unit system)
## :type 		ws: Float
## :param 		unit: unit system intended (metric or us), defaut = metric
##					  metric: respectively °C and m/s
##					  us: respectively °F and mph
## :type 		unit: String
##
## :returns 	wd: rounded wind chill in °C or °F
## :rtype 		wd: Float or String ("NA": not applicable)
##
## Source: QUAYLE, R. G.; STEADMAN, R. G. The steadman wind chill: An improvementover present scales. Weather and 
## Forecasting, v. 13, n. 4, p. 1187–1193, 1998.
##

def wind_chill(T, ws, unit = "metric"):
  if unit == "metric":
    wc = 1.41 - 1.162*ws + 0.98*T + 0.0124*(ws**2) + 0.0185*T*ws
    wc = round(wc, 6)
  
  elif unit == "us":
    wc = 3.16 - 1.2*ws + 0.98*T + 0.0044*(ws**2) + 0.0083*T*ws
    wc = round(wc, 6)

  if (unit != "metric" and unit != "us"):
    wc = "NA"
    print("Invalid units. Choose either 'metric' or 'us' units.")

  return wc

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the wind chill index (Environment Canada version) based on the air temperature and on the wind 
## speed for either the metric or the american unit system.
##
## ATTENTION: this formula, made by the Environment Canada, is a different approach from the Steadman's wind chill index 
## formula, and take into account some specific conditions to be right used such as air temperature bellow 0°C and wind
## speed in two different scenarios: ranging from 0 to 5 km/h or simply above 5 km/h.
##
## :param 		T: air temperature in °C
## :type 		T: Float
## :param 		ws: wind speed at 10m from the ground in km/h
## :type 		ws: Float
##
## :returns 	wd: rounded wind chill in °C
## :rtype 		wd: Float or String ("NA": not applicable)
##
## Source: Enviornment Canadas's website
##         Link: https://www.canada.ca/en/environment-climate-change/services/climate-change/canadian-centre-climate-services/display-download/technical-documentation-climate-normals.html#toc1
##

def wind_chill_canada(T, ws):
  if (T <= 0 and ws >= 5):
    wc = 13.12 + 0.6215*T - 11.37*(ws**0.16) + 0.3965*T*(ws**0.16)
    wc = round(wc, 6)

  elif (T <= 0 and 0 <= ws <= 5):
  	wc = T + ((-1.59 + 0.1345*T)/5)*ws
  	wc = round(wc, 6)

  else:
  	wc = "NA"
  	print("One or more parameters out of the due range.\nCheck if the air temperature is bellow 0°C and if the wind speed is a positive number.")

  return wc

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the heat index based on the air temperature and on the relative humidity of a certain
## evnrionment.
##
## ATTENTION: This function can compute the heat index for either celsius or farenheit unit. However, the formula 
## applied in this program is originally designed to only receive farenheit temperatures. It's important to notice 
## that no regression was applied to this formula, but only the values convertion at the beggining and at the end
## of the function call. 
##
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		rh: relative humidity in %
## :type 		rh: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	hi: rounded heat index in °C or °F
## :rtype 		hi: Float or Sstring ("NA": not applicable)
##
## Source: converted from the Weathermetrics R library based on the NWS formula
##         Link: https://github.com/geanders/weathermetrics
##

def heat_index(T, rh, degrees = "celsius"):
  
  hi = np.zeros(len(T))
  alpha = np.zeros(len(T))
  adjustment1 = np.zeros(len(T))
  adjustment2 = np.zeros(len(T))
  total_adjustment = np.zeros(len(T))

  if degrees == "celsius":
    T = celsius_to_farenheit(T)

  for i in range(len(T)):
    if (degrees != "celsius" and degrees != "farenheit"):
      hi = [str(k) for k in hi]
      hi[i] = "NA"

    else:
      if T[i] <= 40:
        hi[i] = T[i]

      else:
        alpha[i] = 61 + ((T[i] - 68)*1.2) + (rh[i]*0.094)
        hi[i] = 0.5*(alpha[i] + T[i])

        if hi[i] > 79:
          hi[i] = (-42.379 + 2.04901523*T[i] + 10.14333127*rh[i] - 0.22475541*T[i]*rh[i] - 6.83783*(10**(-3))*(T[i]**2) -
                   5.481717*(10**(-2))*(rh[i]**2) + 1.22874*(10**(-3))*(T[i]**2)*rh[i] + 8.5282*(10**(-4))*T[i]*(rh[i]**2) - 
                   1.99*(10**(-6))*(T[i]**2)*(rh[i]**2))
      
          if (rh[i] <= 13 and T[i] >= 80 and T[i] <= 112):
            adjustment1[i] = (13 - rh[i])/4
            adjustment2[i] = ((17 - abs(T[i] - 95))/17)**(1/2)
            total_adjustment[i] = adjustment1[i]*adjustment2[i]
            hi[i] = hi[i] - total_adjustment[i]
        
          elif (rh[i] > 85 and T[i] >= 80 and T[i] <= 87):
            adjustment1[i] = (rh[i] - 85)/10
            adjustment2[i] = (87 - T[i])/5
            total_adjustment[i] = adjustment1[i]*adjustment2[i]
            hi[i] = hi[i] + total_adjustment[i]

      if degrees == "celsius":
        hi[i] = farenheit_to_celsius(hi[i])

      hi[i] = round(hi[i], 6)

  if (degrees != "celsius" and degrees != "farenheit"):
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")

  return hi

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the thom discomfort index based on the air temperature and on the relative humidiy of a certain
## envioronment.
##
## ATTENTION: This function can compute the apparent temperature for either celsius or farenheit unit. However,
## the apparent temperature's formula applied in this program is just valid for celsius units. In other words, there
## isn't any regression applied to this formula, so for the farenheit choice the program will just convert the values
## at the beggining and at the end of the function call.
##
## :param 		T: air temperature in °C or °F
## :type 		T: Float
## :param 		rh: relative humidity in %
## :type 		rh: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	di: rounded thom discomfort index in °C or °F
## :rtype 		di: Float or String ("NA": not applicable)
##
## Source: VANECKOVA, P. et al. Do biometeorological indices improve modeling outcomes of heat-related mortality?Journal 
## of Applied Meteorology and Climatology, v. 50, n. 6,p. 1165–1176, 2011.
##

def discomfort_index(T, rh, degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)
  
  di = T - (0.55 - 0.0055*rh)*(T - 14.5)

  if (degrees == "farenheit"):
    di = celsius_to_farenheit(di)
  
  di = round(di, 6)

  if (degrees != "celsius" and degrees != "farenheit"):
    di = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")

  return di

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the humidex based on the air temperature and on the water vapor pressure of a certain
## environment.
##
## ATTENTION: This function can compute the humidex for either celsius or farenheit unit. However, the humidex's formula 
## applied in this program deppends on a vapour pressure computable value that uses degrees kelvin as its temperature
## parameter. Because of that, for either celsius or farenheit units, the program will convert these values and calculate
## the vapour pressure variable; after that, the humidex is obtained from the simple formula shown below with the air
## temperature in the original chosen unit and the vapour pressure in hPa.
##
## :param 		T: air temperature (in the chosen degree unit)
## :type 		T: Float
## :param 		humidity: based on the moisture unit intended (dewpoint or relative humidity), defaut = dewpoint
##						  dewpoint temperature: in the chosen degree unit
##	 	 				  relative humidity: in %	
## :type 		humidity: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	humidex: rounded humidity index (in the chosen degree unit)
## :rtype 		humidex: Float or String ("NA": not applicable)
##
## Source: Enviornment Canadas's website
##         Link: https://www.canada.ca/en/environment-climate-change/services/climate-change/canadian-centre-climate-services/display-download/technical-documentation-climate-normals.html#toc1
##

def humidex(T, humidity, degrees = "celsius", moisture_unit = "dewpoint"):
  if moisture_unit == "dewpoint":
    Td = humidity # dewpoint temperature

    if degrees == "celsius":
      Td = celsius_to_kelvin(Td)  
      e = 6.112*np.exp(5417.7530*((1/273.15)-(1/Td))) # in hPa
      humidex = T + 0.5555*(e - 10)
      humidex = round(humidex, 6)

    elif degrees == "farenheit":
      Td = farenheit_to_kelvin(Td)  
      e = 6.112*np.exp(5417.7530*((1/273.15)-(1/Td))) # in hPa
      humidex = T + 0.5555*(e - 10)
      humidex = round(humidex, 6)

  elif moisture_unit == "relative humidity":
    rh = humidity # relative humidity
    Td = relative_humidity_to_dewpoint(T, rh) 

    if degrees == "celsius":
      Td = celsius_to_kelvin(Td)  
      e = 6.112*np.exp(5417.7530*((1/273.15)-(1/Td))) # in hPa
      humidex = T + 0.5555*(e - 10)
      humidex = round(humidex, 6)

    elif degrees == "farenheit":
      Td = farenheit_to_kelvin(Td)  
      e = 6.112*np.exp(5417.7530*((1/273.15)-(1/Td))) # in hPa
      humidex = T + 0.5555*(e - 10)
      humidex = round(humidex, 6)

  if (degrees != "celsius" and degrees != "farenheit"):
    humidex = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")

  if (moisture_unit != "dewpoint" and moisture_unit != "relative humidity"):
  	humidex = "NA"
  	print("Invalid moisture unit. Choose either 'dewpoint' or 'relative humidity'.")

  return humidex

#-------------------------------------------------------------------------------------------------------------------------#
## Function to compute the relative strain index based on the air temperature and on the partial water vapor pressure
## of a certain envrionment
##
## ATTENTION: This function just computes the relative strain index for celsius unit. If the farenheit unit is
## chosen, the function will automatically convert the input value and return the saturated vapor pressure based on
## the converted value.
##
## :param 		T: air temperature (in the chosen degree unit)
## :type 		T: Float
## :param 		pwvp: partial water vapor pressure in millimeters of mercury
## :type 		pwvp: Float
## :param 		degrees: degree unit (celsius or farenheit), defaut = celsius
## :type 		degrees: String
##
## :returns 	RSI: rounded relative strain index
## :rtype 		RSI: Float or String ("NA": not applicable)
##
## Source: GARÍN, A. de; BEJARÁN, R. Mortality rate and relative strain index in buenos airescity. International journal 
## of biometeorology, Springer, v. 48, n. 1, p. 31–36, 2003.
##

def relative_strain_index(T, pwvp, degrees = "celsius"):
  if degrees == "farenheit":
    T = farenheit_to_celsius(T)

  rsi = (10.7 + 0.74*(T - 35))/(44 - pwvp)
  rsi = round(rsi, 6)

  if (degrees != "celsius" and degrees != "farenheit"):
    rsi = "NA"
    print("Invalid degrees. For degrees, choose either 'farenheit' or 'celsius'")
                                
  return rsi

#-------------------------------------------------------------------------------------------------------------------------#
