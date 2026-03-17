import os
import time
import certifi
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()
uri_banco = os.getenv("MONGO_URI")

client = MongoClient(uri_banco, tlsCAFile=certifi.where())
db = client["ufc_analytics"]
collection = db["lutadores_stats"]

print("Conectado ao banco de dados")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})
retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2 
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)

fighters_links = []
for char in 'abcdefghijklmnopqrstuvwxyz':
    url_list = f'http://ufcstats.com/statistics/fighters?char={char}&page=all'
    resp = session.get(url_list, timeout=15)
    soup = BeautifulSoup(resp.text, 'lxml')

    tbody = soup.find('tbody')
    if not tbody:
        continue
    for row in tbody.find_all('tr'):
        a = row.find('a')
        if a and a.get('href'):
            href = a['href']
            if href.startswith('http'):
                fighters_links.append(href)
            else:
                fighters_links.append('http://ufcstats.com' + href)
    time.sleep(1)

total_links = len(fighters_links)
print(f"Total de links coletados: {total_links}")

contador_inseridos = 0

for i, link in enumerate(fighters_links, 1):
    print(f"\rProcessando {i}/{total_links} - {contador_inseridos} lutadores qualificados salvos", end='', flush=True)
    
    try:
        resp = session.get(link, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        name = soup.find('span', class_='b-content__title-highlight').text.strip()
        record_text = soup.find('span', class_='b-content__title-record').text.strip()
        
        altura = "null"
        peso_categoria = "null"
        envergadura = "null"
        base = "null"
        
        slpm = td_avg = sub_avg = str_acc = str_def = td_acc = td_def = 0.0

        for li in soup.find_all('li', class_='b-list__box-list-item'):
            t = " ".join(li.text.split())
            
            try:
                if 'Height:' in t:
                    altura = t.split('Height:')[1].strip()
                elif 'Weight:' in t:
                    peso_categoria = t.split('Weight:')[1].strip()
                elif 'Reach:' in t:
                    envergadura = t.split('Reach:')[1].strip()
                elif 'STANCE:' in t:
                    base = t.split('STANCE:')[1].strip()
                elif 'SLpM:' in t:
                    slpm = float(t.split('SLpM:')[1].strip())
                elif 'Str. Acc.:' in t:
                    str_acc = float(t.split('Str. Acc.:')[1].replace('%', '').strip())
                elif 'Str. Def:' in t:
                    str_def = float(t.split('Str. Def:')[1].replace('%', '').strip())
                elif 'TD Avg.:' in t:
                    td_avg = float(t.split('TD Avg.:')[1].strip())
                elif 'TD Acc.:' in t:
                    td_acc = float(t.split('TD Acc.:')[1].replace('%', '').strip())
                elif 'TD Def.:' in t:
                    td_def = float(t.split('TD Def.:')[1].replace('%', '').strip())
                elif 'Sub. Avg.:' in t:
                    sub_avg = float(t.split('Sub. Avg.:')[1].strip())
            except:
                pass

        ufc_wins = 0
        ufc_losses = 0
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
                        result = cols[0].text.strip().lower()
                        if result == 'win':
                            ufc_wins += 1
                        elif result == 'loss':
                            ufc_losses += 1

        if ufc_fights < 7 or ufc_wins <= ufc_losses:
            continue

        documento_mongo = {
            "nome": name,
            "url_perfil": link,
            "cartel_geral": record_text.split(":")[1].strip(),
            "caracteristicas_fisicas": {
                "altura": altura,
                "peso_lbs": peso_categoria,
                "envergadura": envergadura,
                "base_luta": base
            },
            "experiencia_ufc": {
                "lutas": ufc_fights,
                "vitorias": ufc_wins,
                "derrotas": ufc_losses
            },
            "estatisticas": {
                "striking_volume_slpm": slpm,
                "striking_precisao_pct": str_acc,
                "striking_defesa_pct": str_def,
                "quedas_media_tdavg": td_avg,
                "quedas_precisao_pct": td_acc,
                "quedas_defesa_pct": td_def,
                "finalizacoes_media": sub_avg
            }
        }

        collection.update_one(
            {"url_perfil": link},
            {"$set": documento_mongo},
            upsert=True
        )
        
        contador_inseridos += 1
        time.sleep(1)
        
    except Exception as e:
        print(f"\nErro em {link}: {e}")
        continue

print(f"\n\nExtração concluída! Total de {contador_inseridos} lutadores salvos no banco.")