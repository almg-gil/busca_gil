import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extras import RealDictCursor

# Configurações obtidas das variáveis de ambiente (GitHub Actions ou Local)
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

INTERVALO = 0.5 # Tempo de espera entre requisições da API[cite: 5]
TIMEOUT = 60[cite: 5]

def normalizar_link_api(link):
    if not link: return ""[cite: 5]
    if "conteudo=true" not in link:[cite: 5]
        uniao = "&" if "?" in link else "?"[cite: 5]
        link += f"{uniao}conteudo=true&texto=true"[cite: 5]
    return link[cite: 5]

def extrair_texto_xml(conteudo):
    try:
        root = ET.fromstring(conteudo)[cite: 5]
        textos = [][cite: 5]
        for elemento in root.findall(".//texto"):[cite: 5]
            texto = "".join(elemento.itertext()).strip()[cite: 5]
            if texto and texto not in textos: textos.append(texto)[cite: 5]
        if not textos:[cite: 5]
            for elemento in root.findall(".//conteudo"):[cite: 5]
                texto = "".join(elemento.itertext()).strip()[cite: 5]
                if texto and texto not in textos: textos.append(texto)[cite: 5]
        return "\n\n".join(textos) if textos else ""[cite: 5]
    except:
        return ""

def baixar_texto(link):
    link = normalizar_link_api(link)[cite: 5]
    if not link: return ""[cite: 5]
    try:
        r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=TIMEOUT)[cite: 5]
        if r.status_code == 200:[cite: 5]
            texto = extrair_texto_xml(r.content)[cite: 5]
            if not texto:[cite: 5]
                texto_bruto = r.text.strip()[cite: 5]
                if texto_bruto and "<html" not in texto_bruto.lower(): texto = texto_bruto[cite: 5]
            return texto[cite: 5]
    except Exception as e:
        print(f"Erro na requisição: {e}")
    return ""

if __name__ == "__main__":
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        print("❌ Erro: Variáveis de ambiente do banco de dados não configuradas.")
        sys.exit(1)

    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
    
    # Coleta 1: Buscar e preencher Texto Original pendente
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id_cadastro_geral_silegis, link_texto_original, tipo_sigla, numero, ano 
        FROM textos_normas 
        WHERE link_texto_original IS NOT NULL AND link_texto_original <> '' 
          AND (texto_original IS NULL OR texto_original = '')
        LIMIT 300;
    """)
    pendentes_originais = cur.fetchall()
    print(f"Pendentes de Texto Original localizados: {len(pendentes_originais)}")
    
    for row in pendentes_originais:
        id_norma = row["id_cadastro_geral_silegis"]
        print(f"Baixando Original para: {row['tipo_sigla']} {row['numero']}/{row['ano']}")
        texto = baixar_texto(row["link_texto_original"])
        
        if texto:
            cur.execute(
                "UPDATE textos_normas SET texto_original = %s, ultima_atualizacao_coleta = NOW() WHERE id_cadastro_geral_silegis = %s",
                (texto, id_norma)
            )
            conn.commit()
        time.sleep(INTERVALO)[cite: 5]

    # Coleta 2: Buscar e preencher Texto Consolidado pendente
    cur.execute("""
        SELECT id_cadastro_geral_silegis, link_texto_atualizado, tipo_sigla, numero, ano 
        FROM textos_normas 
        WHERE link_texto_atualizado IS NOT NULL AND link_texto_atualizado <> '' 
          AND (texto_consolidado IS NULL OR texto_consolidado = '')
        LIMIT 300;
    """)
    pendentes_consolidados = cur.fetchall()
    print(f"Pendentes de Texto Consolidado localizados: {len(pendentes_consolidados)}")
    
    for row in pendentes_consolidados:
        id_norma = row["id_cadastro_geral_silegis"]
        print(f"Baixando Consolidado para: {row['tipo_sigla']} {row['numero']}/{row['ano']}")
        texto = baixar_texto(row["link_texto_atualizado"])
        
        if texto:
            cur.execute(
                "UPDATE textos_normas SET texto_consolidado = %s, ultima_atualizacao_coleta = NOW() WHERE id_cadastro_geral_silegis = %s",
                (texto, id_norma)
            )
            conn.commit()
        time.sleep(INTERVALO)[cite: 5]

    cur.close()
    conn.close()
    print("\n✅ Coleta de textos concluída com sucesso na nuvem!")
