import requests
from bs4 import BeautifulSoup as bs
import re
from urllib.parse import unquote
import csv
import time

url = "https://en.wikipedia.org/wiki/2024_Summer_Olympics"
response = requests.get(url)

if response.status_code == 200:
    print("Started...")

    # Get URLs for each country
    soup = bs(response.content, 'html.parser')
    tables = soup.find_all('table')
    table = None
    for tbl in tables:
        if "Participating National Olympic Committees" in tbl.get_text():
            table = tbl
            break

    if table:
        print("Get URLs for each country...")
        links = table.find_all('a', href=True, title=True)
        urls_by_country = []
        for link in links:
            if "Afghanistan_at_the_2024_Summer_Olympics" in link['href'] or "Canada_at_the_2024_Summer_Olympics" in link['href']:
                full_url = "https://en.wikipedia.org" + link['href']
                urls_by_country.append(full_url)

    else:
        print("Table Participating National Olympic Committees not found")
        urls_by_country = []

    pattern = re.compile(r'(?<=/wiki/)([^_]+(?:_[^_]+)*)(?=_at)')
    data = []
    
    for url in urls_by_country:
        # Find country_name
        match_country = pattern.findall(url)
        if match_country:
            match_country_cleaned = match_country[0].replace('_', ' ')
            match_country_cleaned = unquote(match_country_cleaned)
            country_name = match_country_cleaned
        else:
            continue

        print(f"Finding competitors for {country_name}...")
        response = requests.get(url)
        if response.status_code == 200:
            html = response.content
            soup = bs(html, 'html.parser')
            table_class = "wikitable sortable jquery-tablesorter"
            tables = soup.find_all('table', {'class': table_class})

            if tables:
                table = tables[1] if len(tables) > 1 else tables[0]
                rows = table.find('tbody').find_all('tr')
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 4:  # Check if there are 4 columns
                        sport = cols[0].get_text(strip=True)
                        men = cols[1].get_text(strip=True)
                        women = cols[2].get_text(strip=True)
                        total = cols[3].get_text(strip=True)
                        data.append([country_name, sport, men, women, total])
                    else:
                        print(f"Row skipped for {country_name} due to unexpected column count")
            else:
                print(f"Table: {table_class} not found for {country_name}")
                
        else:
            print(f"Failed to get {url} Status code:{response.status_code}")

    # Write data to CSV
    with open('olympics_competitors.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Country', 'Sport', 'Men', 'Women', 'Total'])
        # Write data
        writer.writerows(data)

    print("Data has been written to olympics_competitors.csv")

else:
    print("Failed! Status code:", response.status_code)
