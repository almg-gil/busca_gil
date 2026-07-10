import io
import os
import sys
import time
from datetime import datetime
import pandas as pd
import requests
import psycopg2
from psycopg2.extras import execute_values

# Configurações obtidas das variáveis de ambiente (GitHub Actions ou Local)
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    print("❌ Erro: Variáveis de ambiente do banco de dados (DB_HOST, DB_PASSWORD, etc.) não foram configuradas.")
    sys.exit(1)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Referer": "https://dadosabertos.almg.gov.br/documentacao/arquivos/legislacao-mineira"
}[cite: 4]

pagina_base = "https://dadosabertos.almg.gov.br/documentacao/arquivos/legislacao-mineira"[cite: 4]
download_url = "https://dadosabertos.almg.gov.br/arquivo/legislacao-mineira/download"[cite: 4]

session = requests.Session()[cite: 4]
print("Obtendo cookies da página inicial...")
session.get(pagina_base, headers=headers, timeout=60)[cite: 4]

# Conectar ao Supabase
print("Conectando ao banco de dados Supabase...")
conn = psycopg2.connect(
    host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
)
cur = conn.cursor()

print("Iniciando a esteira de download de dados...")
for ano in range(1947, datetime.now().year + 1):[cite: 4]
    print(f"Baixando ano {ano}...")[cite: 4]
    params = {"ano": str(ano), "tipo": "CSV"}[cite: 4]
    
    try:
        r = session.get(download_url, params=params, headers=headers, timeout=120)[cite: 4]
        tamanho = len(r.content)[cite: 4]
        print("Status:", r.status_code, "| tamanho:", tamanho)[cite: 4]
        
        if r.status_code == 200 and tamanho > 1000:[cite: 4]
            csv_buffer = io.StringIO(r.content.decode("utf-8"))[cite: 4]
            df = pd.read_csv(csv_buffer)[cite: 4]
            
            # Limpeza e padronização de colunas para bater com o banco
            df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()
            
            # Mapeamento do CSV para as colunas do banco do Supabase
            df_mapeado = pd.DataFrame()
            df_mapeado["id_cadastro_geral_silegis"] = pd.to_numeric(df["IdCadastroGeralSilegis"], errors="coerce")
            df_mapeado["tipo_sigla"] = df["Tipo"].astype(str).str.strip().str.upper()
            df_mapeado["numero"] = df["Numero"].astype(str).str.strip()
            df_mapeado["ano"] = pd.to_numeric(df["Ano"], errors="coerce")
            df_mapeado["situacao"] = df["Situacao"].astype(str).str.strip()
            df_mapeado["data_publicacao"] = df["DataPublicacao"].astype(str).str.strip()
            df_mapeado["ementa"] = df["Ementa"].astype(str).str.strip()
            df_mapeado["resumo"] = df["Resumo"].astype(str).str.strip()
            df_mapeado["indexacao"] = df["Indexacao"].astype(str).str.strip()
            df_mapeado["observacao"] = df["Observacao"].astype(str).str.strip()
            df_mapeado["link_texto_original"] = df["LinkTextoOriginal"].astype(str).str.strip()
            df_mapeado["link_texto_atualizado"] = df["LinkTextoAtualizado"].astype(str).str.strip()
            df_mapeado["data_atualizacao_catalogo"] = df["DataAtualizacao"].astype(str).str.strip()
            
            # Remove linhas inválidas ou sem ID primário
            df_mapeado = df_mapeado.dropna(subset=["id_cadastro_geral_silegis"])
            df_mapeado["id_cadastro_geral_silegis"] = df_mapeado["id_cadastro_geral_silegis"].astype(int)
            
            # Substitui NaNs por strings vazias para o Postgres aceitar
            df_mapeado = df_mapeado.fillna("")
            
            registros = df_mapeado.to_records(index=False).tolist()
            
            # Query em lote (Batch) com UPSERT: se a norma já existir, atualiza os dados do catálogo
            query_upsert = """
                INSERT INTO textos_normas (
                    id_cadastro_geral_silegis, tipo_sigla, numero, ano, situacao, data_publicacao,
                    ementa, resumo, indexacao, observacao, link_texto_original, link_texto_atualizado, data_atualizacao_catalogo
                ) VALUES %s
                ON CONFLICT (id_cadastro_geral_silegis) DO UPDATE SET
                    tipo_sigla = EXCLUDED.tipo_sigla,
                    numero = EXCLUDED.numero,
                    ano = EXCLUDED.ano,
                    situacao = EXCLUDED.situacao,
                    data_publicacao = EXCLUDED.data_publicacao,
                    ementa = EXCLUDED.ementa,
                    resumo = EXCLUDED.resumo,
                    indexacao = EXCLUDED.indexacao,
                    observacao = EXCLUDED.observacao,
                    link_texto_original = EXCLUDED.link_texto_original,
                    link_texto_atualizado = EXCLUDED.link_texto_atualizado,
                    data_atualizacao_catalogo = EXCLUDED.data_atualizacao_catalogo;
            """
            
            execute_values(cur, query_upsert, registros)
            conn.commit()
            print(f"Salvo no Supabase: {len(df_mapeado)} normas para o ano {ano}")
        else:
            print("Sem dados válidos para", ano)[cite: 4]
            
    except Exception as e:
        print(f"Erro no ano {ano}: {e}")[cite: 4]
        
    time.sleep(1)[cite: 4]

cur.close()
conn.close()
print("\n✅ Catálogo no Supabase atualizado com sucesso!")
