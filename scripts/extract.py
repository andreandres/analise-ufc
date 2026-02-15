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
for row in soup.find('tbody').find_all('tr')[:101]:
    a = row.find('a')
    if a and a.get('href'):
        href = a['href']
        if href.startswith('http'):
            fighters_links.append(href)
        else:
            fighters_links.append('http://ufcstats.com' + href)

data = []
for i, link in enumerate(fighters_links):
    print(f"Extraindo {i+1}/{len(fighters_links)}: {link}")
    
    try:
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Nome do lutador
        name = soup.find('span', class_='b-content__title-highlight').text.strip()
        
        # Stats individuais (inicializa zerados)
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
        
        data.append({"nome": name, "slpm": slpm, "td_avg": td_avg, "sub_avg": sub_avg})
        time.sleep(1.5)
        
    except Exception as e:
        print(f"Erro em {link}: {e}")
        continue



df_raw = pd.DataFrame(data)
df_raw.to_csv(f'{RAW_DIR}/mma_detailed.csv', index=False)
print("\nExtracao concluida!")
print(df_raw.head())