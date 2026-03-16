# News Extractor Intelligence 📰🚀

Uma ferramenta avançada de monitoramento e extração de notícias em tempo real, construída com **Streamlit** e integrada ao **Google News RSS**. Projetada para profissionais que precisam de insights rápidos e relatórios automatizados.

## ✨ Funcionalidades

- **Busca por Termos**: Monitore palavras-chave específicas simultaneamente (separadas por vírgula).
- **Busca por Site**: Monitore domínios específicos (ex: `g1.globo.com`, `uol.com.br`) para capturar as últimas atualizações de portais de interesse.
- **Configurações Flexíveis**: Filtre resultados por período (Últimas 24h, 7 dias, mês ou personalizado) e limite a quantidade de notícias por fonte.
- **Design Premium**: Interface moderna com layout hero, navegação em "pill" na sidebar e total suporte aos temas **Light** e **Dark** do Streamlit.
- **Exportação Inteligente**:
  - **XLSX**: Planilha limpa e organizada para análise de dados.
  - **PDF**: Relatórios profissionais estruturados, prontos para apresentação.

## 🛠️ Tecnologias

- **Linguagem**: Python 3.9+
- **Frontend**: Streamlit
- **Processamento de Dados**: Pandas, OpenPyXL
- **Geração de PDF**: WeasyPrint
- **Consumo de Dados**: Google News RSS Feed (XML Parsing)

## 🚀 Como Executar

### Pré-requisitos
- Python instalado
- Dependências de sistema para o WeasyPrint (libpangocairo, etc.)

### Instalação Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/cibellemc/news-finder.git
   cd news-finder
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   streamlit run App.py
   ```

---

### 🐳 Executando com Docker

Se preferir utilizar Docker, o projeto já conta com uma configuração pronta para produção.

1. Construa a imagem:
   ```bash
   docker build -t news-finder .
   ```

2. Inicie o container:
   ```bash
   docker run -p 8507:8507 news-finder
   ```

A aplicação estará disponível em `http://localhost:8507`.

## 📂 Estrutura do Projeto

- `App.py`: Arquivo principal da aplicação contendo a lógica de busca e UI.
- `requirements.txt`: Lista de dependências Python.
- `Dockerfile`: Configuração para containerização.
- `.streamlit/`: Configurações de tema e servidor do Streamlit.

---
Desenvolvido por **Cibelle Cavalcante**