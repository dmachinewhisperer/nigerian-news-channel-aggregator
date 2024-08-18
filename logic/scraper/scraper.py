import os
import pytz
import json
import sqlite3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


# the RSS feed list is maintained in a separate repository
# a static copy is included in this project
# for the newer copies see: https://github.com/dmachinewhisperer/nigerian-news-channel-rss-feeds
# SITE_RSS_FEED_URLS_PATH = "../../nigerian-news-channel-rss-feeds"

#configs
SQLITE_DATABASE_PATH = '../instance/app.db'
SITE_RSS_FEED_URLS_PATH = './'
RSS_FOLDER = 'rss-feeds'
TIME_WINDOW_HOURS = 6


def log(message, verbose):
    if verbose:
        print(message)

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS historical
    (id INTEGER PRIMARY KEY, name TEXT, pubDate TEXT, title TEXT, description TEXT, link TEXT)
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS current
    (id INTEGER PRIMARY KEY, name TEXT, pubDate TEXT, title TEXT, description TEXT, link TEXT)
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_processed
    (id INTEGER PRIMARY KEY, last_processed TEXT)
    ''')
    conn.commit()

#all time format should be in ISO 8601 format supported by sqlite
def parse_date(date_str):
    return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
    

def fetch_rss(url, file_path):
    print(f"fetching feed for {url}...", end='')
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Referer": url
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print("Done.")
        return True
    return False

 
def process_rss_feed(conn, site_id, site_name, rss_url, test = False):
    file_path = os.path.join(RSS_FOLDER, f"{site_id}.xml")

    cursor = conn.cursor()
    
    #it is possible that the rss feed is rebuilt while this processing is going on.
    #to avoid potencially missing out on news items published at this time, the time here 
    #will be stored as the last_processed time 
    current_time = datetime.now(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    
    # if test is set, we are testing the algorithm without downloading the rss feeds. 
    # older rss feeds is processed in this case if they exist. 
    if test:
        if not os.path.isfile(file_path): return False
    if not test:
        if not fetch_rss(rss_url, file_path):
            print(f"Failed to fetch RSS for {site_name}")
            return False

    # strip the xml and attempt parsing
    try:
        with open(file_path, 'r+', encoding='utf-8') as file:
            content = file.read().lstrip()
            file.seek(0) 
            file.write(content) 
            file.truncate() 
            file.seek(0)

            tree = ET.parse(file)
            root = tree.getroot()


    except ET.ParseError as e:
        print(f"XML Parse Error for {site_name}: {e}")
    except Exception as e:
        print(f"An error occurred while processing RSS for {site_name}: {e}")


    last_build_date = root.find('.//lastBuildDate')
    if last_build_date is None:
        print(f"No lastBuildDate found for {site_name}")
        return False

    last_build_date = parse_date(last_build_date.text.strip())

    cursor.execute("SELECT last_processed FROM last_processed WHERE id = ?", (site_id,))
    result = cursor.fetchone()

    is_first_time_processed = False
    if result:
        last_processed = parse_date(result[0])
        if last_build_date <= last_processed:
            print(f"No new items for {site_name}")
            return True
    else:
        #if no entry is found for for this news source, create an entry for it
        #set last_processed to some time value behind current time
        is_first_time_processed = True
        last_processed = (datetime.now(pytz.utc) - 
                          timedelta(hours=TIME_WINDOW_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO last_processed (id, last_processed) VALUES (?, ?)",
                       (site_id, last_processed))

    for item in root.findall('.//item'):
        pub_date = item.find('pubDate')
        pub_date = parse_date(pub_date.text.strip()) if pub_date is not None else ''

        #for articles we are not processing for the first time, if publication data is older 
        # than the last_processed time, it means we have processed this item in the rss file before
        if pub_date < last_processed and not is_first_time_processed :
           continue
        title = item.find('title')
        title = title.text.strip() if title is not None else ''
        description = item.find('description')
        description = description.text.strip() if description is not None else ''
        link = item.find('link')
        link = link.text.strip() if link is not None else ''

        '''
        media_url = ''
        media = item.find('.//{http://search.yahoo.com/mrss/}content')
        if media is not None:
            media_url = media.get('url', '')
        '''

        cursor.execute('''
        INSERT INTO historical (name, pubDate, title, description, link)
        VALUES (?, ?, ?, ?, ?)
        ''', (site_name, pub_date, title, description, link))

        cursor.execute('''
        INSERT INTO current (name, pubDate, title, description, link)
        VALUES (?, ?, ?, ?, ?)
        ''', (site_name, pub_date, title, description, link))

    cursor.execute("UPDATE last_processed SET last_processed = ? WHERE id = ?",
                   (current_time, site_id))
    conn.commit()
    
    return True

def clean_current_table(conn):
    cursor = conn.cursor()
    cutoff_time = (datetime.now(pytz.utc) - 
                   timedelta(hours=TIME_WINDOW_HOURS)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
    DELETE FROM current
    WHERE pubDate < ?
    ''', (cutoff_time,))
    
    conn.commit()

def main():
    conn = sqlite3.connect(SQLITE_DATABASE_PATH)
    create_tables(conn)

    with open(f'{SITE_RSS_FEED_URLS_PATH}/sites.json', 'r') as f:
        sites = json.load(f)

    for site in sites['data']:
        site_id = site['id']
        site_name = site['name']
        rss_url = site['feed']
        
        #process only sites with rss feeds
        if rss_url:
            #process_rss_feed(conn, site_id, site_name, rss_url)

            #tests
            result = process_rss_feed(conn, site_id, site_name, rss_url, True)
            print(f"Could not parse xml for {rss_url}") if not result else print(f"{rss_url}: Done")
            if not result: print(f"Could not parse xml for {rss_url}")

    clean_current_table(conn)
    conn.close()

if __name__ == "__main__":
    main()