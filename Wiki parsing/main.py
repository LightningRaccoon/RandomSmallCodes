import requests
import os
import json
import re
import PIL
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO

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
# print(filtered_td)
drivers = []
for td in filtered_td:
    driver = []
    print(td.contents)
    line = td.contents[0]
    print(line)

    if td.find('a'):
        driver.append('https:' + line['href'])
    else:
        if line.isnumeric() and int(line) < 100:
            driver.append(line)
        elif '-' in line:
            line = line.strip()
            driver.append(line)
    print(driver)

data = []
for td in filtered_td:
    data.append(td.text)

active_racists = []
# print(data)
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


# print(active_racists)
# print(len(active_racists))


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

# print(teams)
# print(manufacturers)

# -----------------------------
# Extract flags and their descriptions
# -----------------------------
flags = []
flag_rows = flag_table.find_all('tr', valign='top')

for i in range(len(flag_rows)):
    flag = flag_rows[i]
    flag_data = flag.find_all('td')
    flag_description = flag_data[1].text.strip()
    flag_img = flag_data[0].find('img')['src'] # starting with //upload.wikimedia.org/wikipedia/commons/...
    flags.append((flag_img, flag_description))

# print(flags)
# print(len(flags))
flags_images = [flag[0] for flag in flags]

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
identified_images = []

figure_images = []
for figure in figures:
    #print(figure.find('figcaption').text)
    if any(word in figure.find('figcaption').text for word in identifier_words):
        # print(figure.find('figcaption').text)
        # print(figure.find('img')['src'])
        identified_images.append(figure.find('img'))


# print(identified_images)

all_images = []
images = soup.find_all('img')
for img in images:
    all_images.append(img)

unidentified_images = [img for img in all_images if img not in identified_images]
unidentified_images = [img for img in unidentified_images if img['src'] not in flags_images]


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

counter = 1

# for img in identified_images:
#     path = os.path.abspath(identified_path) + '\identified_image' + str(counter) + '.jpg'
#     img_url = 'https:' + img['src']
#     img_data = requests.get(img_url).content
#     with open(path, 'wb') as handler:
#         handler.write(img_data)
#         counter += 1
#
# counter = 1
# for img in flags_images:
#     path = os.path.abspath(flags_path) + '\\flag_image' + str(counter) + '.jpg'
#     img_url = 'https:' + img
#     img_data = requests.get(img_url).content
#     with open(path, 'wb') as handler:
#         handler.write(img_data)
#         counter += 1
#
# counter = 1
# for img in unidentified_images:
#     extension = img['src'][-4:]
#     if not extension.startswith('.'):
#         continue
#     path = os.path.abspath(unidentified_path) + '\\unidentified_image' + str(counter) + img['src'][-4:]
#     if bool(re.match(r'^/[A-Za-z]', img['src'])):
#         img_url = 'https://hu.wikipedia.org' + img['src']
#     elif bool(re.match(r'^//', img['src'])):
#         img_url = 'https:' + img['src']
#     else:
#         img_url = img['src']
#     print(img['src'])
#     print(img_url)
#     img_data = requests.get(img_url).content
#     with open(path, 'wb') as handler:
#         handler.write(img_data)
#         counter += 1

# -----------------------------
# JSON export
# -----------------------------
full_json = []
driver_json = []

def get_image_size(url):
    response = requests.get(url)
    image_res = PIL.Image.open(BytesIO(response.content))
    return image_res.size

def get_svg_size(url):
    response = requests.get(url)
    content = response.content
    soup_xml = BeautifulSoup(content, 'xml')
    tag = soup_xml.find('svg')

    width = tag.get('width')
    height = tag.get('height')

    if width is None or height is None:
        viewBox = tag.get('viewBox')
        if viewBox is not None:
            _, _, width, height = viewBox.split(' ')

    return (width, height)

image_json = []
size_of_all_images = 0
highest_res = (0, '0x0')
lowest_res = (100000000, '10000x10000')
print(all_images)
for img in all_images:
    if bool(re.match(r'^/[A-Za-z]', img['src'])):
        img_url = 'https://hu.wikipedia.org' + img['src']
    elif bool(re.match(r'^//', img['src'])):
        img_url = 'https:' + img['src']
    else:
        img_url = img['src']

    print(img_url)
    extension = img['src'][-4:]
    if not extension.startswith('.'):
        continue
    if extension == '.svg':
        img_res = get_svg_size(img_url)
    elif extension.lower() == '.jpg' or extension.lower() == '.png':
        img_res = get_image_size(img_url)
    else:
        img_res = (0, 0)

    print(img_res)
    size_of_all_images += int(img_res[0]) * int(img_res[1])
    if int(img_res[0]) * int(img_res[1]) > highest_res[0]:
        highest_res = (int(img_res[0]) * int(img_res[1]), str(img_res[0]) + 'x' + str(img_res[1]))
    if int(img_res[0]) * int(img_res[1]) < lowest_res[0]:
        lowest_res = (int(img_res[0]) * int(img_res[1]), str(img_res[0]) + 'x' + str(img_res[1]))
    image_json.append({'image': img_url,
                       'resolution': str(img_res[0]) + 'x' + str(img_res[1]),
                       'image_size': len(requests.get(img_url).content),
                       'image_extension': img['src'][-4:]})




full_json.append({'images': image_json})

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
print("\nStatistics")
print("Number of drivers in the championship:   " + str(len(active_racists)))
print("Number of engine manufacturers:          " + str(len(manufacturers)))
print("Number of images:                        " + str(len(all_images)))
print("Number of identified images:             " + str(len(identified_images)))
print("Number of unidentified images:           " + str(len(unidentified_images)))
print("Size of all images:                      " + str(size_of_all_images) + " pixels")
print("Average size of images:                  " + str(round(size_of_all_images / len(all_images), 0)) + " pixels")
print("Highest resolution image:                " + highest_res[1])
print("Lowest resolution image:                 " + lowest_res[1])