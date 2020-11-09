# Python Climate and Health Toolbox

A set of tools to process data from weather stations and health databases to study the impact of extreme climate events in health.

## Project Overall

This project is studying the extreme climate events, such as heatwaves and their impact on health.

The present toolbox is being developed by students and researchers of the Climate and Health Data Science research team of the University of Campinas.

## Libraries description

### climatex

The IPCC Special Report on Managing the Risks of Extreme Events and Disasters to Advance Climate Change Adaptation (SREX), defines a extreme weather or climate event as "the occurrence of a value of a weather or climate variable above (or below) a threshold value near the upper (or lower) ends of the range of observed values of the variable". For simplicity, both extreme weather events and extreme climate events are referred to collectively as "climate extremes". 

This library implements a set of functions that are capable of identifying extreme events such as heatwaves and coldwaves.

The main inputs to this library would be datasets from weather stations and datasets that characterize climate normal time series.

#### Library functions

Heatwaves and coldwaves are detected according to the methodology of Geirinhas et al. (2018). Those events are characterized by metrics of quantity, duration and frequency described in Fischer and Schär (2010).

>*Requirements*: Input datasets need to have a column named 'DATE' of pandas datetime format, and columns for daily maximum and minimum temperature data.


| Function             | Parameters                                                                                                                                                                            | Description                                                                                                                        |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| complete_df          | dataset                                                                                                                                                                               | Adds missing dates to column DATE                                                                                                  |
| drop_leapday         | dataset                                                                                                                                                                               | Removes leap day data                                                                                                              |
| date_toDay365        | dataset                                                                                                                                                                               | Creates column DAY365 (day of the year) from column DATE                                                                           |
| day365_toDate        | day365, year                                                                                                                                                                          | Obtains a date from year and day of the year                                                                                       |
| get_percentile       | climatic_normal, day365_index, pct_column, <br>window_size, percentile_value                                                                                                          | Calculates pct_column percentile, according to each day of the year,  <br>using a window of X days centered on the day in question |
|get_abovePct_wave     | database, df_pct, db_columnMAX, db_columnMIN                                                                                                                                        |Evaluates if db_columnMAX and db_columnMIN are above the percentiles <br /> from df_pct (generated from climatic_normal) <br /> Used for wave functions|
get_abovePct_range     | database, df_pct, db_columnMAX, db_columnMIN                                                                                                                                         |Evaluates if db_columnMAX and db_columnMIN are above the percentiles <br /> from df_pct (generated from climatic_normal) <br /> Used for above range functions|
get_abovePct_dif       | database, df_pct, db_columnMAX, db_columnMIN                                                                                                                                         |Evaluates if db_columnMAX and db_columnMIN are above the percentiles <br /> from df_pct (generated from climatic_normal) <br /> Used for functions of difference between days|
get_belowPct_wave      | database, df_pct, db_columnMAX, db_columnMIN                                                                                                                                          |Evaluates if db_columnMAX and db_columnMIN are below the percentiles <br /> from df_pct (generated from climatic_normal) <br /> used for wave functions|
| get_wave             | df_wave, wave_column, above or below pct column                                                                                                                                       | Checks if there are 3 consecutive days or more with values from wave_column above or below the percentiles threshold               |
| check_HeatWave       | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, df_pct, percentile_value, window_size - optional) | Detection of Heatwave events (temperatures above thresholds for 3 days or more) using the previous functions             |
| check_ColdWave       | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, df_pct, percentile_value, window_size - optional) | Detection of Coldwave events (temperatures below thresholds for 3 days or more) using the previous functions           |
|check_HighHumidityWave | 	database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of High Humidity Wave events (humidity above thresholds for 3 days or more)<br /> using the previous functions|
|check_LowHumidityWave | 	database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Low Humidity Wave events (humidity below thresholds for 3 days or more)<br /> using the previous functions|
|check_HighPressureWave | 	database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of High Pressure Wave events (pressure above thresholds for 3 days or more)<br /> using the previous functions|
|check_LowHPressureyWave | 	database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Low Pressure Wave events (pressure below thresholds for 3 days or more)<br /> using the previous functions|
| wave_metrics         | df_checkW, wave_column, (plot - optional)                                                                                                                                             | Obtains yearly metrics - quantity, longest duration and frequency of events                                                        |
| wave_seasonMetrics   | df_checkW, wave_column, (plot - optional)                                                                                                                                             | Obtains seasonal metrics - quantity, longest duration and frequency of events                                                      |
| wave_intensity | df_checkW,wave_column,db_columnMAX,df_pct,(season - optional)                                                                                                                         | Obtains the maximum temperature anomaly (Tmax minus percentile) of each Heat/Cold wave                                                      |
|check_TemperatureAboveRange | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Temperature Above Range events <br /> (variation of temperature: temperature max - temperature min above thresholds) <br /> using the previous functions|
|check_HumidityAboveRange | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Humidity Above Range events <br /> (variation of humidity: humidity max - humidity min above thresholds) <br /> using the previous functions|
|check_PressureAboveRange | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Pressure Above Range events <br /> (variation of pressure: pressure max - pressure min above thresholds) <br /> using the previous functions|
|range_metrics | df_above_range (plot-optional) | Obtains yearly metrics - quantity -  of events|
|range_seasonMetrics | df_above_range (plot-optional) | Obtains season metrics - quantity -  of events|
|check_Temperature_difdays | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Difference of Temperature Between Days events <br />(difference between minimum and maximum temperature <br /> from the previous day above thresholds) using the previous functions|
|check_Humidity_difdays | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Difference of Humidity Between Days events <br />(difference between minimum and maximum humidity <br /> from the previous day  above thresholds) using the previous functions|
|check_Pressure_difdays | database, db_columnMAX, db_columMIN, climatic_normal, pct_columnMAX, <br /> pct_columnMIN, (db_columnDay365, db_complete, cn_columnDay365, <br /> df_pct, percentile_value, window_size - optional) | Detection of Difference of Pressure Between Days events <br />(difference between minimum and maximum pressure <br /> from the previous day  above thresholds) using the previous functions|
|dif_metrics | df_above_dif (plot-optional) | Obtains yearly metrics - quantity -  of events
|dif_seasonMetrics | df_above_dif (plot-optional) | Obtains season metrics - quantity -  of events
| plot_oneMetric       | df_metrics, metric, title, (lim, x_interval - optional)                                                                                                                               | Plots metric from df_metrics - yearly metrics dataframe                                                                            |
| plot_oneSeasonMetric | df_seasonMetrics, metric, title, (lim, y_interval - optional)                                                                                                                         | Plots metric from df_seasonMetrics - seasonal metrics dataframe                                                                    |



