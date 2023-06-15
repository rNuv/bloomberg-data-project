# Bloomberg Data Visualization Project

## Description
In my junior year, the Bloomberg Data center by Princeton was offering some students the opportunity to create a project that involved data visualization. I made a web application with Flask that allows users to type in the ticker symbol of any company they like, and see a time series analysis of the company's share prices. The web app also uses web scraping to collect data from the Yahoo finance page for data points related to the stock, a candlestick chart that shows open, low, high and close prices, and news of that particular company. There is also a Jupyter notebook file, outlining the code used to grab and create the visuals. The visuals were made using Bokeh plots.

On the last tab, there is a correlation coefficient graph with the top 25 S&P500 companies. Being such a volatile market, finding correlation between the price movements of two companies is important to minimize risk in a portfolio, or doubling down on risk for a greater return. 

## Pictures
<div align="center">
  <img src="images/home.png" width="666" height="383">  
</div>
<p align="center">
  Home Page
</p>
  
  ![](images/dash1.png)
  ![](images/dash2.png)
  ![](images/dash3.png)
  Deshboard
  
  ![](images/jupyter1.png)
  ![](images/jupyter2.png)
  Jupyer Notebook
  
  ![](images/correlation.png)
  Correlation Chart

## Technoloties
- ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
- ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
- ![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
- ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Web scraping API
- [Bokeh](https://docs.bokeh.org/en/latest/index.html) - The Visualization API
