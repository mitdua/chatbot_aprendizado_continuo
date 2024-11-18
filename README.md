# 🤖 Chatbot de Aprendizado Contínuo

![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40.1-brightgreen.svg)

## 📄 Descrição

Este projeto implementa um **Chatbot de Aprendizado Contínuo** utilizando a arquitetura **GPT-4** da OpenAI. O chatbot é projetado para:

- **Verificar a precisão das informações** fornecidas pelo usuário.
- **Armazenar informações verificadas** para referências futuras.
- **Recuperar informações relevantes** com base em consultas temáticas.
- **Interface de usuário intuitiva** através do Streamlit para uma interação fluida.

O sistema utiliza **Elasticsearch** para armazenamento eficiente de dados e **sentence-transformers** para a geração de embeddings semânticos. Além disso, integra-se com **LangChain** e **LangGraph** para a gestão avançada de fluxos de trabalho de IA.

## 🛠️ Características

- **Verificação de Informação**: Valida a exatidão das informações fornecidas sobre um tópico específico.
- **Armazenamento de Informação**: Salva informações verificadas em um índice do Elasticsearch para referências futuras.
- **Recuperação de Informação**: Recupera informações relevantes com base em consultas temáticas utilizando similaridade coseno.
- **Interface de Chat Intuitiva**: Interage com os usuários através de uma interface web criada com Streamlit.
- **Integração com LangChain e LangGraph**: Utiliza ferramentas avançadas para a execução de fluxos de trabalho e gestão de ferramentas.

## 🚀 Tecnologias Utilizadas

- **Python 3.12+**: Linguagem de programação principal.
- **OpenAI GPT-4**: Modelo de linguagem para gerar respostas inteligentes.
- **Elasticsearch**: Motor de busca e análise para armazenamento e recuperação de informações.
- **Sentence-Transformers**: Biblioteca para a geração de embeddings semânticos.
- **LangChain e LangGraph**: Frameworks para criação e gestão de fluxos de trabalho de IA.
- **Streamlit**: Biblioteca para construir interfaces de usuário web interativas.


## 🛠️ Instalação

### 📋 Pré-requisitos

- **Python 3.12+**
- **Elasticsearch**: Certifique-se de ter uma instância do Elasticsearch em funcionamento.
- **Docker** (opcional): Para facilitar a configuração do Elasticsearch.

### 📦 Passos de Instalação


#### Usando o arquivo Docker Compose (recomendado)
1. **Clone o repositório**

    ```bash
    git clone https://github.com/mitdua/chatbot_aprendizado_continuo.git
    cd chatbot_aprendizado_continuo
    ```

2. **Configure as variáveis de ambiente**

    Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

    ```env
    OPENAI_API_KEY=sua_chave_api_da_openai
    ELASTICSEARCH_HOST=elasticsearch 
    ```

3. **Inicie o ambiente com Docker Compose**
    ```bash
    docker compose up --build
    ```

#### Construindo passo a passo

1. **Clone o repositório**

    ```bash
    git clone https://github.com/mitdua/chatbot_aprendizado_continuo.git
    cd chatbot_aprendizado_continuo
    ```

2. **Crie um ambiente virtual**

    ```bash
    python3.12 -m venv venv
    source venv/bin/activate
    ```

3. **Instale as dependências**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure as variáveis de ambiente**

    Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:

    ```env
    OPENAI_API_KEY=sua_chave_api_da_openai
    ELASTICSEARCH_HOST=localhost
    ```

5. **Configure o Elasticsearch**

    Você pode configurar o Elasticsearch localmente ou utilizando Docker.   

    Certifique-se de ter o Docker instalado e execute o seguinte comando:

    ```bash
    docker run -d \
    --name elasticsearch \
    -e discovery.type=single-node \
    -e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
    -e xpack.security.enabled=false \
    -p 9200:9200 \
    -v esdata:/usr/share/elasticsearch/data \
    docker.elastic.co/elasticsearch/elasticsearch:8.16.0

    ```
6. **Execute a Aplicação Streamlit**
    ```bash
        streamlit run app.py
    ```

## 🎮 Uso
### Interaja com o Chatbot

1. Abra seu navegador e navegue para [http://localhost:8501](http://localhost:8501).
2. Escreva suas mensagens no campo de entrada e observe as respostas do chatbot em tempo real.

### 📈 Fluxo de Trabalho do Chatbot

1. **Entrada do Usuário**: O usuário envia uma mensagem através da interface do Streamlit.
2. **Verificação de Informação**: O chatbot verifica a precisão da informação fornecida utilizando o modelo GPT-4.
3. **Armazenamento de Informação**: Se a informação for válida, ela é armazenada no Elasticsearch para futuras referências.
4. **Recuperação de Informação**: Quando solicitado, o chatbot recupera informações relevantes com base em consultas temáticas.
5. **Resposta ao Usuário**: O chatbot responde ao usuário com as informações verificadas e/ou recuperadas.



