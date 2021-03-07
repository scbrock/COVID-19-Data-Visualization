# Covid-19-Data-Visulization
In this project, we implemented a dashboard to visualize the data of COVID-19 in Ontario from various perspectives including summary statistics, plots, and a news feed. For instance, we provide statisitcs of infected cases, recovered cases based on the public health unit, and the visulization of vaccination cases. The objective is to provide the general public and decison makers with an overview of the COVID-19 situation in Ontario.

The dashboard is developed in Python3 including libraries such as Dash, Dash Bootstrap, BeautifulSoup, and Pandas. Here is a `requirements.txt` that lists the Python version and the libraries we used. Please refer to it if you cannnot run the dashboard.



## Getting Started
Please clone this repository via the follwoing command or the way you prefer.
```
git clone https://github.com/scbrock/COVID-19-Data-Visualization.git
```
After cloning the repository, run the file dashboard.py under the `Dashboard_Final` folder to start the dashboard. 
```
python3 dashboard.py 
```
After running the Python file, a localhost address such as http://localhost:8000 will be generated. Please copy the address to Chrome browser. 

## Usage
When using the dashboard, it may take a while to render the page, please do not worry about it. There are several interactive plots where we provide dropdown menus and tabs, etc. so that the users can specify the regions and dates they want to focus on. A note on using the dashboard: to visualize the data in a specific region, please delete the "all" box first, then add the regions you want.

![Alt text](https://github.com/scbrock/COVID-19-Data-Visualization/blob/main/screenshot.png)
