import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def parse_date(date):
    if date[0].isnumeric():
        return dt.datetime.strptime(date, '%Y %b %d')
    elif date=='Yesterday':
        return dt.datetime.today() - dt.timedelta(days=1)
    elif date=='Today':
        return dt.datetime.today()
    else:
        return dt.datetime.strptime(date + ' ' + str(dt.date.today().year), '%b %d %Y')

browser = webdriver.Chrome(executable_path='/Users/eliwork/Desktop/ikon-dash/chromedriver')

browser.get("https://www.onthesnow.com/ikon-pass/skireport")
time.sleep(1)

elem = browser.find_element_by_tag_name("body")

no_of_pagedowns = 50

while no_of_pagedowns:
    elem.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.2)
    no_of_pagedowns-=1

res = browser.find_element_by_tag_name('tbody')
html = res.get_attribute('outerHTML')

soup = BeautifulSoup(html, 'lxml')
tbodies = soup.find_all('tbody')
tbody = tbodies[0]
spots = []

spots = []
for row in tbody.findChildren(recursive=False)[:-1]:
    res = {}
    row_items = row.findChildren(recursive=False)
    if len(row_items) < 5:
        continue
    for i in range(len(row_items)):
        if i == 0:
            res['name'] = row_items[0].find('span').getText()
            res['last_update'] = row_items[0].find('time').getText()
            ext = row_items[0].find('a', href=True)['href']
            res['state'] = ext.split('/')[1].replace('-',' ').title()
            res['report_link'] = 'https://www.onthesnow.com' + ext
        if i==1:
            res['snowfall_amount'] = int(row_items[1].find('span', {'class': 'h4 styles_h4__318ae'}).getText()[:-1])
            res['last_snowfall'] = parse_date(row_items[1].find('time').getText())
        if i==2:
            res['base_depth'] = row_items[2].find('span', {'class', 'h4 styles_h4__318ae'}).getText()
            res['main_surface'] = row_items[2].find('div').getText()
        if i==3:
            open_trails = row_items[3].find('span', {'class', 'h4 styles_h4__318ae'}).getText()
            res['open_trails'], res['total_trails'] = open_trails.split('/')
        if i==4:
            open_lifts = row_items[4].find('span', {'class', 'h4 styles_h4__318ae'} ).getText()
            res['open_lifts'], res['total_lifts'] = open_lifts.split('/')
    spots.append(res)
spots
df = pd.DataFrame(spots)
df.to_csv('snowfall.csv', index=False)