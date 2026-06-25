---

# MPA - Market Prices Analysis

O projeto "Market Prices Analysis" (MPA) foi criado para combater a assimetria de informações e a desinformação de preços no varejo local. O objetivo da ferramenta é oferecer transparência e autonomia ao consumidor na hora de realizar compras. O sistema automatiza a extração de dados brutos a partir de vídeos gravados das prateleiras dos supermercados. A captura ocorre por meio de uma varredura contínua de vídeo, o que transfere todo o esforço de coleta do usuário para o algoritmo. Essas informações são estruturadas e consolidadas em um dashboard interativo, permitindo a comparação ágil de valores.

## Arquitetura do Sistema

O MPA opera sob uma arquitetura cliente-servidor assíncrona, dividida em módulos independentes que se comunicam entre si:

### 1. Módulo Extrator (Processamento Local)

* Este módulo é responsável pelo processamento local das imagens capturadas.


* O script `extrator_precos.py` segmenta o vídeo contínuo aplicando uma taxa de amostragem temporal entre 0,2 e 0,5 segundos por frame para evitar a sobrecarga da CPU.


* A ferramenta utiliza OpenCV para realizar operações de pré-processamento, como redimensionamento bilinear suave, conversão para escala de cinza e aplicação de equalização de contraste adaptativo (CLAHE).


* A extração dos textos brutos nas imagens pré-processadas é feita pelo motor EasyOCR, operando totalmente offline para reduzir o consumo de banda e a latência.



### 2. Módulo Estruturador (IA e Normalização)

* Atua como uma camada de normalização semântica na nuvem para corrigir distorções textuais e erros do OCR, como truncamentos ou substituições fonéticas (por exemplo, ler "Spril" em vez de "Sprite").


* O script `estruturador_ia.py` consome os logs locais via requisições HTTP síncronas e aciona a API do modelo Gemini 2.5 Flash-Lite.


* A inteligência artificial é instruída por engenharia de prompts rigorosa a atuar apenas como um parser semântico, retornando os dados em um esquema JSON rigoroso contendo cinco campos: Produto, Marca, Volume, Preço e Status de Promoção.


* O payload de dados é enriquecido com metadados contextuais, como a identificação do estabelecimento comercial.


* Foi implementada uma estratégia de retry com backoff exponencial para lidar com falhas transitórias e garantir a resiliência da comunicação com a API.



### 3. Frontend Web (Dashboard)

* A interface interativa de usuário foi desenvolvida em Python utilizando a framework Streamlit em conjunto com a biblioteca Pandas.


* O frontend consome o arquivo JSON gerado pela IA e realiza a transformação dos dados em DataFrames.


* O usuário tem acesso a um painel responsivo com indicadores-chave de desempenho (KPIs) calculados dinamicamente, tabelas interativas e gráficos de barras que permitem a filtragem e exploração dos dados por produto, marca, volume ou preço.



## Modelo de Negócios

A sustentabilidade financeira do projeto é fundamentada em uma arquitetura SaaS (Software as a Service) com fluxos de receita recorrente mensal (MRR). A comercialização é segmentada em duas vertentes principais:

* **Vertente B2C (Micro-SaaS):** Focada no consumidor final que busca economia no orçamento familiar, oferecendo uma assinatura de baixo ticket médio que tem o seu retorno sobre o investimento compensado pela economia gerada nas compras.


* **Vertente B2B:** Direcionada a pequenos varejistas, fornecedores e comércios locais (como restaurantes) na forma de um serviço corporativo de Inteligência de Mercado. Este modelo fornece acesso a relatórios automatizados, ferramentas de extração de dados em larga escala e dashboards de análise da concorrência.



## Equipe de Desenvolvimento

Projeto de Inovação (2026) desenvolvido pela equipe:

* Guilherme Cardoso


* Lucas Kühl


* Vilson Kühl


* Gustavo Henrique Alves
