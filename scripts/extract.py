import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
import time

BASE_DIR = Path(__file__).parent.parent 
RAW_DIR = BASE_DIR / 'raw_data'

RAW_DIR.mkdir(exist_ok=True)


url_list = 'http://ufcstats.com/statistics/fighters?char=a&page=all'
resp = requests.get(url_list)
soup = BeautifulSoup(resp.text, 'lxml')

fighters_links = []
for row in soup.find('tbody').find_all('tr'):
    a = row.find('a')
    if a and a.get('href'):
        href = a['href']
        if href.startswith('http'):
            fighters_links.append(href)
        else:
            fighters_links.append('http://ufcstats.com' + href)

data = []
data = []
TARGET_COUNT = 10

for i, link in enumerate(fighters_links):
    if len(data) >= TARGET_COUNT:
        break
        
    try:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        
        name = soup.find('span', class_='b-content__title-highlight').text.strip()
        
        record_text = soup.find('span', class_='b-content__title-record').text.strip()
        
        # Contar Lutas no UFC
        ufc_fights = 0
        history_table = soup.find('table', class_='b-fight-details__table')
        if history_table:
            rows = history_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 6:
                    event_name = cols[6].text.strip()
                    if 'UFC' in event_name:
                        ufc_fights += 1

        if ufc_fights < 5:
            continue

        
        slpm = td_avg = sub_avg = 0.0
        
        for li in soup.find_all('li', class_='b-list__box-list-item'):
            t = li.text.strip()
            try:
                if 'SLpM' in t:
                    slpm = float(t.split('SLpM:')[1].strip().split()[0])
                if 'TD Avg.' in t:
                    td_avg = float(t.split('TD Avg.:')[1].strip().split()[0])
                if 'Sub. Avg.' in t:
                    sub_avg = float(t.split('Sub. Avg.:')[1].strip().split()[0])
            except (ValueError, IndexError):
                pass
        
        data.append({
            "nome": name, 
            "slpm": slpm, 
            "td_avg": td_avg, 
            "sub_avg": sub_avg, 
            "ufc_fights": ufc_fights,
            "record": record_text.split(":")[1].strip()
        })
        time.sleep(1)
        
    except Exception as e:
        print(f"Erro em {link}: {e}")
        continue



df_raw = pd.DataFrame(data)
df_raw.to_csv(f'{RAW_DIR}/mma_detailed.csv', index=False)
print("\nExtracao concluida!")
print(df_raw.head())