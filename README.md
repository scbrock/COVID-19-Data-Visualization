# Covid-19-Data-Visulization
In this project, we implemented a Dashboard to visualize the data of Covid-19 in Ontario from various perspectives including summary statistics, plots, and a news feed. For instance, we provide statisitcs of infected cases, recovered cases based on the public health unit, and the visulization of vaccination cases. The objective is to privide the general public and decison makers with a overview of covid-19 situation.

The dashboard is mainly developed in Python3 including libraries such as Dash, Dash Bootstrap, BeautifulSoup, etc. Here is a requirement.txt list the Python version and the libraries we used. Please refer to it, if you can not run the Dashboard.



## Getting Started
Please clone this code files via the follwoing commands or the way you prefer.
```
git clone https://github.com/scbrock/COVID-19-Data-Visualization.git
```
Then run the merged.py under the Covid-19-Data-Visulization folder to start the Dashboard. 
```
python3 merged.py 
```
After running the Python file, a localhost address such as http://localhost:8000 will be generated. Please copy the address to Chrome browser. 
## Usage
When using the dashboard, it may take a while to render the page, please don't worry about it. There are several interactive plots where we provide dropdown menus and tabs, etc. so that the users can specify the regions or dates they want to focus on. (One note to use the Dashboard: to visualize the data in a specific region, please delete the "all" box first, then add the regions you want.) 

![Alt text](https://github.com/scbrock/COVID-19-Data-Visualization/blob/main/screenshot.png)
