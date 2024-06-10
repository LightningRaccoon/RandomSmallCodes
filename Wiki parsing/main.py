import platform
import sys
import requests
import os
import json
import re
import PIL
from PIL import Image
from bs4 import BeautifulSoup
import io


def main():
    link = 'https://hu.wikipedia.org/wiki/Formula%E2%80%931'
    html = requests.get(link)

    # Find all tables
    soup = BeautifulSoup(html.text, 'html.parser')
    tables = soup.find_all('table')

    # Find tables for active drivers, teams and manufacturers, flags
    driver_number_table = None
    team_manufacturer_table = None
    flag_table = None

    for table in tables:
        column_headers = table.find_all('th')
        if len(column_headers) == 4 and column_headers[2].text == 'Pilóta Név' and driver_number_table is None:
            driver_number_table = table
        elif len(column_headers) == 0 and table.find_all('tr')[0].find_all('td')[0].text == 'Formula–1':
            team_manufacturer_table = table
        elif len(column_headers) == 2 and column_headers[0].text == 'Zászló':
            flag_table = table

    # -----------------------------
    # Extract active numbers, drivers and their wiki links
    # -----------------------------
    filtered_td = driver_number_table.find_all('td')
    filtered_td = [td for td in filtered_td if not td.find('img')]

    drivers = []
    current_race_number = 0
    current_driver_wiki = ""

    for td in filtered_td:
        #print(td.contents)
        line = td.contents[0]
        #print(line)

        if td.find('a'):
            current_driver_wiki = 'https://hu.wikipedia.org/' + td.find('a')['href']
        else:
            line = line.strip()
            if line.isnumeric() and int(line) < 100:
                current_race_number = int(line)
            elif line.endswith('–'):
                years = line
                driver = [current_race_number, current_driver_wiki, years]
                drivers.append(driver)

    print(drivers)
    print(len(drivers))

    # -----------------------------
    # Extract active drivers, their teams and numbers
    # -----------------------------
    new_drivers = []
    for driver in drivers:
        html = requests.get(driver[1])
        soup_driver = BeautifulSoup(html.text, 'html.parser')
        table = soup_driver.find_all('table', class_='infobox ujinfobox')
        driver_name = driver[1].split('/')[-1].split('_')
        driver_name = driver_name[0] + ' ' + driver_name[1]
        print(driver_name)
        #print(table)
        tr = table[0].find_all('tr')
        team = ""
        for t in tr:
            td = t.find_all('td')
            if len(td) == 2 and td[0].text == 'Csapata':
                team_text = td[1].text
                team = team_text[:team_text.find('(')]
                print(team)

        new_driver = [driver_name, driver[0], team]
        new_drivers.append(new_driver)

    print(new_drivers)

    data = []
    for td in filtered_td:
        data.append(td.text)

    active_drivers = []
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
            active_drivers.append((race_num, racist_name))


    # print(active_drivers)
    # print(len(active_drivers))


    # -----------------------------
    # Extract teams and motor manufacturers
    # -----------------------------
    print("Extracting teams and manufacturers...")
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
    print("Teams and manufacturers extraction finished\n")

    # -----------------------------
    # Extract flags and their descriptions
    # -----------------------------
    print("Extracting flags and descriptions...")
    flags = []
    flag_rows = flag_table.find_all('tr', valign='top')

    for i in range(len(flag_rows)):
        flag = flag_rows[i]
        flag_data = flag.find_all('td')
        flag_description = flag_data[1].text.strip()
        flag_img = flag_data[0].find('img')['src']
        flags.append((flag_img, flag_description))

    # print(flags)
    # print(len(flags))
    flags_images = [flag[0] for flag in flags]
    print("Flags extraction finished\n")

    # -----------------------------
    # Extract all images from the page
    # -----------------------------
    figures = soup.find_all('figure')

    pilots = [r[1] for r in active_drivers]
    identifier_words = teams + manufacturers + pilots

    # Remove duplicates
    identifier_words = list(dict.fromkeys(identifier_words))

    identified_images = []
    for figure in figures:
        # print(figure.find('figcaption').text)
        if any(word in figure.find('figcaption').text for word in identifier_words):
            # print(figure.find('figcaption').text)
            # print(figure.find('img')['src'])
            identified_images.append(figure.find('img'))

    all_images = soup.find_all('img')

    unidentified_images = [img for img in all_images if img not in identified_images]
    unidentified_images = [img for img in unidentified_images if img['src'] not in flags_images]

    # Make 3 folder for the images
    identified_path, unidentified_path, flags_path = generate_folders()

    # Collect identified images
    counter = 1
    for img in identified_images:
        path = os.path.abspath(identified_path) + '\identified_image' + str(counter) + '.jpg'
        img_url = 'https:' + img['src']
        img_data = requests.get(img_url).content

        with open(path, 'wb') as handler:
            handler.write(img_data)
            counter += 1

    # Collect flags
    counter = 1
    for img in flags_images:
        path = os.path.abspath(flags_path) + '\\flag_image' + str(counter) + '.jpg'
        img_url = 'https:' + img
        img_data = requests.get(img_url).content

        with open(path, 'wb') as handler:
            handler.write(img_data)
            counter += 1

    # Collect unidentified images
    counter = 1
    for img in unidentified_images:
        extension = img['src'][-4:]
        if not extension.startswith('.'):
            continue
        path = os.path.abspath(unidentified_path) + '\\unidentified_image' + str(counter) + img['src'][-4:]

        if bool(re.match(r'^/[A-Za-z]', img['src'])):
            img_url = 'https://hu.wikipedia.org' + img['src']
        elif bool(re.match(r'^//', img['src'])):
            img_url = 'https:' + img['src']
        else:
            img_url = img['src']

        img_data = requests.get(img_url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
            counter += 1

    # -----------------------------
    # JSON export
    # -----------------------------
    print("Exporting to JSON...")
    full_json = []

    # Collect drivers to JSON
    driver_json = collect_driver_json(new_drivers)
    full_json.append({'drivers': driver_json})

    # Collect images to JSON
    print("all_images: ", len(all_images))
    image_json, size_of_all_images, highest_res, lowest_res = collect_img_json(all_images)
    full_json.append({'images': image_json})

    # Collect flags to JSON
    flags_json = collect_flag_json(flags)
    full_json.append({'flag_rules': flags_json})

    # Export to json
    with open('data.json', 'w') as file:
        json.dump(full_json, file)
    print("JSON is finished!")

    # -----------------------------
    # Statistics
    # -----------------------------
    print("Making statistics...")
    statistics = [str(len(active_drivers)),
                  str(len(manufacturers)),
                  str(len(all_images)),
                  str(len(identified_images)),
                  str(len(unidentified_images)),
                  str(size_of_all_images) + "kb",
                  str(int(round(size_of_all_images / len(all_images), 0))) + "px",
                  highest_res[1],
                  lowest_res[1]]

    make_statistics(statistics)
    print("Statistics are finished!")

def generate_folders():
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

    return identified_path, unidentified_path, flags_path


def get_image_size(url):
    response = requests.get(url, stream=True)
    try:
        image_res = Image.open(io.BytesIO(response.content))
    except PIL.UnidentifiedImageError:
        print('Error: Unidentified image')
        return (0, 0)
    print(response)
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


def collect_driver_json(new_drivers):
    driver_json = []
    for driver in new_drivers:
        driver_json.append({'driver_name': driver[0],
                            'driver_number': driver[1],
                            'driver_team': driver[2]})
    return driver_json


def collect_img_json(all_images):
    image_json = []
    size_of_all_images = 0
    highest_res = (0, '0x0')
    lowest_res = (100000000, '10000x10000')
    counter = 1
    for img in all_images:
        if bool(re.match(r'^/[A-Za-z]', img['src'])):
            img_url = 'https://hu.wikipedia.org' + img['src']
        elif bool(re.match(r'^//', img['src'])):
            img_url = 'https:' + img['src']
        else:
            img_url = img['src']
        print('\nImage number: ' + str(counter))
        print(img_url)
        extension = img['src'][-4:]
        print(extension)
        # if not extension.startswith('.'):
        #     continue
        if extension == '.svg':
            img_res = get_svg_size(img_url)
        elif extension.lower() == '.jpg' or extension.lower() == '.png':
            #print(img_url)
            img_res = get_image_size(img_url)
        else:
            img_res = (0, 0)
        # print(img_res)
        size_of_all_images += int(img_res[0]) * int(img_res[1])
        resolution_size = int(img_res[0]) * int(img_res[1])
        if resolution_size > highest_res[0]:
            highest_res = (int(img_res[0]) * int(img_res[1]), str(img_res[0]) + 'x' + str(img_res[1]))
        elif resolution_size < lowest_res[0] and int(img_res[0]) != 0 and int(img_res[1]) != 0:
            lowest_res = (int(img_res[0]) * int(img_res[1]), str(img_res[0]) + 'x' + str(img_res[1]))
        image_json.append({'image': img_url,
                           'resolution': str(img_res[0]) + 'x' + str(img_res[1]),
                           'image_size': len(requests.get(img_url).content),
                           'image_extension': img['src'][-4:]})
        counter += 1

    print(len(image_json))
    return image_json, size_of_all_images, highest_res, lowest_res


def collect_flag_json(flags):
    flags_json = []
    for flag in flags:
        flags_json.append({'flag_image': 'https://' + flag[0], 'description': flag[1]})

    return flags_json


def make_statistics(statistics):
    if platform.system() == 'Windows' and re.match('10.*', platform.version()):
        command = 'scripts\\stat_gen.bat' + ' ' + ' '.join(statistics)
        os.system(command)
    elif platform.system() == 'Linux' and platform.version() == '20.04':
        command = 'sh scripts/stat_gen.sh' + ' ' + ' '.join(statistics)
        os.system(command)
    else:
        print('Unsupported OS version')


if __name__ == '__main__':
    main()