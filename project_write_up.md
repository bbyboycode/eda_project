# Analyzing MTA Turnstile Data to Optimize Street Team Outreach
Stanley Guo
## Abstract
The goal of this project was to analyze three months worth of MTA turnstile data to assist WomenTechWomenYes (WTWTY) generate attention to their upcoming gala at the beginning of the summer and to bring attention to the organization overall. I worked with subway turnstile data provided by the MTA on their website. After a bit of data cleaning to remove some duplicate data and other types of unusable data, I generated a few visualizations to communicate my findings to WTWY and provided recommendations on how to best strucutre their street teaming efforts for maximum results.
## Design
The project was designed with the goal of getting as many interactions with passengers as possible. I decided to focus on the total number of exits per station because that will give street teams access to passengers coming from areas surrounding the imemediate five boroughs that the MTA serves. Many passengers from Long Island, Westchester and New Jersey use the LIRR, Metro-Northm and NJ Transit, respectively, and they end up in MTA subways stations as their end point in their travels.
## Data
The dataset scraped from the MTA contains roughly 2.7 million rows of data. Each row contains entry and exit data about a certain turnstile, at a certain station, on a certain day, at a certain point in time, meaning information from every single turnstile in the subway ecosystem is collected at four hour intervals.
## Algorithims
I first created a shell of the database that was to be imported for further analysis in Jupyter using SQLite3 in my compter's command line.

I then ran a script in Jupyter to scrape the data needed from the MTA website and transformed that data into a CSV file and loaded that into the database that I created with SQLite3.

Using the SQLALchemy packaged in Python, I did some initial exploration of the data.

The majority of the work done was completed using the Pandas package in Python.
* I created a new column in the dataframe that converted the initial DATE and TIME columns into a combined DATETIME column
* Then I cleaned up some date and found two issues with the data.
  * The first issues was with duplicate data. Some turnstiles had a DESC value of RECOVR AUD on top of having an identical row but with DESC as REGULAR. Since the majority of rows has a DESC value of REGULAR, it was safe to assume that we could drop rows that contained RECOVR AUD.
  * The second issues was with a negative counter. The turnstile data is cumulative, so logically it would make sense that PREV_EXITS would be less than EXITS, however, this was not the case for some rows.
## Tools
* SQLite3 for database creation
* SQLALchemy for SQL querying within the Jupyter environment
* Pandas and Numpy for data manipulation and data cleaning
* Matplotlib and Seaborn for data visualization
# Communication
I found the top five busiest stations that I believe WTWY should place their street teams at for best results.
Originally the top five busiest stations around was supposed to be 34 St-Herald Sq, 42 St-Port Auth, 34 St-Penn Station, Grnd Cntrl-42nd st, and PATH New WTC, however, I decided to omit 34 St-Penn Station because it is too close in proximity to 34 St-Herald Sq, and I replaced it with W 4 St-Wash Sq

![image](https://github.com/guostan123/EDA_MTA_Project/blob/main/busiest_mta_stations_by_day.png)
![image](https://github.com/guostan123/EDA_MTA_Project/blob/main/busiest_mta_stations_by_day_line_graph.png)
![image](https://github.com/guostan123/EDA_MTA_Project/blob/main/busiest_mta_stations_by_day_heat.png)
