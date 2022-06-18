import os
import re
import time
import logging
import requests
import json
import pandas as pd
logging.basicConfig(level=logging.INFO,filename='history.log', format='%(asctime)s:%(levelname)s:%(message)s')

def get_addresses(filename=None):
    """Get input addresses"""
    with open(filename, 'r') as f:
        addresses = f.read().splitlines()
    # Lower case all values
    addresses = [x.lower() for x in addresses]
    addresses = [x.replace(' ', '+') for x in addresses]
    return addresses

def find_lat_long(x=None):
    """Function to parse out latitude and longitude"""
    check_if_match = re.search('location', x)
    if check_if_match:
        get_lat_long_string = re.search(r"location(.*?)}", x).group(1)
        get_lat_string = re.search(r"'lat':(.*?),", get_lat_long_string).group(1)
        latitude = get_lat_string.split()[0]
        get_long_string = re.search(r"'lng':(.*?)$", get_lat_long_string).group(1)
        longitude = get_long_string.split()[0]
    else:
        return "No value returned."
    return f"({latitude},{longitude})"

if __name__ == "__main__":
    addresses = get_addresses('./input.txt')
    #print(addresses)

    core_path = "https://maps.googleapis.com/maps/api/geocode/json?address="
    api_key = os.environ['API_KEY']
    df = pd.DataFrame()
    for address in addresses:
        path = core_path + str(address) + '&key=' + api_key
        response = requests.get(path)
        status, reason, resp_headers, resp_content = response.status_code, response.reason, response.headers, response.content
        print(f"response status code: {status}")
        #print(f"response status: {reason}")
        #print(f"response headers: {resp_headers}")
        #print(f"response content: {resp_content}")
        resp_content_json = json.loads(resp_content.decode('utf-8'))
        logging.info(resp_content_json)
        print(resp_content_json)

        df = df.append(resp_content_json['results'])
        time.sleep(2)

    # Final edits
    df = df.drop('address_components', axis=1)
    df['Lat/Long'] = df.apply(lambda x: find_lat_long(str(x['geometry'])), axis=1)
    df.to_csv('lat-long-results.csv', index=False, encoding='utf-8')
