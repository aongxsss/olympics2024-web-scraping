import requests
from bs4 import BeautifulSoup as bs
import re
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv

# Setup driver
path = r'C:\Users\SARUNPAX\Desktop\project-for learning\sc\chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(path)
driver = webdriver.Chrome(options=chrome_options)

# parse num
def parse_number(text):
    
    try:
        return int(float(text))  
    except ValueError:
        return 0
    
# URL
url = "https://en.wikipedia.org/wiki/2024_Summer_Olympics"


    
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an HTTPError for bad responses

    print("Started...")
    
    # Get urls for each country   
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
       
            # if "France_at_the_2024_Summer_Olympics" in link['href']:
            # if "Afghanistan_at_the_2024_Summer_Olympics" in link['href'] or "Canada_at_the_2024_Summer_Olympics" in link['href']:
            if not ("/wiki/Category:Nations_at_the_2024_Summer_Olympics" in link['href'] or "Qatar_at_the_2024_Summer_Olympics" in link['href']):
                full_urls = "https://en.wikipedia.org" + link['href']
                urls_by_country.append(full_urls)

    else:
        print("Table Participating National Olympic Committees not found")
        urls_by_country = []
    pattern = re.compile(r'(?<=/wiki/)([^_]+(?:_[^_]+)*)(?=_at)')
    countries = []
    total_countries = len(urls_by_country)-1
    print("total_countries: ", total_countries)
    count = 1
    data = []

    for url in urls_by_country:
        try:
            # Find country name
            match_country = pattern.findall(url)
            if match_country:
                match_country_cleaned = match_country[0].replace('_', ' ')
                match_country_cleaned = unquote(match_country_cleaned)
                countries.append(match_country_cleaned)
                country_name = countries[-1]
                
                driver.get(url)
                time.sleep(3)
                html = driver.page_source
                soup = bs(html, 'html.parser')
                
                table_class = 'wikitable' if country_name == 'Moldova' else 'wikitable sortable jquery-tablesorter'
                tables = soup.find_all('table', {'class': table_class})
                
                if tables:
                    print(f"Fetching competitors data for {country_name}... | {count} out of {total_countries}")
                    if country_name == 'Moldova':
                        table = tables[4]
                    elif country_name in ['Malaysia','Philippines']:
                        table = tables[2]
                    elif country_name in ['Azerbaijan', 'Ukraine']:
                        table = tables[0]  
                    else:
                        table = tables[1] if len(tables) > 1 else tables[0]

                        
                    rows = table.find('tbody').find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 4:  # Check if there are enough columns
                            sport = cols[0].get_text(strip=True)
                            men_text = cols[1].get_text(strip=True)
                            women_text = cols[2].get_text(strip=True)
                            total_text = cols[3].get_text(strip=True)
                            
                            men = parse_number(men_text)
                            women = parse_number(women_text)
                            total = parse_number(total_text)
                            
                            data.append([country_name, sport, men, women, total])
                            
                        else:
                            print("Table format is incorrect")

                    count = count +1     

                else:
                    print(f"Table: {table_class} not found for {country_name}")
            else:
                print("ํURLS not matching")
        
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    if data:
        with open('olympics_competitors_latest.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Header
            writer.writerow(['Country', 'Sport', 'Men', 'Women', 'Total'])
            # Rows
            writer.writerows(data)
            print("Data has been written to olympics_competitors.csv")
    else:
        print("No data to write to CSV")
        
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch {url}. Error: {e}")

finally:
    driver.quit()
