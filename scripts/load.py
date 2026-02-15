import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TRANSFORMED_DIR = BASE_DIR / 'transformed'

csv_path = TRANSFORMED_DIR / 'mma_com_estilos.csv'

if not csv_path.exists():
    print(f"ERRO: Arquivo não encontrado em {csv_path}")
    print("Rode primeiro: python scripts/transform.py")
    exit()

df = pd.read_csv(csv_path)

print("=" * 60)
print("ANÁLISE COMPLETA - LUTADORES UFC")
print("=" * 60)

print(f"\nTotal de lutadores analisados: {len(df)}")

print("\nDistribuição por estilo:")
print(df['estilo'].value_counts())

# Top Strikers
print("\n" + "=" * 60)
print("TOP 10 STRIKERS (maior SLpM)")
print("=" * 60)
strikers_top = df[df['estilo']=='Striker'].nlargest(10, 'slpm')
print(strikers_top[['nome', 'slpm', 'td_avg']].to_string(index=False))

# Top Grapplers por Takedowns
print("\n" + "=" * 60)
print("TOP 10 GRAPPLERS (maior TD Avg)")
print("=" * 60)
grapplers_top = df[df['estilo']=='Grappler'].nlargest(10, 'td_avg')
print(grapplers_top[['nome', 'td_avg', 'sub_avg']].to_string(index=False))

# Médias por estilo
print("\n" + "=" * 60)
print("MÉDIAS POR ESTILO")
print("=" * 60)
medias = df.groupby('estilo')[['slpm', 'td_avg', 'sub_avg']].mean().round(2)
print(medias)

print("\nAnalise completa")
