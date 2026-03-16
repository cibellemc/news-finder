import streamlit as st
import pandas as pd
import requests
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime, timedelta
from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from weasyprint import HTML

st.set_page_config(page_title="Extração de Notícias", page_icon=None, layout="wide")

# Custom CSS for a professional/premium look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        color: #fafafa;
    }
    .news-card {
        background-color: #1a1c24;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid #2d2e3a;
        transition: border-color 0.2s ease;
    }
    .news-card:hover {
        border-color: #4facfe;
    }
    .news-title {
        color: #4facfe;
        font-size: 1.1rem;
        font-weight: 500;
        text-decoration: none;
        margin-bottom: 6px;
        display: block;
    }
    .news-meta {
        color: #888;
        font-size: 0.85rem;
        display: flex;
        gap: 12px;
        margin-top: 8px;
    }
    .source-tag {
        background-color: #262730;
        color: #4facfe;
        padding: 1px 6px;
        border-radius: 3px;
        font-weight: 400;
        font-size: 0.8rem;
    }
    /* Hide top level padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navegação")
selection = st.sidebar.radio(
    "Ir para:",
    ["Busca por Termo", "Busca por Site"]
)

st.sidebar.divider()
st.sidebar.subheader("Configurações Globais")

num_news = st.sidebar.number_input("Notícias por fonte:", min_value=1, max_value=30, value=10, step=1)

time_option = st.sidebar.selectbox(
    "Período",
    ["Qualquer data", "Últimas 24 horas", "Última semana", "Último mês", "Período personalizado"]
)

start_date, end_date = None, None
if time_option == "Período personalizado":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Data inicial", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("Data final", datetime.now())

# Initialize session_state
if "noticias_termo" not in st.session_state:
    st.session_state.noticias_termo = None
if "noticias_site" not in st.session_state:
    st.session_state.noticias_site = None

def build_query(keyword, is_site=False, time_option="Qualquer data", start_date=None, end_date=None):
    query = keyword
    if is_site and not keyword.startswith("site:"):
        query = f"site:{keyword}"

    # Adiciona filtros de tempo à query
    if time_option == "Últimas 24 horas":
        query += " when:1d"
    elif time_option == "Última semana":
        query += " when:7d"
    elif time_option == "Último mês":
        query += " when:30d"
    elif time_option == "Período personalizado":
        if start_date:
            query += f" after:{start_date.strftime('%Y-%m-%d')}"
        if end_date:
            query += f" before:{end_date.strftime('%Y-%m-%d')}"
            
    return urllib.parse.quote(query)

def fetch_news_rss(keyword, is_site, num_news, time_option, start_date=None, end_date=None):
    encoded_query = build_query(keyword, is_site, time_option, start_date, end_date)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        
        results = []
        for item in root.findall('./channel/item'):
            if len(results) >= num_news:
                break
            
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            source = item.find('source').text if item.find('source') is not None else 'Fonte desconhecida'
            # description = item.find('description').text if item.find('description') is not None else ''
            
            # if description:
            #     description = html.unescape(description) # Converte &lt; para <, etc.
            #     description = re.sub(r'<[^>]+>', '', description).strip() # Remove as tags HTML

            date_str = pubDate
            try:
                dt = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %Z')
                date_str = dt.strftime('%d/%m/%Y %H:%M')
            except ValueError:
                pass
                
            results.append({
                'title': title,
                'link': link,
                'date': date_str,
                'media': source,
                # 'desc': description,
                'keyword': keyword,
                'is_site': is_site
            })
            
        return results
    except Exception as e:
        st.error(f"Erro ao buscar notícias para '{keyword}': {e}")
        return []

def display_results(df):
    if df is not None:
        st.subheader("Resultados encontrados")
        for keyword, group in df.groupby('keyword'):
            with st.expander(f"{keyword} ({len(group)} notícias)"):
                for _, row in group.iterrows():
                    link = row["link"].split("&ved=")[0]
                    st.markdown(f"""
                    <div class="news-card">
                        <a class="news-title" href="{link}" target="_blank">{row['title']}</a>
                        <div class="news-meta">
                            <span>Data: {row['date']}</span>
                            <span class="source-tag">Portal: {row['media']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Global download buttons for the current results
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            all_data = BytesIO()
            export_df = df.copy()
            export_df.rename(columns={
                "title": "Título",
                "media": "Fonte",
                "date": "Data",
                "link": "Link",
                "keyword": "Busca"
            }, inplace=True)
            export_df.to_excel(all_data, index=False, engine='openpyxl')
            all_data.seek(0)
            st.download_button("Baixar planilha XLSX", data=all_data, file_name=f"noticias_{datetime.now().strftime('%Y%m%d')}.xlsx", key=f"dl_xlsx_{selection}", use_container_width=True)
        
        with col_dl2:
            html_content = f"<html><body><h2>Relatório de Notícias - {datetime.now().strftime('%d/%m/%Y')}</h2>"
            for keyword, group in df.groupby('keyword'):
                html_content += f"<h3>Busca: {keyword}</h3>"
                for _, row in group.iterrows():
                    html_content += f"<p><b>{row['title']}</b><br>{row['date']} - {row['media']}<br><a href='{row['link']}'>{row['link']}</a></p><hr>"
            html_content += "</body></html>"
            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(pdf_file)
            pdf_file.seek(0)
            st.download_button("Baixar relatório PDF", data=pdf_file, file_name=f"noticias_{datetime.now().strftime('%Y%m%d')}.pdf", key=f"dl_pdf_{selection}", use_container_width=True)

# Page logic
if selection == "Busca por Termo":
    st.title("Extração de Notícias")
    st.header("Busca por Termo")
    
    # st.info("Insira palavras-chave, nomes de pessoas ou temas de interesse separados por vírgula (ex: jucepi, Alzenir Porto, Gov.Pi empresas, empreendedorismo). O sistema buscará as notícias mais relevantes relacionadas a esses termos em diversos portais de notícias.")
    
    PALAVRAS_CHAVE_PADRAO = ["jucepi", "Alzenir Porto", "Gov.Pi empresas", "empreendedorismo"]
    keywords_input = st.text_area("Insira palavras-chave, nomes de pessoas ou temas de interesse separados por vírgula (ex: jucepi, Alzenir Porto, Gov.Pi empresas, empreendedorismo).", ",".join(PALAVRAS_CHAVE_PADRAO), height=100)
    
    if st.button("Buscar por Termo", use_container_width=True):
        keywords = [p.strip() for p in keywords_input.split(",") if p.strip()]
        all_results = []
        if keywords:
            progress_bar = st.progress(0)
            for i, keyword in enumerate(keywords):
                res = fetch_news_rss(keyword, False, num_news, time_option, start_date, end_date)
                all_results.extend(res)
                progress_bar.progress((i + 1) / len(keywords))
            progress_bar.empty()
            st.session_state.noticias_termo = pd.DataFrame(all_results)
        else:
            st.warning("Por favor, insira pelo menos um termo de busca.")
    
    display_results(st.session_state.noticias_termo)

elif selection == "Busca por Site":
    st.title("Extração de Notícias")
    st.header("Busca por Site")
    
    # st.info("Insira os domínios dos sites onde deseja concentrar sua busca separados por vírgula (ex: pi.gov.br, g1.globo.com). O sistema filtrará os resultados para mostrar apenas as matérias publicadas nos portais informados.")
    
    SITES_PADRAO = ["pi.gov.br", "g1.globo.com"]
    sites_input = st.text_area("Insira os domínios dos sites onde deseja concentrar sua busca separados por vírgula (ex: pi.gov.br, g1.globo.com).", ",".join(SITES_PADRAO), height=100)
    
    if st.button("Buscar por Site", use_container_width=True):
        sites = [p.strip() for p in sites_input.split(",") if p.strip()]
        all_results = []
        if sites:
            progress_bar = st.progress(0)
            for i, site in enumerate(sites):
                res = fetch_news_rss(site, True, num_news, time_option, start_date, end_date)
                all_results.extend(res)
                progress_bar.progress((i + 1) / len(sites))
            progress_bar.empty()
            st.session_state.noticias_site = pd.DataFrame(all_results)
        else:
            st.warning("Por favor, insira pelo menos um domínio de site.")
    
    display_results(st.session_state.noticias_site)
