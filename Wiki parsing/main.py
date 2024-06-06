import requests
import os
import json
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
team_manufacturer_table = None
flag_table = None
#find four column table
for table in tables:
    column_headers = table.find_all('th')
    if len(column_headers) == 4 and column_headers[2].text == 'Pilóta Név' and race_number_table is None:
        #print(table)
        race_number_table = table
    elif len(column_headers) == 0 and table.find_all('tr')[0].find_all('td')[0].text == 'Formula–1':
        team_manufacturer_table = table
        #print(team_manufacturer_table)
    elif len(column_headers) == 2 and column_headers[0].text == 'Zászló':
        flag_table = table

# -----------------------------
# Extract active numbers with racers
# -----------------------------
filtered_td = race_number_table.find_all('td')
filtered_td = [td for td in filtered_td if not td.find('img')]

data = []
for td in filtered_td:
    data.append(td.text)

active_racists = []
print(data)
race_num = -1
racist_name = ""
for i in range(len(data)):
    line = data[i].strip()

    if line.isnumeric() and int(line) < 100:
        #print(line)
        race_num = int(line)

    if line.endswith('–'):
        racist_name = data[i-1]
        #print(racist_name)
        active_racists.append((race_num, racist_name))


print(active_racists)
print(len(active_racists))


# -----------------------------
# Extract teams and motor manufacturers
# -----------------------------
teams = []
manufacturers = []
team_rows = team_manufacturer_table.find_all('tr', valign='top')
#print(team_rows)

for row in team_rows:
    data = row.find_all('td')
    if data[0].text.strip() == 'Csapatok':
        teams = data[1].text[data[1].text.find('(')+1:len(data[1].text)-1].split(', ')
    elif data[0].text.strip() == 'Motorok':
        manufacturers = data[1].text[data[1].text.find('(')+1:len(data[1].text)-1].split(', ')


# -----------------------------
# Extract flags and their descriptions
# -----------------------------
flags = []
flag_rows = flag_table.find_all('tr', valign='top')

for i in range(0, len(flag_rows), 2):
    flag = flag_rows[i]
    flag_data = flag.find_all('td')
    flag_description = flag_data[1].text.strip()
    flag_img = flag_data[0].find('img')['src'] # starting with //upload.wikimedia.org/wikipedia/commons/...
    flags.append((flag_img, flag_description))

print(flags)






# -----------------------------
# Extract all images from the page
# -----------------------------
figures = soup.find_all('figure')
print(len(figures))

pilots = [r[1] for r in active_racists]
identifier_words = teams + manufacturers + pilots
print(len(identifier_words))
identifier_words = list(dict.fromkeys(identifier_words))
print(len(identifier_words))

figure_images = []
for figure in figures:
    #print(figure.find('figcaption').text)
    if any(word in figure.find('figcaption').text for word in identifier_words):
        print(figure.find('figcaption').text)

print(figure_images)

all_images = []
images = soup.find_all('img')
for img in images:
    all_images.append(img)

# Make 3 folder for the images
identified_directory = "identified"
unidentified_directory = "unidentified"
flags_directory = "flags"

identified_path = os.path.join(identified_directory)
unidentified_path = os.path.join(unidentified_directory)
flags_path = os.path.join(flags_directory)

if not os.path.exists(identified_path):
    os.mkdir(identified_path)

if not os.path.exists(unidentified_path):
    os.mkdir(unidentified_path)

if not os.path.exists(flags_path):
    os.mkdir(flags_path)


# -----------------------------
# JSON export
# -----------------------------
full_json = []
flags_json = []
for flag in flags:
    flags_json.append({'flag_image': 'https://' + flag[0], 'description': flag[1]})

full_json.append({'flag_rules': flags_json})

#export flags
with open('data.json', 'w') as file:
    json.dump(full_json, file)

# -----------------------------
# Statistics
# -----------------------------
# print("Number of drivers in the championship:   ")
# print("Number of engine manufacturers:          ")
# print("Number of images:                        ")
# print("Number of identified images:             ")
# print("Number of unidentified images:           ")
# print("Size of all images:                      ")
# print("Average size of images:                  ")
# print("Highest resolution image:                ")
# print("Lowest resolution image:                 ")