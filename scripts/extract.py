import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
uri_banco = os.getenv("MONGO_URI")

client = MongoClient(uri_banco, tlsCAFile=certifi.where())
db = client["ufc_analytics"]
collection = db["lutadores_stats"]

print("Conectado ao banco de dados")


fighters_links = []
for char in 'abcdefghijklmnopqrstuvwxyz':
    url_list = f'http://ufcstats.com/statistics/fighters?char={char}&page=all'
    resp = requests.get(url_list)
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
        resp = requests.get(link)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        name = soup.find('span', class_='b-content__title-highlight').text.strip()
        record_text = soup.find('span', class_='b-content__title-record').text.strip()
        
        # Contar Vitórias e Derrotas no UFC
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
        
        documento_mongo = {
            "nome": name,
            "url_perfil": link,
            "cartel_geral": record_text.split(":")[1].strip(),
            "experiencia_ufc": {
                "lutas": ufc_fights,
                "vitorias": ufc_wins,
                "derrotas": ufc_losses
            },
            "estatisticas": {
                "slpm": slpm,
                "td_avg": td_avg,
                "sub_avg": sub_avg
            }
        }

        collection.update_one(
            {"url_perfil": link},
            {"$set": documento_mongo},
            upsert=True
        )
        contador_inseridos += 1
        
        #Sleep pro servidor n achar q e bot xing ling
        time.sleep(1)
        
    except Exception as e:
        print(f"\nErro em {link}: {e}")
        continue

print(f"\n\nExtração concluída! Total de {contador_inseridos} lutadores salvos no banco.")