#### Examples

Useful scripts on how to use this library:


| File                        | Description                                                                                            |
|-----------------------------|--------------------------------------------------------------------------------------------------------|
| [IAC_heatwave_analyses.ipynb](https://github.com/climate-and-health-datasci-Unicamp/py-climate-health-toolbox/blob/master/examples/IAC_heatwave_analyses.ipynb) | Heatwave analyses for the weather station of the Agronomic Institute of Campinas (IAC) in Campinas, SP |
| [Comparison_IAC_VCP.ipynb](https://github.com/climate-and-health-datasci-Unicamp/py-climate-health-toolbox/blob/master/examples/Comparison_IAC_VCP.ipynb)    | Comparison between heatwave metrics of two weather stations from Campinas                              |

______________________________________________________________________________________________________________________________________________________________

**Author:** Daniela S. Oliveira, daniela.souza@outlook.com

**Contributors:** Felipe Pedroso, Lucas Ueda, Paula D. P. Costa

#### Installation

```
    You will need to install those modules
    
    Pandas              (0.25.3)
    Numpy               (1.18.0)
    More_itertools      (8.4.0)
    Matplotlib          (3.1.2)
```
To use this library you will need to:

```
   pip install py-climate-health-toolbox
```
```python
   import climahe.climatex as tex
```

#### Citing this library

OLIVEIRA, Daniela Souza de; PEDROSO, Felipe Augusto; UEDA, Lucas Hideki; COSTA, Paula Dornhofer Paro; AVILA, Ana Maria Heuminski de; FARIA, Eliana Cotta de. Python Climate and Health Toolbox: climatex. 0.0.3. [S. l.], 2020. <https://pypi.org/project/py-climate-health-toolbox/>.

## References

FISCHER, E. M.; SCHÄR, C. Consistent geographical patterns of changes in high-impact European heatwaves. Nature Geoscience, v. 3, n. 6, p. 398–403, 2010.

GEIRINHAS, J. L. et al. Climatic and synoptic characterization of heat waves in Brazil. International Journal of Climatology, v. 38, n. 4, p. 1760–1776, 2018.

## Acknowledgment

Grant 2017/20013-0 São Paulo Research Foundation (FAPESP)
   
