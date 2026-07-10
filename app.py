import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Silegis - Busca de Normas", layout="wide")

# Conectar ao Supabase
@st.cache_resource
def conectar_banco():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        sslmode="require"
    )

# Função rápida para buscar os textos completos APENAS quando o usuário clicar
def buscar_texto_completo(id_silegis):
    conn = conectar_banco()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT resumo, indexacao, observacao, texto_consolidado, texto_original FROM textos_normas WHERE id_cadastro_geral_silegis = %s",
            (id_silegis,)
        )
        return cursor.fetchone()

st.title("🏛️ Silegis - Busca de Normas (Supabase + Streamlit)")

termo = st.text_input("Digite o termo de busca (Ex: 'meio ambiente' ou 'educação'):")

if termo:
    conn = conectar_banco()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # CONSULTA ULTRA-OTIMIZADA: NÃO SELECIONA OS TEXTOS LONGOS AQUI!
    # O index GIN roda apenas sobre os vetores de busca de forma instantânea.
    query_sql = """
        SELECT id_cadastro_geral_silegis, tipo_sigla, numero, ano, situacao, data_publicacao, ementa,
               ts_rank_cd(to_tsvector('portuguese', COALESCE(ementa, '') || ' ' || COALESCE(texto_consolidado, '') || ' ' || COALESCE(texto_original, '')), plainto_tsquery('portuguese', %s)) as relevanca
        FROM textos_normas
        WHERE to_tsvector('portuguese', COALESCE(ementa, '') || ' ' || COALESCE(texto_consolidado, '') || ' ' || COALESCE(texto_original, '')) 
              @@ plainto_tsquery('portuguese', %s)
        ORDER BY relevanca DESC
        LIMIT 50;
    """
    
    try:
        cursor.execute(query_sql, (termo, termo))
        resultados = cursor.fetchall()
        
        if not resultados:
            st.warning("Nenhum resultado encontrado.")
        else:
            st.success(f"{len(resultados)} resultados encontrados.")
            
            col_esquerda, col_direita = st.columns([2, 3])
            
            lista_normas = [f"{r['tipo_sigla'].upper()} {r['numero']}/{r['ano']}" for r in resultados]
            # Mapeamos apenas os metadados
            docs_metadados = {f"{r['tipo_sigla'].upper()} {r['numero']}/{r['ano']}": r for r in resultados}
            
            with col_esquerda:
                norma_selecionada = st.radio("Selecione uma norma:", options=lista_normas, label_visibility="collapsed")
            
            with col_direita:
                if norma_selecionada and norma_selecionada in docs_metadados:
                    meta = docs_metadados[norma_selecionada]
                    st.subheader(f"📄 {norma_selecionada}")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Situação", meta.get("situacao", "N/A"))
                    c2.metric("Publicação", meta.get("data_publicacao", "N/A"))
                    
                    st.markdown("---")
                    
                    # Mostra a ementa imediatamente (já veio na busca leve)
                    if meta.get("ementa"):
                        with st.expander("EMENTA", expanded=True):
                            st.text(meta["ementa"])
                    
                    # AGORA SIM: Busca os textos pesados sob demanda na nuvem!
                    with st.spinner("Carregando o restante do conteúdo da norma..."):
                        detalhes_pesados = buscar_texto_completo(meta["id_cadastro_geral_silegis"])
                    
                    if detalhes_pesados:
                        campos_longos = ["resumo", "indexacao", "observacao", "texto_consolidado", "texto_original"]
                        for campo in campos_longos:
                            if detalhes_pesados.get(campo):
                                with st.expander(campo.upper(), expanded=False):
                                    st.text(detalhes_pesados[campo])
                                    
    except Exception as e:
        st.error(f"Erro na busca: {e}")
