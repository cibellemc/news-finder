import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime, timedelta
from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from weasyprint import HTML


st.title("📰 Extração de Notícias")

# Sidebar para escolha da quantidade de notícias
st.sidebar.header("⚙️ Configurações de Busca")
num_news = st.sidebar.slider("Quantidade de notícias por palavra-chave:", min_value=10, max_value=50, value=10, step=10)

# if time_option == "Período personalizado":
#     col1, col2 = st.sidebar.columns(2)
#     with col1:
#         start_date = st.date_input("Data inicial", datetime.now() - timedelta(days=7))
#     with col2:
#         end_date = st.date_input("Data final", datetime.now())
    
PALAVRAS_CHAVE_PADRAO = [
    # "jucepi", "Alzenir Porto", "Gov.Pi empresas", "empreendedorismo" 
    # "consulta prévia", "contrato social", "consulta de viabilidade", 
    # "certidões", "livros", "balanço", "alterações", "baixa", "abertura", 
    # "startup", "leiloeiro público", "autenticação de livros", "transformação digital"
    "inteligência artificial", "chatgpt", "openai", "modelos de linguagem", "aprendizado de máquina"
]
# Inicializa session_state
if "noticias" not in st.session_state:
    st.session_state.noticias = None

with st.form("search_form"):
    palavras_chave_input = st.text_area(
        "Digite palavras-chave (separe por vírgula):",
        ",".join(PALAVRAS_CHAVE_PADRAO)
    )
    submit_button = st.form_submit_button('Buscar notícias')

if submit_button:
    keywords = [palavra.strip() for palavra in palavras_chave_input.split(",") if palavra.strip()]
    all_results = []
    progress_bar = st.progress(0)

    for i, keyword in enumerate(keywords):
        googlenews = GoogleNews(lang='pt-BR')
        
        # if time_option == "Últimas 24 horas":
        #     googlenews.set_period('1d')
        # elif time_option == "Última semana":
        #     googlenews.set_period('7d')
        # elif time_option == "Último mês":
        #     googlenews.set_period('1m')
        # elif time_option == "Período personalizado":
        #     googlenews.set_time_range(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'))
        
        googlenews.search(keyword)

        total_results = 0
        page = 1

        while total_results < num_news:
            results = googlenews.page_at(page)
            if not results:
                break
            for result in results:
                result['keyword'] = keyword
            all_results.extend(results)
            total_results += len(results)
            page += 1
            
        googlenews.clear()
        progress_bar.progress((i + 1) / len(keywords))
    
        progress_bar.empty()

    if all_results:
        df = pd.DataFrame(all_results)
        st.session_state.noticias = df

    
if st.session_state.noticias is not None:
        df = st.session_state.noticias

        # Exibição das notícias em formato mobile-friendly
        st.markdown("###  Detalhes das Notícias")
        
        for keyword, group in df.groupby('keyword'):
            with st.expander(f"📌 {keyword} ({len(group)} notícias)"):
                for _, row in group.iterrows():
                    if row.get("title") and row.get("link"):
                        link = row["link"].split("&ved=")[0]
                        
                        # Container para cada notícia
                        with st.container():
                            st.markdown(f"#### [{row['title']}]({link})")
                            
                            date_str = row.get('date', 'Data não disponível')
                            media_str = row.get('media', 'Fonte desconhecida')
                            st.markdown(f"*{date_str} - {media_str}*")
                            
                            if row.get('desc'):
                                if isinstance(row['desc'], str) and row['desc'].strip():
                                    st.markdown(row['desc'])
                            
                            st.markdown("---")
        
        all_data = BytesIO()
        df.drop(columns=["datetime", "img"], inplace=True, errors="ignore")
        df.rename(columns={
    "title": "Título",
    "media": "Fonte",
    "date": "Data",
    "desc": "Descrição",
    "link": "Link",
}, inplace=True)

        df.to_excel(all_data, index=False, engine='openpyxl')
        all_data.seek(0)
        
        st.download_button(
            label="📥 Baixar todas as notícias (XLSX)",
            data=all_data,
            file_name=f"todas_noticias_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # Gerar HTML
        html_content = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h2, h3 { color: #333; }
                div.news-item { margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
                a { font-weight: bold; color: #007BFF; text-decoration: none; }
                a:hover { text-decoration: underline; }
                p { margin: 5px 0; }
            </style>
        </head>
        <body>
        <h2>Detalhes das Notícias</h2>
        """
        for keyword, group in df.groupby('keyword'):
            html_content += f"<h3>{keyword} ({len(group)} notícias)</h3>"
            for _, row in group.iterrows():
                link = row.get("Link", "#").split("&ved=")[0]
                title = row.get("Título", "Sem título")
                date_str = row.get("Data", "Data não disponível")
                media_str = row.get("Fonte", "Fonte desconhecida")
                desc = row.get("Descrição", "Sem descrição")
                html_content += f"""
                    <div class='news-item'>
                        <a href='{link}' target='_blank'>{title}</a>
                        <p>Descrição: {desc}</p>
                        <p>Fonte: {media_str} - {date_str}</p>
                    </div>
                """
            html_content += "<br>"
        html_content += "</body></html>"
        
        # Converter HTML para PDF
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        
        st.download_button(
            label="📥 Baixar detalhes das notícias (PDF)",
            data=pdf_file,
            file_name=f"noticias_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
