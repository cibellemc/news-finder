import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime, timedelta

st.title("📰 Extração de Notícias")

# Sidebar for time period selection
st.sidebar.header("⏱️ Período de Busca")
time_option = st.sidebar.radio(
    "Selecione o período:",
    ["Últimas 24 horas", "Última semana", "Último mês", "Período personalizado"],
    index=0
)

# Handle custom date range
if time_option == "Período personalizado":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Data inicial", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("Data final", datetime.now())
    
# Lista de palavras-chave padrão
PALAVRAS_CHAVE_PADRAO = [
    "transformação digital"
]

# Form for keyword input
with st.form("search_form"):
    palavras_chave_input = st.text_area(
        "Digite palavras-chave (separe por vírgula):",
        ",".join(PALAVRAS_CHAVE_PADRAO)
    )
    submit_button = st.form_submit_button('Buscar notícias')

if submit_button:
    # Convert input to list
    keywords = [palavra.strip() for palavra in palavras_chave_input.split(",") if palavra.strip()]
    
    # Create DataFrame to store all results
    all_results = []
    
    # Progress bar
    progress_text = "Buscando notícias..."
    progress_bar = st.progress(0)
    
    # Configure GoogleNews based on time period
    for i, keyword in enumerate(keywords):
        googlenews = GoogleNews(lang='pt-BR')
        
        # Set time period based on selection
        if time_option == "Últimas 24 horas":
            googlenews.set_period('1d')
        elif time_option == "Última semana":
            googlenews.set_period('7d')
        elif time_option == "Último mês":
            googlenews.set_period('1m')
        elif time_option == "Período personalizado":
            googlenews.set_time_range(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'))
        
        # Search for news
        googlenews.search(keyword)
        results = googlenews.result()
        
        if results:
            # Add keyword column to results
            for result in results:
                result['keyword'] = keyword
            all_results.extend(results)
        
        googlenews.clear()
        
        # Update progress bar
        progress_bar.progress((i + 1) / len(keywords))

    # Remove progress bar after completion
    progress_bar.empty()
    
    if all_results:
        df = pd.DataFrame(all_results)
        
        # Tabela responsiva
        st.markdown("### 📊 Resumo das Buscas")
        
        # Versão mobile-friendly da tabela de resumo
        for _, row in df.groupby('keyword').size().reset_index().iterrows():
            keyword = row['keyword']
            count = row[0]
            
            # Container para cada linha
            with st.container():
                # Usar colunas com proporções ajustadas para mobile
                cols = st.columns([2, 1])
                
                with cols[0]:
                    st.markdown(f"**{keyword}** ({count} notícias)")
                
                with cols[1]:
                    keyword_data = df[df['keyword'] == keyword].to_csv(
                        index=False,
                        encoding='utf-8-sig'
                    ).encode('utf-8-sig')
                    
                    st.download_button(
                        label="📥 Baixar",
                        data=keyword_data,
                        file_name=f"noticias_{keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                st.markdown("---")
        
        # Botão para baixar todas as notícias
        all_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Baixar todas as notícias",
            data=all_data,
            file_name=f"todas_noticias_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Exibição das notícias em formato mobile-friendly
        st.markdown("### 📰 Detalhes das Notícias")
        
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
                    else:
                        st.info("Notícia sem dados completos")
    else:
        st.warning("Nenhuma notícia encontrada para os termos pesquisados.")