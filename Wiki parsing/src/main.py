import os
import io
import json
import re
import platform

import PIL
import requests
from PIL import Image
from bs4 import BeautifulSoup


def extract_tables(tables):
    """
    Extract tables from the html
    :param tables:
    :return:
    """
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
    return driver_number_table, team_manufacturer_table, flag_table


def get_active_drivers(td_list):
    """
    Get active drivers
    :param td_list:
    :return:
    """
    drivers = []
    current_race_number = 0
    current_driver_wiki = ""
    for td in td_list:
        line = td.contents[0]
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
    return drivers


def get_driver_with_teams(drivers):
    """
    Get drivers with their teams
    :param drivers:
    :return:
    """
    drivers_with_teams = []
    for driver in drivers:
        html = requests.get(driver[1])
        soup_driver = BeautifulSoup(html.text, 'html.parser')
        table = soup_driver.find_all('table', class_='infobox ujinfobox')
        driver_name = driver[1].split('/')[-1].split('_')
        driver_name = driver_name[0] + ' ' + driver_name[1]
        tr = table[0].find_all('tr')
        team = ""
        for t in tr:
            td = t.find_all('td')
            if len(td) == 2 and td[0].text == 'Csapata':
                team_text = td[1].text
                team = team_text[:team_text.find('(')]
                team = team.strip()

        new_driver = [driver_name, driver[0], team]
        drivers_with_teams.append(new_driver)
    return drivers_with_teams


def get_teams_and_manufacturers(team_manufacturer_table):
    teams = []
    manufacturers = []
    team_rows = team_manufacturer_table.find_all('tr', valign='top')

    for row in team_rows:
        data = row.find_all('td')
        if data[0].text.strip() == 'Csapatok':
            teams = data[1].text[data[1].text.find('(')+1:len(data[1].text)-1].split(', ')
        elif data[0].text.strip() == 'Motorok':
            manufacturers = data[1].text[data[1].text.find('(')+1:len(data[1].text)-1].split(', ')

    return teams, manufacturers


def get_flags(flag_table):
    flags = []
    flag_rows = flag_table.find_all('tr', valign='top')

    for i in range(len(flag_rows)):
        flag = flag_rows[i]
        flag_data = flag.find_all('td')
        flag_description = flag_data[1].text.strip()
        flag_img = flag_data[0].find('img')['src']
        flags.append((flag_img, flag_description))

    flags_images = [flag[0] for flag in flags]
    return flags, flags_images


def get_image_size(url):
    """
    Get the size of the image from the url
    :param url:
    :return:
    """
    response = requests.get(url, stream=True)
    try:
        image_res = Image.open(io.BytesIO(response.content))
    except PIL.UnidentifiedImageError:
        #print('Error: UnidentifiedImageError')
        return 0, 0
    return image_res.size


def get_svg_size(url):
    """
    Get the size of the svg image from the url
    :param url:
    :return:
    """
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

    return width, height


def create_directories():
    """
    Create directories for identified, unidentified and flags images
    :return:
    """
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


def download_identified_images(identified_images, identified_path):
    """
    Download identified images
    :param identified_images:
    :param identified_path:
    :return:
    """
    counter = 1
    for img in identified_images:
        path = os.path.abspath(identified_path) + '\identified_image' + str(counter) + '.jpg'
        img_url = 'https:' + img['src']
        img_data = requests.get(img_url).content

        with open(path, 'wb') as handler:
            handler.write(img_data)
            counter += 1


def download_flags(flags_images, flags_path):
    """
    Download flags
    :param flags_images:
    :param flags_path:
    :return:
    """
    counter = 1
    for img in flags_images:
        path = os.path.abspath(flags_path) + '\\flag_image' + str(counter) + '.jpg'
        img_url = 'https:' + img
        img_data = requests.get(img_url).content

        with open(path, 'wb') as handler:
            handler.write(img_data)
            counter += 1


def download_unidentified_images(unidentified_images, unidentified_path):
    """
    Download unidentified images
    :param unidentified_images:
    :param unidentified_path:
    :return:
    """
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


def collect_driver_json(new_drivers):
    """
    Collect drivers to JSON
    :param new_drivers:
    :return:
    """
    driver_json = []
    for driver in new_drivers:
        driver_json.append({'driver_name': driver[0],
                            'driver_number': driver[1],
                            'driver_team': driver[2]})
    return driver_json


