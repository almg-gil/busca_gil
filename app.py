import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Silegis - Busca de Normas", layout="wide")

# Conectar ao Supabase (O Streamlit pegará as credenciais de forma segura)
@st.cache_resource
def conectar_banco():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        port=st.secrets["DB_PORT"],
        sslmode="require"  # <- Esta linha é vital para a Direct Connection
    )

st.title("🏛️ Silegis - Busca de Normas (Supabase + Streamlit)")

termo = st.text_input("Digite o termo de busca (Ex: 'meio ambiente' ou 'educação'):")

if termo:
    conn = conectar_banco()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Consulta SQL usando o Full-Text Search nativo em português do Postgres
    query_sql = """
        SELECT *, 
               ts_rank_cd(to_tsvector('portuguese', COALESCE(ementa, '') || ' ' || COALESCE(texto_consolidado, '') || ' ' || COALESCE(texto_original, '')), query) as relevanca
        FROM textos_normas, to_tsquery('portuguese', %s) query
        WHERE to_tsvector('portuguese', COALESCE(ementa, '') || ' ' || COALESCE(texto_consolidado, '') || ' ' || COALESCE(texto_original, '')) @@ query
        ORDER BY relevanca DESC
        LIMIT 50;
    """
    
    try:
        # Formata o termo para o padrão do Postgres (troca espaços por & para agir como AND)
        termo_formatado = " & ".join(termo.split())
        cursor.execute(query_sql, (termo_formatado,))
        resultados = cursor.fetchall()
        
        if not resultados:
            st.warning("Nenhum resultado encontrado.")
        else:
            st.success(f"{len(resultados)} resultados encontrados.")
            
            col_esquerda, col_direita = st.columns([2, 3])
            lista_normas = [f"{r['tipo_sigla'].upper()} {r['numero']}/{r['ano']}" for r in resultados]
            docs_completos = {f"{r['tipo_sigla'].upper()} {r['numero']}/{r['ano']}": r for r in resultados}
            
            with col_esquerda:
                norma_selecionada = st.radio("Selecione uma norma:", options=lista_normas, label_visibility="collapsed")
            
            with col_direita:
                if norma_selecionada and norma_selecionada in docs_completos:
                    doc = docs_completos[norma_selecionada]
                    st.subheader(f"📄 {norma_selecionada}")
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Situação", doc.get("situacao", "N/A"))
                    c2.metric("Publicação", doc.get("data_publicacao", "N/A"))
                    
                    st.markdown("---")
                    campos_longos = ["ementa", "resumo", "indexacao", "observacao", "texto_consolidado", "texto_original"]
                    for campo in campos_longos:
                        if doc.get(campo):
                            with st.expander(campo.upper(), expanded=(campo in ["ementa"])):
                                st.text(doc[campo])
    except Exception as e:
        st.error(f"Erro na busca: {e}")
