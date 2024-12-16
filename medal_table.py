from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Setup Selenium
path = r'C:\Users\SARUNPAX\Desktop\project-for learning\sc\chromedriver.exe'  
chrome_options = Options()
# chrome_options.add_argument("--headless") 
service = Service(path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define countries to scrape
countries_list = ['albania', 'algeria', 'argentina', 'armenia', 'australia', 'austria', 'azerbaijan', 'bahrain', 'belgium',
                  'botswana', 'brazil', 'bulgaria', 'cabo-verde', 'canada', 'chile', 'colombia', 'cote-d-ivoire', 'croatia', 'cuba',
                  'cyprus', 'czechia', 'dpr-korea', 'denmark', 'dominica', 'dominican-republic', 'ecuador', 'egypt', 'ethiopia', 'fiji',
                  'france', 'georgia', 'germany', 'great-britain', 'greece', 'grenada', 'guatemala', 'hong-kong-china', 'hungary', 'india',
                  'indonesia', 'ireland', 'ir-iran', 'israel', 'italy', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kosovo', 'kyrgyzstan',
                  'lithuania', 'malaysia', 'mexico', 'mongolia', 'morocco', 'netherlands', 'new-zealand', 'norway', 'pakistan', 'panama', 'china',
                  'peru', 'philippines', 'poland', 'portugal', 'puerto-rico', 'qatar', 'eor', 'korea', 'republic-of-moldova', 'romania', 'saint-lucia',
                  'serbia', 'singapore', 'slovakia', 'slovenia', 'south-africa', 'spain', 'sweden', 'switzerland', 'tajikistan', 'thailand', 'chinese-taipei',
                  'tunisia', 'turkiye', 'uganda', 'ukraine', 'united-states', 'uzbekistan', 'zambia']

countries_list_len = len(countries_list)
count = 1
try:
    all_data = {}
    first_country = True

    for country in countries_list:
        try:
            print(f'Started scraping data for {country}... | {count} out of {countries_list_len}')
            url = f"https://olympics.com/en/paris-2024/medals/{country}"

            driver.get(url)
            time.sleep(2)

            # Click the cookie accept button only for the first country
            if first_country:
                try:
                    accept_button_cookie = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
                    )
                    accept_button_cookie.click()
                    first_country = False  # Set to False after clicking
                except:
                    print("Cookie accept button not found or already accepted.")

            collapse_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="p2024-main-content"]/div[1]/div[1]/div/div[1]/div[2]/button'))
            )
            collapse_button.click()
            time.sleep(1)
            html = driver.page_source
            soup = bs(html, 'html.parser')
            # print(soup.prettify())
            sports = soup.find_all('div', {'class': 'emotion-srm-1qme0ry'})
            
            data = {}
            events_data = []

            if sports:
                data[country] = {}

                for sport in sports:
                    sport_medal_elements = sport.find_all('div', {'class': 'emotion-srm-1oyaqcr elzx0n30'})
                    sport_event_elements = sport.find_all('div', {'class': 'emotion-srm-6l9pan'})
                    
                    for sport_medal_element in sport_medal_elements:
                        try:
                            sport_name = sport_medal_element.find('span', {'class': 'elzx0n31 emotion-srm-1styswf'}).text.strip()
                            medals = sport_medal_element.find_all('span', {'class': 'e1oix8v91 emotion-srm-1bh15i7'})
                            gold = medals[0].text.strip()
                            silver = medals[1].text.strip()
                            bronze = medals[2].text.strip()
                            total = sport_medal_element.find('span', {'class': 'e1oix8v91 emotion-srm-1xl957n'}).text.strip()
                            
                            data[country][sport_name] = {
                                'gold': gold,
                                'silver': silver,
                                'bronze': bronze,
                                'total': total,
                                'events': [],
                                'temp_gold': int(gold),
                                'temp_silver': int(silver),
                                'temp_bronze': int(bronze)
                            }
                        except Exception as e:
                            print(f"Error processing sport medal data for {country}: {e}")
                            continue

                    for sport_event_element in sport_event_elements:
                        event_details = sport_event_element.find_all('div', {'class': 'emotion-srm-14s0sqk e1nfau490'})
                        for event_detail in event_details:
                            try:
                                events = event_detail.find('div', {'class': 'emotion-srm-157if6k e1nfau491'})
                                if events:
                                    anchor_tag = events.find('a')
                                    if anchor_tag:
                                        event = anchor_tag.text.strip()
                                    else:
                                        span_tag = events.find('span')
                                        if span_tag:
                                            event = span_tag.text.strip()
                                        else:
                                            event = "N/A"
                                else:
                                    event = "N/A"
                                    
                                athletes_name = event_detail.find('div', {'class': 'emotion-srm-70qvj9 e1qok5fm0'})
                                if athletes_name:
                                    a_tag = athletes_name.find('a')
                                    if a_tag:
                                        athlete_name = a_tag.text.strip()
                                    else:
                                        span_tag = athletes_name.find('span')
                                        if span_tag:
                                            athlete_name = span_tag.text.strip()
                                        else:
                                            athlete_name = 'N/A'
                                else:
                                    athlete_name = 'N/A'
                                    
                                medal_type_div = event_detail.find('div', {'class': 'emotion-srm-r44ruj e1uhuzof1'})
                                if medal_type_div:
                                    medal_type_span = medal_type_div.find('span')
                                    if medal_type_span:
                                        medal_type = medal_type_span.text.strip()
                                        if medal_type == 'G':
                                            medal_type = 'Gold'
                                            medal_code = 1
                                        elif medal_type == 'S':
                                            medal_type = 'Silver'
                                            medal_code = 2
                                        else:
                                            medal_type = 'Bronze'
                                            medal_code = 3
                                    else:
                                        medal_type = "N/A"
                                        medal_code = 0
                                else:
                                    medal_type = "N/A"
                                    medal_code = 0
                                
                                events_data.append({
                                    'event': event,
                                    'athlete': athlete_name,
                                    'medal': medal_type,
                                    'medal_code': medal_code
                                })
                            except Exception as e:
                                print(f"Error processing event data for {country}: {e}")
                                continue
                
                for event in events_data:
                    for sport_name, sport_info in data[country].items():
                        if event['medal'] == 'Gold' and sport_info['temp_gold'] > 0:
                            sport_info['events'].append(event)
                            sport_info['temp_gold'] -= 1
                            break
                        elif event['medal'] == 'Silver' and sport_info['temp_silver'] > 0:
                            sport_info['events'].append(event)
                            sport_info['temp_silver'] -= 1
                            break
                        elif event['medal'] == 'Bronze' and sport_info['temp_bronze'] > 0:
                            sport_info['events'].append(event)
                            sport_info['temp_bronze'] -= 1
                            break

                all_data.update(data)
                print(f"Finished scraping data for {country}\n")
                count = count+1
            else:
                print(f"No sports data found for {country}")
                count = count+1

        except Exception as e:
            print(f"Error scraping data for {country}: {e}")
            continue

    rows = []
    for country, sports_info in all_data.items():
        for sport, info in sports_info.items():
            for event in info['events']:
                row = [country, sport, event['event'], event['athlete'], event['medal'], event['medal_code']]
                rows.append(row)

    csv_file = "olympics_medals.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['country', 'sport_name', 'event', 'athlete_name', 'medal_type', 'medal_code'])
        writer.writerows(rows)

    print(f"Data has been written to {csv_file}")
                    
finally:
    driver.quit()
