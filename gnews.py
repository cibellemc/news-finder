import time
from GoogleNews import GoogleNews
import pandas as pd

# Inicializa o pacote GoogleNews
googlenews = GoogleNews()

# Lista de palavras-chave
palavras_chave = ["", ""]

# Lista para armazenar os dados coletados
dados = []

# Pesquisa para cada palavra-chave
for palavra in palavras_chave:
    googlenews.search(palavra)
    resultado = googlenews.result()
    
    # Extrai os dados relevantes para cada notícia
    for noticia in resultado:
        titulo = noticia['title']
        link = noticia['link'].split("&ved=")[0]  # Remove parâmetros indesejados
        data = noticia['date']
        veiculo = noticia['media']
        
        # Adiciona os dados à lista
        dados.append([palavra, titulo, link, data, veiculo])

    # Aguarda 5 segundos antes de realizar a próxima requisição
    time.sleep(5)

# Cria um DataFrame com os dados
df = pd.DataFrame(dados, columns=['Palavra-chave', 'Título', 'Link', 'Data', 'Veículo'])

# Exibe o DataFrame
# print(df)

# Salva o DataFrame em um arquivo CSV
df.to_csv("minhas_noticias.csv", index=False, encoding='utf-8')
