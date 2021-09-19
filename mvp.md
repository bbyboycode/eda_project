# Analysis of the Busisest Subway Stations Around NYC
The goal of this project is to better understand which subway stations around NYC are the busiest by utilizing MTA turnstile to help promote WomenTechWomenYes (WTWY) and their upcoming gala.
## Initial Results
![image](https://github.com/guostan123/eda_project/blob/main/busiest_mta_stations_by_day.png)

To get the top five busiest subway stations, I cleaned MTA turnstile data and performed data cleaning and aggregation with the Pandas package.

I found that the top five busiest subway stations in NYC were (in descending order), were 34 ST-HERALD SQ, 42 ST-PORT AUTH, GRD CNTRL-42 ST, PATH NEW WTC and W 4 ST-WASH SQ.

The top five initially included 34 ST-PENN STA, however I decided to drop it since it was too close in proximity to 34 ST-HERALD SQ and it wouldn't make sense to place street teams that close to each other. I replaced 34 ST-PENN STA with W 4 ST-WASH SQ which was the sixth busiest subway station.
