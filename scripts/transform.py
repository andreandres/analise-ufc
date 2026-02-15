import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  
TRANSFORMED_DIR = BASE_DIR / 'transformed'
RAW_DIR = BASE_DIR / 'raw_data'

TRANSFORMED_DIR.mkdir(exist_ok=True)

df = pd.read_csv(f'{RAW_DIR}/mma_detailed.csv')

df["slpm"] = df["slpm"].fillna(0.0)
df["td_avg"] = df["td_avg"].fillna(0.0)
df["sub_avg"] = df["sub_avg"].fillna(0.0) 

def style(row):
    if row['slpm'] > 3.5 and row['td_avg'] < 2.0:
        return 'Striker'
    elif row['td_avg'] > 2.5 or row['sub_avg'] > 1.0:
        return 'Grappler'
    return 'Balanced'

df['estilo'] = df.apply(style, axis=1)

df.to_csv('transformed/mma_com_estilos.csv', index=False)
df[df['estilo']=='Striker'].to_csv(TRANSFORMED_DIR / 'strikers.csv', index=False)
df[df['estilo']=='Grappler'].to_csv(TRANSFORMED_DIR / 'grapplers.csv', index=False)
df[df['estilo']=='Balanced'].to_csv(TRANSFORMED_DIR / 'balanced.csv', index=False)


print("Concluido!\n")
print(f"Total lutadores: {len(df)}")
print(f"Strikers: {len(df[df['estilo']=='Striker'])}")
print(f"Grapplers: {len(df[df['estilo']=='Grappler'])}")
print(f"Balanceados: {len(df[df['estilo']=='Balanced'])}\n")
