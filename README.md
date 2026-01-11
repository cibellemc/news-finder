# 📰 Extração de Notícias com Streamlit

Este projeto é uma aplicação web interativa desenvolvida em Python para busca, monitorização e exportação de notícias em tempo real. Utiliza a biblioteca Google News para recolha de dados e permite a exportação dos resultados em formatos profissionais (Excel e PDF).

## 🚀 Funcionalidades

* Busca por Múltiplas Palavras-Chave: Insira vários termos separados por vírgula para uma pesquisa abrangente.

* Configuração de Quantidade: Controle o número de notícias recolhidas por palavra-chave através de um slider lateral.

* Interface Mobile-Friendly: Visualização organizada em cartões expansíveis (expanders), ideal para leitura em dispositivos móveis.

* Exportação de Dados:

    * Excel (XLSX): Planilha completa com títulos, fontes, datas, descrições e links.

    * Relatório PDF: Documento formatado com estilos CSS, gerado automaticamente a partir das notícias encontradas.

## 🛠️ Tecnologias Utilizadas

* Streamlit: Interface do utilizador.

* Pandas: Processamento de dados.

* GoogleNews: API de recolha de notícias.

* WeasyPrint: Motor de renderização de PDF (HTML para PDF).

* Openpyxl: Geração de ficheiros Excel.

## 📋 Pré-requisitos e Instalação

1. Instalar dependências Python

Crie um ambiente virtual e instale as bibliotecas necessárias:

```
# linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Dependências do Sistema (CRÍTICO)

A biblioteca WeasyPrint requer bibliotecas externas do sistema operativo para renderizar fontes e gráficos (Pango/Cairo).

Se estiver em Linux local (Debian/Ubuntu):

```
sudo apt-get install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

## 🖥️ Como Executar

No terminal, navegue até à pasta do projeto.

Execute o comando:
```
streamlit run App.py
```

A aplicação abrirá automaticamente no seu navegador.

## 📄 Estrutura do Relatório PDF

O PDF gerado inclui:

* Estilização personalizada via CSS.

* Organização por palavra-chave.

* Links clicáveis para as fontes originais.

* Descrição resumida da notícia.

Desenvolvido para facilitar o fluxo de monitorização de notícias e clipping digital.