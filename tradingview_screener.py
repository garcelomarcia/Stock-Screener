# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 11:25:35 2021

@author: 52811
"""

import requests
import urllib.request
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd

from piotroski_f_revised import piotroski

driver = webdriver.Chrome()
url = "https://www.tradingview.com"
driver.maximize_window()
driver.get(url)
time.sleep(1)

driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/div[4]/span[2]/a").click()
try:
    driver.find_element_by_xpath("/html/body/div[11]/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span/span").click()
except:
    time.sleep(1)
    driver.find_element_by_xpath("/html/body/div[11]/div/div[2]/div/div/div/div/div/div/div[1]/div[4]/div/span/span").click()
username = input("Enter in your username: ")
password = input("Enter your password: ")

time.sleep(1)
username_textbox = driver.find_element_by_xpath("/html/body/div[11]/div/div[2]/div/div/div/div/div/div/form/div[1]/div[1]/input")
password_textbox = driver.find_element_by_xpath("/html/body/div[11]/div/div[2]/div/div/div/div/div/div/form/div[2]/div[1]/input")

username_textbox.send_keys(username)
password_textbox.send_keys(password + Keys.ENTER)

time.sleep(1)
url = "https://www.tradingview.com/screener/"
driver.get(url)
page_content = driver.page_source.encode('utf-8').strip()

ticker = []
sector = []
industry = []
rating = []
last = []
change = []
wp = []
mp = []
qmp = []
yp = []
ytd = []
rv = []
avg_vol = []
time.sleep(1)

SCROLL_PAUSE_TIME = 0.5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    
    
row_count = len(driver.find_elements_by_xpath("/html/body/div[8]/div/div[4]/table/tbody/tr"))+1
for i in range(1,row_count,1):
    print(f'Getting Data for stock number {i} of {row_count}')
    try:
        ticker.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[1]/div/div[2]/a').text)
    except:
        print("error getting ticker")
    
    try:
        sector.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[2]').text)
    except:
        print("error getting sector")
        
    try:
        industry.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[3]').text)
    except:
        print("error getting industry")
        
    try:
        rating.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[4]/span').text)
    except:
        print("error getting rating")
        
    try:
        last.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[5]').text)
    except:
        print("error getting last")
        
    try:
        change.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[6]').text)
    except:
        print("error getting change")
    
    try:
        wp.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[7]').text)
    except:
        print("error getting wp")
        
    try:
        mp.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[8]').text)
    except:
        print("error getting mp")
        
    try:
        qmp.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[9]').text)
    except:
        print("error getting qmp")
    
    try:
        yp.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[10]').text)
    except:
        print("error getting yp")
    try:
        ytd.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[11]').text)
    except:
        print("error getting ytd")
    
    try:
        rv.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[12]').text)
    except:
        print("error getting rv")
        
    try:
        avg_vol.append(driver.find_element_by_xpath(f'/html/body/div[8]/div/div[4]/table/tbody/tr[{i}]/td[13]').text)
    except:
        print("error getting avg_vol")
df = pd.DataFrame({"Ticker": ticker, "Sector": sector, "Industry": industry, "Rating": rating, "Last": last, "%Change": change,
                   "Weekly Performance": wp, "Monthly Performance": mp, "Quarterly Performance": qmp, "Yearly Performance": yp,"YTD": ytd, "Relative Vol": rv,
                   "Average Vol(90)": avg_vol})
df = df[(df != "—").all(1)]
df.iloc[:,[4,10]] = df.iloc[:,[4,11]].astype(float)
for j in range(5,10,1):
    df.iloc[:,j] = df.iloc[:,j].str.rstrip('%').str.replace('−','-').astype(float) / 100.0
df.iloc[:,11] = df.iloc[:,11].replace({'K': '*1e3', 'M': '*1e6'}, regex=True).map(pd.eval).astype(float)



industry_average = pd.DataFrame(df.groupby('Industry').mean()["Yearly Performance"].rename("Industry Avg Yearly Performance"))
industry_average = industry_average.sort_values(by="Industry Avg Yearly Performance",ascending=False)
industry_average = industry_average.reset_index()
top10_industries = industry_average.iloc[0:10,0].to_list()
df['Industry Over/Under'] = (df['Yearly Performance']-(df.groupby('Industry').transform('mean')["Yearly Performance"]))
df['Industry Performance'] = df.groupby('Industry').transform('mean')["Yearly Performance"]
df = df.set_index('Industry')
filtered_df = df[df.index.isin(top10_industries)]




scores={}
for each in top10_industries:
    
    industry_filter = filtered_df.filter(like=each, axis=0)
    ticker_list = industry_filter.iloc[:,0].to_list()
    scores[each]=piotroski(ticker_list)
    
scores_df=pd.DataFrame(scores)
scores_df = scores_df.sum(axis=1)
scores_df2 = pd.DataFrame(scores_df, columns=['Scores'])

filtered_df = pd.merge(left=filtered_df, right=scores_df2, left_on='Ticker', right_index=True)
filtered_df.to_excel("screened_stocks.xlsx")