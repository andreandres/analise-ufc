import os
import pandas as pd
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
uri_banco = os.getenv("MONGO_URI")

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "raw_data"
RAW_DIR.mkdir(exist_ok=True)

print("Conectando ao banco de dados")

client = MongoClient(uri_banco, tlsCAFile=certifi.where())
db = client["ufc_analytics"]
collection = db["lutadores_stats"]

dados_brutos = list(collection.find({}, {'_id': 0}))

if not dados_brutos:
    print("Nenhum dado encontrado no banco de dados, rode o script extract.py primeiro")

else:
    df = pd.json_normalize(dados_brutos)

    caminho_saida = RAW_DIR / "mma_detailed.csv"
    df.to_csv(caminho_saida, index=False)
    print(f"Dados exportados para {caminho_saida}")
    print(df.head())
    