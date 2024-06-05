import requests
from bs4 import BeautifulSoup

# parse by link

def parse_by_link(link):
    html = requests.get(link)
    return html

def parse_active_drivers_with_number(table):
    return 0

link = 'https://hu.wikipedia.org/wiki/Formula%E2%80%931'
html = parse_by_link(link)

#find tables
soup = BeautifulSoup(html.text, 'html.parser')
tables = soup.find_all('table')

race_number_table = None
#find four column table
for table in tables:
    column_headers = table.find_all('th')
    if len(column_headers) == 4 and column_headers[2].text == 'Pilóta Név':
        #print(table)
        race_number_table = table
        break

rows = race_number_table.find_all('td', attrs={'rowspan': '2'})
print(rows)