def collect_img_json(all_images):
    """
    Collect images to JSON
    :param all_images:
    :return:
    """
    image_json = []
    size_of_all_images = 0
    highest_res = (0, '0x0')
    lowest_res = (100000000, '10000x10000')
    counter = 1
    for img in all_images:
        # Make full url
        if bool(re.match(r'^/[A-Za-z]', img['src'])):
            img_url = 'https://hu.wikipedia.org' + img['src']
        elif bool(re.match(r'^//', img['src'])):
            img_url = 'https:' + img['src']
        else:
            img_url = img['src']

        # Get the resolution of the image
        extension = img['src'][-4:]
        if extension == '.svg':
            img_res = get_svg_size(img_url)
        elif extension.lower() == '.jpg' or extension.lower() == '.png':
            img_res = get_image_size(img_url)
        else:
            img_res = (0, 0)

        # Collect image data
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

    return image_json, size_of_all_images, highest_res, lowest_res


def collect_flag_json(flags):
    """
    Collect flags to JSON
    :param flags:
    :return:
    """
    flags_json = []
    for flag in flags:
        flags_json.append({'flag_image': 'https://' + flag[0], 'description': flag[1]})

    return flags_json


def make_statistics(statistics):
    """
    Make statistics
    :param statistics:
    :return:
    """
    if platform.system() == 'Windows' and re.match('10.*', platform.version()):
        command = 'scripts\\stat_gen.bat' + ' ' + ' '.join(statistics)
        os.system(command)
    elif platform.system() == 'Linux' and platform.version() == '20.04':
        command = 'sh scripts/stat_gen.sh' + ' ' + ' '.join(statistics)
        os.system(command)
    else:
        print('Unsupported OS version')


def main():
    link = 'https://hu.wikipedia.org/wiki/Formula%E2%80%931'
    html = requests.get(link)

    # Find all tables
    soup = BeautifulSoup(html.text, 'html.parser')
    tables = soup.find_all('table')

    # Find tables for active drivers, teams and manufacturers, flags
    driver_number_table, team_manufacturer_table, flag_table = extract_tables(tables)

    # -----------------------------
    # Extract active numbers, drivers and their wiki links
    # -----------------------------
    print("Extracting active drivers with their numbers...")
    filtered_td = driver_number_table.find_all('td')
    filtered_td = [td for td in filtered_td if not td.find('img')]

    driver_data = get_active_drivers(filtered_td)

    print("Active drivers extraction finished\n")

    # -----------------------------
    # Extract active drivers, their teams and numbers
    # -----------------------------
    print("Extracting active drivers with their teams...")
    drivers_with_teams = get_driver_with_teams(driver_data)

    print("Active drivers and teams extraction finished\n")

    # -----------------------------
    # Extract teams and motor manufacturers
    # -----------------------------
    print("Extracting teams and manufacturers...")
    teams, manufacturers = get_teams_and_manufacturers(team_manufacturer_table)

    print("Teams and manufacturers extraction finished\n")

    # -----------------------------
    # Extract flags and their descriptions
    # -----------------------------
    print("Extracting flags and descriptions...")
    flags, flags_images = get_flags(flag_table)

    print("Flags extraction finished\n")

    # -----------------------------
    # Extract all images from the page
    # -----------------------------
    print("Extracting images...")
    figures = soup.find_all('figure')

    # Collect all identifiers
    pilots = [r[0] for r in drivers_with_teams]
    identifier_words = teams + manufacturers + pilots

    # Remove duplicates
    identifier_words = list(dict.fromkeys(identifier_words))

    identified_images = []
    for figure in figures:
        if any(word in figure.find('figcaption').text for word in identifier_words):
            identified_images.append(figure.find('img'))

    all_images = soup.find_all('img')

    unidentified_images = [img for img in all_images if img not in identified_images]
    unidentified_images = [img for img in unidentified_images if img['src'] not in flags_images]

    # Create folders for identified, unidentified and flags images
    identified_path, unidentified_path, flags_path = create_directories()

    # Collect identified images
    download_identified_images(identified_images, identified_path)

    # Collect flags
    download_flags(flags_images, flags_path)

    # Collect unidentified images
    download_unidentified_images(unidentified_images, unidentified_path)

    print("Images extraction finished\n")

    # -----------------------------
    # JSON export
    # -----------------------------
    print("Exporting to JSON...")
    full_json = []

    # Collect drivers to JSON
    driver_json = collect_driver_json(drivers_with_teams)
    full_json.append({'drivers': driver_json})

    # Collect images to JSON
    image_json, size_of_all_images, highest_res, lowest_res = collect_img_json(all_images)
    full_json.append({'images': image_json})

    # Collect flags to JSON
    flags_json = collect_flag_json(flags)
    full_json.append({'flag_rules': flags_json})

    # Export to json
    with open('data.json', 'w') as file:
        json.dump(full_json, file)
    print("JSON is finished\n")

    # -----------------------------
    # Statistics
    # -----------------------------
    print("Making statistics...")
    statistics = [str(len(drivers_with_teams)),
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


if __name__ == '__main__':
    main()
