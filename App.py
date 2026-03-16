import streamlit as st
import pandas as pd
import requests
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime, timedelta
from io import BytesIO
from weasyprint import HTML

st.set_page_config(page_title="Extração de Notícias", page_icon=None, layout="wide")

# Custom CSS for Professional Layout (Theme Agnostic)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Global Styles */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.1);
        width: 280px !important;
    }
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.25rem;
        font-weight: 700;
        color: #4facfe;
        margin-bottom: 30px;
        padding-top: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: grey;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 15px 0 8px 0;
        opacity: 0.7;
    }
    [data-testid="stSidebarNav"] { display: none; }
    
    /* Content Components */
    .search-container {
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 25px;
        background-color: rgba(128, 128, 128, 0.05);
    }
    .search-type-header {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #4facfe;
        font-weight: 600;
        margin-bottom: 24px;
        font-size: 0.95rem;
        text-transform: uppercase;
    }
    
    .news-card {
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        position: relative;
    }
    .card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .portal-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: rgba(79, 172, 254, 0.1);
        color: #4facfe;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .publication-date { font-size: 0.72rem; opacity: 0.7; font-weight: 500; }
    .news-card-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 10px; line-height: 1.4; color: inherit; }
    .card-footer { display: flex; gap: 20px; border-top: 1px solid rgba(128, 128, 128, 0.1); padding-top: 12px; }
    .card-action { color: #4facfe; text-decoration: none; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.3px; display: flex; align-items: center; gap: 7px; text-transform: uppercase; }
    
    .results-section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    .results-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: inherit;
    }
    
    .stats-label {
        font-size: 0.8rem;
        color: grey;
        font-weight: 500;
        opacity: 0.8;
    }
    
    .copyright-footer {
        text-align: center; color: grey; font-size: 0.72rem;
        margin: 60px 0 40px 0; letter-spacing: 1.5px; font-weight: 600; opacity: 0.6;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Logic ---
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Extração de Notícias</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section-title">Navegação</div>', unsafe_allow_html=True)
    nav_selection = st.radio(
        "Menu",
        ["Busca por Termo", "Busca por Site"],
        label_visibility="collapsed",
        key="nav_radio"
    )
    selection = nav_selection
    
    st.markdown('<div class="sidebar-section-title">Configurações Globais</div>', unsafe_allow_html=True)
    time_option = st.selectbox(
        "Período",
        ["Qualquer data", "Últimos 7 dias", "Últimas 24 horas", "Último mês", "Período personalizado"],
        index=1
    )
    
    start_date, end_date = None, None
    if time_option == "Período personalizado":
        start_date = st.date_input("Início", datetime.now() - timedelta(days=7))
        end_date = st.date_input("Fim", datetime.now())
    
    num_news = st.number_input("Notícias por fonte", min_value=1, max_value=30, value=10)

# --- Logic Setup ---
if "noticias_termo" not in st.session_state: st.session_state.noticias_termo = None
if "noticias_site" not in st.session_state: st.session_state.noticias_site = None

def build_query(keyword, is_site=False, time_option="Qualquer data", start_date=None, end_date=None):
    query = keyword
    if is_site and not keyword.startswith("site:"): query = f"site:{keyword}"
    if time_option == "Últimas 24 horas": query += " when:1d"
    elif time_option in ["Últimos 7 dias", "Última semana"]: query += " when:7d"
    elif time_option == "Último mês": query += " when:30d"
    elif time_option == "Período personalizado" and start_date:
        query += f" after:{start_date.strftime('%Y-%m-%d')}"
        if end_date: query += f" before:{end_date.strftime('%Y-%m-%d')}"
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
            if len(results) >= num_news: break
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            source = item.find('source').text if item.find('source') is not None else 'Fonte desconhecida'
            description = item.find('description').text if item.find('description') is not None else ''
            
            if description:
                description = html.unescape(description)
                description = re.sub(r'<[^>]+>', '', description).strip()
                if len(description) > 200: description = description[:197] + "..."

            date_str = pubDate
            try:
                dt = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %Z')
                date_str = dt.strftime('%d/%m/%Y %H:%M')
            except ValueError: pass
                
            results.append({
                'title': title, 'link': link, 'date': date_str, 'media': source, 'desc': description, 'keyword': keyword, 'is_site': is_site
            })
        return results
    except Exception as e:
        st.error(f"Erro: {e}")
        return []

def display_dashboard(df):
    if df is not None and not df.empty:
        total = len(df)
        sources = df['keyword'].nunique()
        st.markdown(f"""
            <div class="results-section-header">
                <div class="results-title">Resultados encontrados</div>
                <div class="stats-label">Mostrando {total} resultados de {sources} fontes</div>
            </div>
            """, unsafe_allow_html=True)

        for keyword, group in df.groupby('keyword'):
            with st.expander(f"{keyword} ({len(group)} notícias)"):
                for _, row in group.iterrows():
                    link = row["link"].split("&ved=")[0]
                    st.markdown(f"""
                        <div class="news-card">
                            <div class="card-top">
                                <div class="publication-date">DATA: {row['date']}</div>
                                <div class="portal-badge">FONTE: {row['media']}</div>
                            </div>
                            <div class="news-card-title">{row['title']}</div>
                            <div class="card-footer">
                                <a href="{link}" target="_blank" class="card-action">VER ÍNTEGRA</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Download Section
        col1, col2 = st.columns(2)
        with col1:
            all_data = BytesIO()
            # Drop desc and is_site columns as requested
            export_df = df.drop(columns=['desc', 'is_site'], errors='ignore')
            export_df.rename(columns={"title":"Título","media":"Fonte","date":"Data","link":"Link","keyword":"Busca"}, inplace=False).to_excel(all_data, index=False, engine='openpyxl')
            all_data.seek(0)
            st.download_button("Baixar planilha XLSX", data=all_data, file_name="relatorio_noticias.xlsx", key=f"dl_xlsx_{selection}", use_container_width=True)
        with col2:
            try:
                html_report = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; padding: 40px; color: #333; }}
                        .header {{ border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 30px; }}
                        h1 {{ color: #007bff; font-size: 24px; margin: 0; }}
                        .date {{ font-size: 12px; color: #666; }}
                        .keyword-block {{ margin-bottom: 40px; }}
                        .keyword-title {{ font-size: 18px; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 15px; color: #000; }}
                        .news-card {{ margin-bottom: 20px; }}
                        .news-title {{ font-size: 14px; font-weight: bold; color: #000; margin-bottom: 4px; }}
                        .news-meta {{ font-size: 10px; color: #666; margin-bottom: 8px; }}
                        .news-link {{ font-size: 10px; color: #007bff; text-decoration: none; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>RELATÓRIO DE NOTÍCIAS</h1>
                        <div class="date">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
                    </div>
                """
                for kw, group in df.groupby('keyword'):
                    html_report += f"<div class='keyword-block'><div class='keyword-title'>BUSCA: {kw.upper()}</div>"
                    for _, row in group.iterrows():
                        html_report += f"""
                        <div class='news-card'>
                            <div class='news-title'>{row['title']}</div>
                            <div class='news-meta'>PORTAL: {row['media']} | DATA: {row['date']}</div>
                            <div class='news-link'>{row['link']}</div>
                        </div>
                        """
                    html_report += "</div>"
                html_report += "</body></html>"
                
                pdf_bytes = BytesIO()
                HTML(string=html_report).write_pdf(pdf_bytes)
                pdf_bytes.seek(0)
                st.download_button("Exportar Relatório PDF", data=pdf_bytes, file_name="relatorio_noticias.pdf", key=f"dl_pdf_{selection}", use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")

# --- Search Area ---
if selection == "Busca por Termo":
    # st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<div class="search-type-header">Busca por Termo</div>', unsafe_allow_html=True)
    
    col_input, col_submit = st.columns([6, 1])
    with col_input:
        default_val = "jucepi, Alzenir Porto, Gov.Pi empresas, empreendedorismo"
        query_val = st.text_input("Busca", value=default_val, label_visibility="collapsed")
    with col_submit:
        exec_search = st.button("PESQUISAR", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if exec_search:
        keys = [p.strip() for p in query_val.split(",") if p.strip()]
        outputs = []
        if keys:
            pb = st.progress(0)
            for i, k in enumerate(keys):
                outputs.extend(fetch_news_rss(k, False, num_news, time_option, start_date, end_date))
                pb.progress((i+1)/len(keys))
            pb.empty()
            st.session_state.noticias_termo = pd.DataFrame(outputs)
    
    display_dashboard(st.session_state.noticias_termo)

elif selection == "Busca por Site":
    # st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<div class="search-type-header">Busca por Site</div>', unsafe_allow_html=True)
    
    col_input, col_submit = st.columns([6, 1])
    with col_input:
        default_sites = "pi.gov.br, g1.globo.com"
        sites_val = st.text_input("Domínios", value=default_sites, label_visibility="collapsed")
    with col_submit:
        exec_search_site = st.button("PESQUISAR", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if exec_search_site:
        keys = [p.strip() for p in sites_val.split(",") if p.strip()]
        outputs = []
        if keys:
            pb = st.progress(0)
            for i, k in enumerate(keys):
                outputs.extend(fetch_news_rss(k, True, num_news, time_option, start_date, end_date))
                pb.progress((i+1)/len(keys))
            pb.empty()
            st.session_state.noticias_site = pd.DataFrame(outputs)
            
    display_dashboard(st.session_state.noticias_site)

# st.markdown('<div class="copyright-footer">NEWS EXTRACTOR INTELLIGENCE © 2025</div>', unsafe_allow_html=True)
