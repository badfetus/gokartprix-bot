import os

import discord
import json
import formfiller
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin

def getSchedule():
    session = HTMLSession()
    res = session.get('https://www.gokartprix.gno.se/2022-season/')
    soup = BeautifulSoup(res.html.html, "html.parser")
    tables = [
        [
            [td.get_text(strip=True) for td in tr.find_all('td')] 
            for tr in table.find_all('tr')
        ] 
        for table in soup.find_all('table')
    ]
    return tables
            
            
def getStandings():
    session = HTMLSession()
    res = session.get('https://www.gokartprix.gno.se/2022-season/2022-standings/')
    soup = BeautifulSoup(res.html.html, "html.parser")
    tables = [
        [
            [td.get_text(strip=True) for td in tr.find_all('td')] 
            for tr in table.find_all('tr')
        ] 
        for table in soup.find_all('table')
    ]
    return tables

print(getSchedule()[0][0][0])
print(getStandings()[0][0][0])