import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime, timedelta
from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from weasyprint import HTML


st.title("📰 Extração de Notícias")

# Sidebar for time period selection
st.sidebar.header("⏱️ Período de Busca")
time_option = st.sidebar.radio(
    "Selecione o período:",
    ["Últimas 24 horas", "Última semana", "Último mês", "Período personalizado"],
    index=0
)

if time_option == "Período personalizado":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Data inicial", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("Data final", datetime.now())
    
PALAVRAS_CHAVE_PADRAO = [
"transformação digital"
]

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
        
        if time_option == "Últimas 24 horas":
            googlenews.set_period('1d')
        elif time_option == "Última semana":
            googlenews.set_period('7d')
        elif time_option == "Último mês":
            googlenews.set_period('1m')
        elif time_option == "Período personalizado":
            googlenews.set_time_range(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'))
        
        googlenews.search(keyword)
        results = googlenews.result()
        
        if results:
            for result in results:
                result['keyword'] = keyword
            all_results.extend(results)
        
        googlenews.clear()
        progress_bar.progress((i + 1) / len(keywords))
    
    progress_bar.empty()
    
    if all_results:
        df = pd.DataFrame(all_results)
        st.markdown("### 📊 Resumo das Buscas")
        
        for _, row in df.groupby('keyword').size().reset_index().iterrows():
            keyword = row['keyword']
            count = row[0]
            
            with st.container():
                cols = st.columns([2, 1])
                with cols[0]:
                    st.markdown(f"**{keyword}**")
                    # st.markdown(f"**{keyword}** ({count} notícias)")
                with cols[1]:
                    keyword_data = BytesIO()
                    df[df['keyword'] == keyword].to_excel(keyword_data, index=False, engine='openpyxl')
                    keyword_data.seek(0)
                    
                    st.download_button(
                        label="📥 Baixar XLSX",
                        data=keyword_data,
                        file_name=f"noticias_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                st.markdown("---")
        
        all_data = BytesIO()
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
                link = row.get("link", "#").split("&ved=")[0]
                title = row.get("title", "Sem título")
                date_str = row.get("date", "Data não disponível")
                media_str = row.get("media", "Fonte desconhecida")
                desc = row.get("desc", "Sem descrição")
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
        
        
        # st.markdown("### 📰 Detalhes das Notícias")
        # st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.warning("Nenhuma notícia encontrada para os termos pesquisados.")
