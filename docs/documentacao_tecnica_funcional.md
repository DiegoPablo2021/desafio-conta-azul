# Documentacao tecnica e funcional - Desafio Conta Azul Business Analytics

## 1. Sumario executivo

Este documento descreve uma proposta completa para resolver o case de Business Analytics da Conta Azul a partir dos arquivos:

- `Desafio_tecnico_Business_Analytics_(1).pdf`
- `saas_funnel_case_10k_refresh_(4)_(2).csv`

O desafio pede uma analise de um produto digital SaaS com tres etapas principais de funil:

1. Visita ao site/app
2. Criacao de conta gratuita, chamada de `signup`
3. Assinatura de plano pago, chamada de `purchase`

O objetivo analitico e investigar o comportamento dos usuarios, identificar gargalos no funil, aplicar raciocinio analitico/estatistico e transformar achados em recomendacoes de negocio.

A base possui 10.000 usuarios unicos, visitando o produto entre 2025-06-01 e 2025-10-30. O funil geral observado foi:

| Etapa            | Volume | Taxa sobre visitas | Taxa sobre etapa anterior |
| ---------------- | -----: | -----------------: | ------------------------: |
| Visitas          | 10.000 |            100,00% |                   100,00% |
| Signups          |  2.983 |             29,83% |                    29,83% |
| Purchases        |    919 |              9,19% |        30,81% dos signups |
| Respostas de NPS |  1.206 |             12,06% |                       N/A |

Principais sinais preliminares:

- `referral` e `email` sao os canais com melhor conversao para compra.
- `paid` e `social` apresentam gargalos relevantes, principalmente na conversao final para plano pago.
- `desktop` converte melhor que `mobile` em todas as etapas principais.
- O NPS medio geral e 8,11, mas a separacao por comprador vs nao comprador muda muito a interpretacao: compradores possuem NPS estimado de 33,33, enquanto nao compradores possuem NPS estimado de -29,46.
- O plano `BASIC` concentra a maior parte das compras, com 526 de 919 compras, ou 57,24%.
- O dataset e consistente nas principais regras de negocio: nao ha compra sem signup, compra sem plano, plano sem compra, nem tempos preenchidos em registros incompativeis.

## 2. Entendimento funcional do desafio

### 2.1 Objetivo de negocio

O produto SaaS precisa entender onde perde usuarios no funil de aquisicao e monetizacao. A analise deve apoiar decisoes como:

- Em quais canais investir mais orcamento?
- Onde existe maior perda de eficiencia no funil?
- O problema esta em aquisicao, ativacao, conversao para pago ou experiencia?
- Existe diferenca relevante entre mobile e desktop?
- Ha segmentos com maior satisfacao e maior propensao a compra?
- Quais hipoteses de melhoria podem ser testadas em produto, marketing ou vendas?

### 2.2 Publico-alvo da analise

Stakeholders provaveis:

- Lideranca de Growth
- Product Manager
- Marketing Performance
- CRM/Lifecycle Marketing
- Customer Experience
- Business Analytics
- Diretoria de Receita ou Produto

### 2.3 Perguntas analiticas centrais

1. Qual e a taxa de conversao em cada etapa do funil?
2. Em qual etapa ocorre o maior gargalo?
3. Quais canais trazem maior volume e melhor qualidade?
4. O comportamento difere por dispositivo?
5. O comportamento difere por pais?
6. Existem mudancas relevantes ao longo dos meses?
7. Quais planos sao mais comprados?
8. Qual a relacao entre NPS e conversao?
9. Quais segmentos deveriam receber priorizacao?
10. Quais acoes de negocio podem melhorar conversao e satisfacao?

## 3. Inventario dos dados

### 3.1 Arquivos analisados

| Arquivo                                        | Tipo | Uso                       |
| ---------------------------------------------- | ---- | ------------------------- |
| `Desafio_tecnico_Business_Analytics_(1).pdf` | PDF  | Enunciado do desafio      |
| `saas_funnel_case_10k_refresh_(4)_(2).csv`   | CSV  | Base principal de analise |

### 3.2 Dicionario de dados original

| Campo                | Tipo observado  | Descricao funcional            | Observacoes                                                |
| -------------------- | --------------- | ------------------------------ | ---------------------------------------------------------- |
| `user_id`          | inteiro         | Identificador unico do usuario | 10.000 valores unicos                                      |
| `dt_visit`         | data em texto   | Data da primeira visita        | Range de 2025-06-01 a 2025-10-30                           |
| `channel`          | texto           | Canal de origem                | `organic`, `paid`, `referral`, `social`, `email` |
| `device`           | texto           | Dispositivo                    | `mobile`, `desktop`                                    |
| `country`          | texto           | Pais de origem                 | `BR`, `MX`, `AR`, `CL`, `US`                     |
| `signup`           | inteiro binario | 1 se criou conta gratuita      | 0 ou 1                                                     |
| `purchase`         | inteiro binario | 1 se assinou plano pago        | 0 ou 1                                                     |
| `plan`             | texto           | Plano pago escolhido           | `BASIC`, `PRO`, `PREMIUM`, nulo quando nao comprou   |
| `days_to_signup`   | numerico        | Dias entre visita e signup     | Nulo quando nao houve signup                               |
| `days_to_purchase` | numerico        | Dias entre signup e compra     | Nulo quando nao houve purchase                             |
| `respondeu_nps`    | inteiro binario | 1 se respondeu NPS             | 0 ou 1                                                     |
| `nps_score`        | numerico        | Nota NPS                       | Nulo quando nao respondeu                                  |

### 3.3 Granularidade

A granularidade da tabela e:

> Uma linha por usuario que realizou a primeira visita ao produto no periodo analisado.

Isso significa que:

- `user_id` deve ser chave unica da tabela.
- `signup` e `purchase` sao flags de status do usuario dentro da janela de observacao.
- `dt_visit` representa a data inicial do ciclo do usuario.
- `days_to_signup` e `days_to_purchase` sao offsets relativos, nao datas absolutas.
- A data estimada de signup pode ser derivada como `dt_visit + days_to_signup`.
- A data estimada de compra pode ser derivada como `dt_visit + days_to_signup + days_to_purchase`, assumindo que `days_to_purchase` e contado a partir do signup, conforme descrito no PDF.

### 3.4 Volumetria

| Metrica                  |      Valor |
| ------------------------ | ---------: |
| Linhas                   |     10.000 |
| Usuarios unicos          |     10.000 |
| Usuarios duplicados      |          0 |
| Colunas                  |         12 |
| Primeira visita          | 2025-06-01 |
| Ultima visita            | 2025-10-30 |
| Dias distintos de visita |        152 |

## 4. Diagnostico de qualidade dos dados

### 4.1 Validacoes executadas

| Regra                                                | Resultado |
| ---------------------------------------------------- | --------: |
| `purchase = 1` sem `signup = 1`                  |         0 |
| `plan` preenchido sem `purchase = 1`             |         0 |
| `purchase = 1` sem `plan`                        |         0 |
| `days_to_signup` preenchido sem `signup = 1`     |         0 |
| `signup = 1` sem `days_to_signup`                |         0 |
| `days_to_purchase` preenchido sem `purchase = 1` |         0 |
| `purchase = 1` sem `days_to_purchase`            |         0 |
| `nps_score` preenchido sem `respondeu_nps = 1`   |         0 |
| `respondeu_nps = 1` sem `nps_score`              |         0 |
| Respostas de NPS de nao compradores                  |       465 |

### 4.2 Interpretacao da qualidade

O dataset esta adequado para a analise proposta. As regras essenciais do funil estao consistentes.

O principal cuidado semantico e o NPS. Existem 465 respostas de NPS de usuarios que nao compraram. Logo, o NPS nao deve ser interpretado apenas como satisfacao de clientes pagantes. Ele deve ser analisado em pelo menos dois recortes:

- NPS de compradores
- NPS de nao compradores

Essa separacao evita conclusoes incorretas. Por exemplo, o NPS geral pode parecer saudavel, mas esconder forte insatisfacao entre usuarios que nao avancaram para compra.

### 4.3 Regras recomendadas para producao

Em uma solucao produtiva, as validacoes minimas devem bloquear ou alertar quando:

- Houver `purchase = 1` e `signup = 0`.
- Houver `purchase = 1` e `plan` nulo.
- Houver `plan` preenchido e `purchase = 0`.
- Houver valores de `signup`, `purchase` ou `respondeu_nps` fora de 0 e 1.
- Houver `nps_score` fora do intervalo 0 a 10.
- Houver `days_to_signup` ou `days_to_purchase` negativo.
- Houver duplicidade de `user_id`.
- Houver `dt_visit` invalida ou fora da janela esperada.
- Houver categorias inesperadas para canal, dispositivo, pais ou plano.

## 5. Diagnostico analitico preliminar

### 5.1 Funil geral

| Metrica              |  Valor |
| -------------------- | -----: |
| Visitas              | 10.000 |
| Signups              |  2.983 |
| Compras              |    919 |
| Visit to signup      | 29,83% |
| Visit to purchase    |  9,19% |
| Signup to purchase   | 30,81% |
| Taxa de resposta NPS | 12,06% |

Interpretacao:

- O primeiro gargalo e a conversao de visita para signup, pois 70,17% dos visitantes nao criam conta.
- O segundo gargalo tambem e material: 69,19% dos usuarios que criaram conta nao compram.
- Como o case e SaaS, a etapa signup to purchase deve ser investigada como ativacao, onboarding, pricing, prova de valor e friccao comercial.

### 5.2 Performance por canal

| Canal    | Visitas | Signups | Compras | Visit to signup | Visit to purchase | Signup to purchase | NPS medio |
| -------- | ------: | ------: | ------: | --------------: | ----------------: | -----------------: | --------: |
| organic  |   4.271 |   1.339 |     459 |          31,35% |            10,75% |             34,28% |      8,17 |
| paid     |   3.247 |     828 |     169 |          25,50% |             5,20% |             20,41% |      7,85 |
| social   |     999 |     219 |      41 |          21,92% |             4,10% |             18,72% |      7,99 |
| referral |     982 |     409 |     179 |          41,65% |            18,23% |             43,77% |      8,38 |
| email    |     501 |     188 |      71 |          37,52% |            14,17% |             37,77% |      8,06 |

Leituras principais:

- `referral` e o melhor canal em qualidade: maior visit to signup, maior visit to purchase, maior signup to purchase e melhor NPS medio.
- `email` tem baixo volume, mas boa eficiencia. Pode ser um canal promissor para lifecycle, retargeting ou base propria.
- `organic` combina escala e boa conversao. Deve ser protegido e ampliado com SEO, conteudo e otimizar paginas de entrada.
- `paid` tem volume alto, mas conversao final baixa. Antes de aumentar budget, e necessario revisar segmentacao, mensagem, landing pages, palavras-chave, criativos e expectativa gerada.
- `social` tem baixa conversao e baixo volume relativo. Deve ser tratado como canal de topo de funil ou passar por revisao de audiencia e proposta de valor.

### 5.3 Performance por dispositivo

| Dispositivo | Visitas | Signups | Compras | Visit to signup | Visit to purchase | Signup to purchase | NPS medio |
| ----------- | ------: | ------: | ------: | --------------: | ----------------: | -----------------: | --------: |
| desktop     |   3.758 |   1.359 |     493 |          36,16% |            13,12% |             36,28% |      8,18 |
| mobile      |   6.242 |   1.624 |     426 |          26,02% |             6,82% |             26,23% |      8,05 |

Leituras principais:

- Mobile representa 62,42% das visitas, mas converte muito menos que desktop.
- Desktop tem quase o dobro da conversao visit to purchase em relacao a mobile.
- A diferenca sugere friccao de UX, performance, formulario, checkout, clareza de valor ou comportamento de pesquisa em mobile.
- Como mobile tem maior volume, pequenas melhorias nesse fluxo podem gerar impacto absoluto relevante.

### 5.4 Performance por pais

| Pais | Visitas | Signups | Compras | Visit to signup | Visit to purchase | Signup to purchase | NPS medio |
| ---- | ------: | ------: | ------: | --------------: | ----------------: | -----------------: | --------: |
| BR   |   6.986 |   2.084 |     644 |          29,83% |             9,22% |             30,90% |      8,12 |
| MX   |   1.009 |     308 |      95 |          30,53% |             9,42% |             30,84% |      7,99 |
| AR   |     807 |     231 |      74 |          28,62% |             9,17% |             32,03% |      8,01 |
| CL   |     708 |     220 |      58 |          31,07% |             8,19% |             26,36% |      8,15 |
| US   |     490 |     140 |      48 |          28,57% |             9,80% |             34,29% |      8,23 |

Leituras principais:

- O Brasil concentra quase 70% das visitas e compras. E o mercado central da amostra.
- As taxas por pais sao relativamente proximas.
- O Chile tem boa taxa de signup, mas menor signup to purchase, sinalizando possivel gargalo pos-signup.
- Os EUA tem menor volume, mas boa eficiencia relativa. Como a amostra e pequena, conclusoes devem ser tratadas com cautela.

### 5.5 Performance temporal

| Mes     | Visitas | Signups | Compras | Visit to signup | Visit to purchase | Signup to purchase | NPS medio |
| ------- | ------: | ------: | ------: | --------------: | ----------------: | -----------------: | --------: |
| 2025-06 |   1.872 |     581 |     164 |          31,04% |             8,76% |             28,23% |      7,94 |
| 2025-07 |   2.053 |     593 |     165 |          28,88% |             8,04% |             27,82% |      8,03 |
| 2025-08 |   2.121 |     615 |     201 |          29,00% |             9,48% |             32,68% |      8,07 |
| 2025-09 |   1.955 |     607 |     211 |          31,05% |            10,79% |             34,76% |      8,22 |
| 2025-10 |   1.999 |     587 |     178 |          29,36% |             8,90% |             30,32% |      8,33 |

Leituras principais:

- Setembro foi o melhor mes em visit to purchase e signup to purchase.
- O NPS medio cresce de junho a outubro, sugerindo melhora de experiencia ou mudanca de mix.
- Outubro tem NPS maior, mas menor conversao que setembro. Isso pode indicar que satisfacao e conversao nao estao perfeitamente alinhadas no periodo.

### 5.6 Planos

| Plano   | Compras | Participacao | NPS medio | Respostas NPS | Media de dias ate compra |
| ------- | ------: | -----------: | --------: | ------------: | -----------------------: |
| BASIC   |     526 |       57,24% |      8,65 |           428 |                    10,43 |
| PRO     |     287 |       31,23% |      8,58 |           228 |                    10,78 |
| PREMIUM |     106 |       11,53% |      8,55 |            85 |                     9,91 |

Leituras principais:

- `BASIC` e o principal motor de conversao.
- `PRO` e relevante e pode representar melhor monetizacao, mas a base nao traz receita. Sem preco ou MRR, nao se deve concluir qual plano e mais valioso financeiramente.
- `PREMIUM` tem menor volume. Pode haver oportunidade de upsell, mas seria necessario analisar preco, perfil e valor percebido.

### 5.7 NPS

Classificacao sugerida:

- Promotor: `nps_score >= 9`
- Neutro/passivo: `7 <= nps_score < 9`
- Detrator: `nps_score < 7`

Observacao: o dataset possui notas decimais. O NPS tradicional costuma usar nota inteira de 0 a 10. Como o dado vem decimal, a classificacao acima deve ser documentada como regra analitica adotada.

| Segmento        | Respostas | NPS medio | NPS estimado | Promotores | Passivos | Detratores |
| --------------- | --------: | --------: | -----------: | ---------: | -------: | ---------: |
| Geral           |     1.206 |      8,11 |         9,12 |        337 |      642 |        227 |
| Compradores     |       741 |      8,62 |        33,33 |        274 |      440 |         27 |
| Nao compradores |       465 |      7,30 |       -29,46 |         63 |      202 |        200 |

Interpretacao:

- O NPS geral esconde duas realidades muito diferentes.
- Usuarios que compram estao bem mais satisfeitos.
- Usuarios que nao compram possuem insatisfacao relevante.
- Esse padrao sugere que quem percebe valor suficiente para comprar tambem tende a avaliar melhor a experiencia, enquanto usuarios que nao convertem podem estar enfrentando desalinhamento de expectativa, friccao de ativacao ou baixa percepcao de valor.

## 6. Stacks sugeridas

### 6.1 Stack recomendada - Local, aderente ao desafio e ao contexto do candidato

Esta e a stack recomendada para resolver este desafio localmente, sem depender de ambiente corporativo, BigQuery, Snowflake, Google Sheets, Looker ou Power BI.

Componentes:

- Python como linguagem principal do projeto
- Pandas para leitura, profiling, validacoes e preparacao dos dados
- DuckDB para executar SQL local diretamente sobre o CSV e sobre views analiticas
- Plotly para graficos interativos
- Streamlit para o dashboard local
- Word para o resumo executivo de ate 2 paginas
- Markdown para documentacao tecnica versionavel

Justificativa:

- O enunciado aceita SQL, planilha, dashboard e notebook.
- O dataset e pequeno, com 10.000 linhas, entao nao ha necessidade de cloud.
- Streamlit e uma escolha defensavel porque permite entregar um dashboard local e interativo sem depender de licencas ou ambiente externo.
- DuckDB permite escrever SQL local com uma experiencia proxima de analytics engineering, sem servidor, credencial ou warehouse.
- Plotly gera graficos interativos adequados para funil, series temporais, ranking por canal, comparacoes por dispositivo e analise de NPS.
- Word atende diretamente ao entregavel de resumo de conclusoes em ate 2 paginas.
- Excel fica dispensavel nesta arquitetura, podendo ser usado apenas se houver necessidade de conferencia manual.

Entrega recomendada:

| Entregavel | Ferramenta recomendada | Papel na solucao |
|---|---|---|
| Pipeline local | Python + Pandas | Leitura, tratamento, validacao e datasets derivados |
| SQL local | DuckDB | Views e consultas reproduziveis do funil e segmentos |
| Graficos | Plotly | Visualizacoes interativas |
| Dashboard | Streamlit | Aplicacao local para exploracao executiva |
| Resumo executivo | Word/DOCX | Conclusoes em ate 2 paginas |
| Documentacao tecnica | Markdown | Arquitetura, metricas, regras e instrucoes |

Recomendacao pratica:

> Usar Python + Pandas + DuckDB + Plotly + Streamlit como stack principal. Usar Word para o resumo executivo e Markdown para a documentacao tecnica.

### 6.2 Stack alternativa - Somente Power BI e Excel

Indicada se o tempo estiver curto e a prioridade for entregar visual e resumo executivo.

Componentes:

- Power BI Desktop
- Power Query
- DAX
- Excel opcional

Vantagens:

- Baixa barreira de execucao.
- Tudo roda localmente.
- Boa qualidade visual.
- Permite criar dashboard e medidas sem infraestrutura adicional.

Desvantagens:

- Menor reprodutibilidade tecnica fora do Power BI.
- SQL fica ausente ou limitado.
- Analises estatisticas e validacoes ficam menos transparentes que em notebook.

Uso recomendado:

- Boa opcao de contingencia.
- Nao e a opcao mais forte se a intencao for demonstrar tambem dominio tecnico em dados.

### 6.3 Stack alternativa - Notebook first

Indicada se a prioridade for demonstrar raciocinio analitico e estatistico.

Componentes:

- Python
- Pandas
- Matplotlib/Seaborn/Plotly
- DuckDB opcional
- Excel opcional para export de tabelas

Vantagens:

- Alta rastreabilidade.
- Excelente para qualidade de dados e EDA.
- Facil gerar tabelas, graficos e evidencias.
- Permite documentar raciocinio passo a passo.

Desvantagens:

- Menos executivo que um dashboard interativo.
- Pode exigir mais storytelling no resumo final.

Uso recomendado:

- Muito bom para a analise.
- Ideal quando combinado com Power BI para a camada visual.

### 6.4 Stack nao recomendada para execucao do case - Cloud/Looker/BigQuery/Snowflake

A Conta Azul pode usar Looker internamente, mas nao e necessario usar Looker para este desafio se voce nao tem dominio da ferramenta nem acesso a ambiente.

Componentes que poderiam existir em ambiente corporativo:

- Looker
- BigQuery
- Snowflake
- Databricks
- Airflow
- dbt Cloud

Por que nao usar como stack principal neste case:

- Voce nao tem acesso a ambiente.
- O prazo do desafio e curto.
- O dataset e pequeno e local.
- A curva de aprendizado poderia tirar foco do que realmente sera avaliado: raciocinio analitico, clareza, metricas e recomendacoes.

Como mencionar corretamente:

> "Embora a empresa utilize Looker, optei por Streamlit como dashboard local por ser uma solucao leve, reproduzivel e sem dependencia de ambiente corporativo. As metricas e consultas foram estruturadas em SQL com DuckDB, podendo ser migradas para Looker ou outra camada semantica em ambiente corporativo."

### 6.5 Observacao sobre Looker vs Streamlit

Usar Streamlit nao enfraquece a entrega, desde que a solucao seja bem documentada e o dashboard tenha leitura executiva. O ponto principal do case e demonstrar raciocinio analitico, clareza de metricas, qualidade de conclusoes e recomendacoes acionaveis.

O avaliador provavelmente observara:

- Se os KPIs estao corretos.
- Se o funil foi bem interpretado.
- Se os gargalos foram identificados.
- Se as recomendacoes fazem sentido para negocio.
- Se as conclusoes estao conectadas a dados.
- Se a entrega e clara, organizada e reproduzivel.

Para reduzir qualquer risco por a empresa usar Looker, inclua uma frase no resumo metodologico:

> "O dashboard foi desenvolvido em Streamlit para permitir execucao local e reproducivel. As metricas foram implementadas em SQL com DuckDB e documentadas de forma agnostica, podendo ser reproduzidas em Looker, Power BI, Excel ou qualquer camada semantica equivalente."

### 6.6 Stack final recomendada para entrega

Recomendacao principal:

> Python + Pandas + DuckDB + Plotly + Streamlit + Word.

Na pratica:

- Usar Pandas para carregar o CSV, aplicar tipos, validar qualidade e criar campos derivados.
- Usar DuckDB como camada SQL local, com views para `staging`, funil, canais, dispositivos, paises, planos, tempo e NPS.
- Usar Plotly para os graficos interativos.
- Usar Streamlit para entregar o dashboard local.
- Usar Word para o resumo executivo de ate 2 paginas exigido no desafio.
- Documentar que a empresa usa Looker, mas que as metricas e regras foram estruturadas de forma agnostica e poderiam ser reproduzidas em Looker.

## 7. Arquitetura proposta

### 7.1 Arquitetura para o case

Fluxo recomendado:

```text
CSV original
  -> Raw
  -> Staging validado e tipado
  -> Views SQL no DuckDB
  -> Dataframes analiticos em Pandas
  -> Graficos Plotly
  -> Dashboard Streamlit
  -> Resumo executivo em Word
```

### 7.1.1 Estrutura fisica implementada

Estrutura alvo do projeto local:

```text
desafio-conta-azul/
  app.py
  .vscode/
    settings.json
  .streamlit/
    config.toml
  notebooks/
    01_eda_funil_saas.ipynb
  requirements.txt
  README.md
  Desafio_tecnico_Business_Analytics_(1).pdf
  saas_funnel_case_10k_refresh_(4)_(2).csv
  src/
    __init__.py
    config.py
    data_pipeline.py
    metrics.py
  sql/
    01_create_views.sql
    02_funnel_analysis.sql
    03_nps_analysis.sql
  docs/
    assets/
      image-end-to-end.png
      arquitetura_pipeline_dados.png
    documentacao_tecnica_funcional.md
    guia_celulas_notebook.md
    resumo_executivo.md
  output/
    doc/
      resumo_executivo_conta_azul.docx
```

Responsabilidades principais:

- `app.py`: aplicacao Streamlit e composicao visual do dashboard.
- `.vscode/settings.json`: configuracao do interpretador Python 3.13 e caminhos de analise do Pylance.
- `.streamlit/config.toml`: configuracao de tema global do Streamlit.
- `notebooks/01_eda_funil_saas.ipynb`: notebook de investigacao, profiling, validacoes, graficos e conclusoes preliminares.
- `src/config.py`: caminhos e configuracoes centrais.
- `src/data_pipeline.py`: leitura do CSV, profiling, tratamento, validacoes e registro de views no DuckDB.
- `src/metrics.py`: funcoes de consulta e metricas usadas pelo dashboard.
- `sql/`: consultas SQL reproduziveis para avaliacao tecnica.
- `docs/`: documentacao tecnica e resumo executivo em Markdown.
- `docs/assets/`: imagens usadas na documentacao e no README.
- `docs/guia_celulas_notebook.md`: explicacao celula a celula do notebook de EDA.
- `scripts/`: geradores opcionais dos documentos Word em `output/doc/`.
- `output/doc/`: pasta de saida local criada pelos scripts. O resumo executivo em Word e versionado como entregavel formal; os demais `.docx` de apoio ficam ignorados.

### 7.2 Camadas

#### Raw

Objetivo:

- Preservar o arquivo original sem transformacao destrutiva.

Responsabilidades:

- Armazenar o CSV exatamente como recebido.
- Registrar nome do arquivo, data de ingestao e hash se possivel.
- Nao aplicar regra de negocio.

Tabelas/arquivos:

- `raw_saas_funnel_case`

#### Staging

Objetivo:

- Padronizar tipos, nomes e regras tecnicas.

Transformacoes:

- Converter `dt_visit` para data.
- Converter flags para inteiros ou booleanos.
- Normalizar categorias textuais.
- Criar `signup_date` quando aplicavel.
- Criar `purchase_date` quando aplicavel.
- Validar dominios.
- Validar consistencia do funil.

Tabelas/arquivos:

- `stg_saas_funnel_users`

#### Trusted ou marts

Objetivo:

- Criar tabelas prontas para analise e BI.

Possiveis tabelas:

- `fact_user_funnel`
- `dim_date`
- `dim_channel`
- `dim_device`
- `dim_country`
- `dim_plan`
- `fact_nps_response` ou NPS incorporado em `fact_user_funnel`, dependendo da modelagem escolhida.

### 7.3 Modelo dimensional recomendado

Na implementacao local com DuckDB e Streamlit, o modelo fisico sera simplificado para views analiticas. Mesmo assim, a logica segue principios de modelo dimensional:

- Uma view principal `stg_funnel_users`, com uma linha por usuario.
- Views agregadas para funil geral, canal, dispositivo, pais, mes, plano e NPS.
- Campos derivados de data e classificacao criados na camada de staging.
- Regras de metricas centralizadas em SQL e reutilizadas no dashboard.

Views criadas em memoria pelo DuckDB:

| View | Objetivo |
|---|---|
| `vw_funnel_overall` | Funil geral e taxas principais |
| `vw_funnel_by_channel` | Conversao por canal |
| `vw_funnel_by_device` | Conversao por dispositivo |
| `vw_funnel_by_country` | Conversao por pais |
| `vw_funnel_by_month` | Evolucao mensal |
| `vw_plan_mix` | Mix de planos comprados |
| `vw_channel_device` | Conversao cruzada por canal e dispositivo |
| `vw_nps_summary` | NPS geral, compradores e nao compradores |
| `vw_nps_by_channel` | NPS por canal |

#### Grao da fato principal

`fact_user_funnel`:

> Uma linha por usuario visitado.

Colunas sugeridas:

| Coluna                | Descricao                        |
| --------------------- | -------------------------------- |
| `user_id`           | Chave do usuario                 |
| `visit_date_key`    | Chave da data de visita          |
| `signup_date_key`   | Chave da data estimada de signup |
| `purchase_date_key` | Chave da data estimada de compra |
| `channel_key`       | Chave do canal                   |
| `device_key`        | Chave do dispositivo             |
| `country_key`       | Chave do pais                    |
| `plan_key`          | Chave do plano                   |
| `signup_flag`       | 1/0                              |
| `purchase_flag`     | 1/0                              |
| `days_to_signup`    | Dias ate signup                  |
| `days_to_purchase`  | Dias do signup ate compra        |
| `nps_response_flag` | 1/0                              |
| `nps_score`         | Nota NPS                         |

#### Dimensoes

`dim_date`:

- `date_key`
- `date`
- `year`
- `quarter`
- `month`
- `month_name`
- `year_month`
- `week`
- `day`

`dim_channel`:

- `channel_key`
- `channel_name`
- `channel_group`
- `is_paid_media`

`dim_device`:

- `device_key`
- `device_name`

`dim_country`:

- `country_key`
- `country_code`
- `country_name`
- `region`

`dim_plan`:

- `plan_key`
- `plan_name`
- `plan_tier`
- `plan_sort_order`

### 7.4 Semantica analitica no dashboard local

Como a implementacao final usa DuckDB e Streamlit, nao ha relacionamentos fisicos de Power BI. Ainda assim, a solucao preserva uma semantica analitica clara:

- `stg_funnel_users` funciona como a tabela principal, com uma linha por usuario.
- As dimensoes de analise sao colunas controladas: `channel`, `device`, `country`, `plan` e `visit_month`.
- As metricas sao calculadas por SQL no DuckDB, sempre a partir da mesma camada de staging.
- Os filtros do Streamlit reduzem a base e recriam a conexao DuckDB em memoria para recalcular as metricas.
- Essa abordagem evita divergencia entre graficos, tabelas e KPIs.

Padrao conceitual preservado:

- Dimensoes filtram a fato principal.
- Cada metrica tem definicao centralizada.
- O grao declarado permanece uma linha por usuario.
- Datas de visita, signup e compra sao tratadas com significado explicito.

Em uma migracao futura para Looker, Power BI ou outra camada semantica, os mesmos campos poderiam virar dimensoes e medidas formais.

Referencia conceitual para uma ferramenta de BI corporativa:

Relacionamentos:

| Dimensao                     | Fato                                    | Relacao     |
| ---------------------------- | --------------------------------------- | ----------- |
| `dim_channel[channel_key]` | `fact_user_funnel[channel_key]`       | 1:*         |
| `dim_device[device_key]`   | `fact_user_funnel[device_key]`        | 1:*         |
| `dim_country[country_key]` | `fact_user_funnel[country_key]`       | 1:*         |
| `dim_plan[plan_key]`       | `fact_user_funnel[plan_key]`          | 1:*         |
| `dim_date[date_key]`       | `fact_user_funnel[visit_date_key]`    | 1:* ativo   |
| `dim_date[date_key]`       | `fact_user_funnel[signup_date_key]`   | 1:* inativo |
| `dim_date[date_key]`       | `fact_user_funnel[purchase_date_key]` | 1:* inativo |

Observacao:

- A relacao ativa principal deve ser por data de visita, porque o enunciado diz que cada linha representa um usuario que visitou entre junho e outubro/2025.
- Analises por data de signup ou compra devem usar medidas DAX com `USERELATIONSHIP`, se essas datas forem criadas.

## 8. Transformacoes recomendadas

### 8.1 Regras de tipagem

| Campo                | Tipo final       |
| -------------------- | ---------------- |
| `user_id`          | inteiro          |
| `dt_visit`         | date             |
| `channel`          | string/categoria |
| `device`           | string/categoria |
| `country`          | string/categoria |
| `signup`           | inteiro/boolean  |
| `purchase`         | inteiro/boolean  |
| `plan`             | string/categoria |
| `days_to_signup`   | inteiro nullable |
| `days_to_purchase` | inteiro nullable |
| `respondeu_nps`    | inteiro/boolean  |
| `nps_score`        | decimal nullable |

### 8.2 Campos derivados

Campos recomendados:

- `signup_date = dt_visit + days_to_signup`
- `purchase_date = signup_date + days_to_purchase`
- `visited_flag = 1`
- `funnel_stage`
- `nps_class`
- `has_nps_score`
- `is_purchaser`
- `is_signup`

Regra de `funnel_stage`:

```text
purchase = 1 -> Purchased
signup = 1 and purchase = 0 -> Signup only
signup = 0 -> Visit only
```

Regra de `nps_class`:

```text
nps_score >= 9 -> Promoter
7 <= nps_score < 9 -> Passive
nps_score < 7 -> Detractor
nps_score is null -> No response
```

### 8.3 Validacoes de staging

Exemplos de validacoes:

```sql
-- Duplicidade de usuario
select user_id, count(*) as qtd
from stg_saas_funnel_users
group by user_id
having count(*) > 1;
```

```sql
-- Compra sem signup
select count(*) as invalid_rows
from stg_saas_funnel_users
where purchase = 1 and signup = 0;
```

```sql
-- Plano inconsistente
select count(*) as invalid_rows
from stg_saas_funnel_users
where (purchase = 1 and plan is null)
   or (purchase = 0 and plan is not null);
```

```sql
-- NPS fora do intervalo
select count(*) as invalid_rows
from stg_saas_funnel_users
where nps_score < 0 or nps_score > 10;
```

```sql
-- Datas e tempos invalidos
select count(*) as invalid_rows
from stg_saas_funnel_users
where days_to_signup < 0
   or days_to_purchase < 0;
```

## 9. KPIs e definicoes semanticas

### 9.1 KPIs principais

| KPI                            | Formula                                     | Interpretacao                     |
| ------------------------------ | ------------------------------------------- | --------------------------------- |
| Visits                         | `count(user_id)`                          | Usuarios visitantes               |
| Signups                        | `sum(signup)`                             | Usuarios que criaram conta        |
| Purchases                      | `sum(purchase)`                           | Usuarios que compraram plano      |
| Visit to signup rate           | `signups / visits`                        | Eficiencia da primeira conversao  |
| Visit to purchase rate         | `purchases / visits`                      | Eficiencia total do funil         |
| Signup to purchase rate        | `purchases / signups`                     | Eficiencia pos-cadastro           |
| Signup drop-off                | `1 - visit_to_signup_rate`                | Perda antes do signup             |
| Purchase drop-off after signup | `1 - signup_to_purchase_rate`             | Perda entre signup e compra       |
| Avg days to signup             | `avg(days_to_signup)` filtrando signups   | Velocidade de criacao de conta    |
| Avg days to purchase           | `avg(days_to_purchase)` filtrando compras | Velocidade de conversao para pago |
| NPS response rate              | `nps responses / visits`                  | Cobertura da pesquisa             |
| Avg NPS score                  | `avg(nps_score)`                          | Satisfacao media                  |
| NPS                            | `% promoters - % detractors`              | Indicador padrao de lealdade      |

### 9.2 Medidas DAX sugeridas

```DAX
Visits =
COUNTROWS ( 'fact_user_funnel' )
```

```DAX
Signups =
SUM ( 'fact_user_funnel'[signup_flag] )
```

```DAX
Purchases =
SUM ( 'fact_user_funnel'[purchase_flag] )
```

```DAX
Visit to Signup Rate =
DIVIDE ( [Signups], [Visits] )
```

```DAX
Visit to Purchase Rate =
DIVIDE ( [Purchases], [Visits] )
```

```DAX
Signup to Purchase Rate =
DIVIDE ( [Purchases], [Signups] )
```

```DAX
Signup Drop-off Rate =
1 - [Visit to Signup Rate]
```

```DAX
Post Signup Drop-off Rate =
1 - [Signup to Purchase Rate]
```

```DAX
NPS Responses =
CALCULATE (
    COUNTROWS ( 'fact_user_funnel' ),
    'fact_user_funnel'[nps_response_flag] = 1
)
```

```DAX
Average NPS Score =
AVERAGE ( 'fact_user_funnel'[nps_score] )
```

```DAX
Promoters =
CALCULATE (
    COUNTROWS ( 'fact_user_funnel' ),
    'fact_user_funnel'[nps_score] >= 9
)
```

```DAX
Detractors =
CALCULATE (
    COUNTROWS ( 'fact_user_funnel' ),
    'fact_user_funnel'[nps_score] < 7
)
```

```DAX
NPS =
VAR Responses = [NPS Responses]
RETURN
    DIVIDE ( [Promoters] - [Detractors], Responses ) * 100
```

```DAX
Average Days to Signup =
CALCULATE (
    AVERAGE ( 'fact_user_funnel'[days_to_signup] ),
    'fact_user_funnel'[signup_flag] = 1
)
```

```DAX
Average Days to Purchase =
CALCULATE (
    AVERAGE ( 'fact_user_funnel'[days_to_purchase] ),
    'fact_user_funnel'[purchase_flag] = 1
)
```

### 9.3 Medidas por relacionamento inativo de data

Se forem criadas `signup_date_key` e `purchase_date_key`:

```DAX
Signups by Signup Date =
CALCULATE (
    [Signups],
    USERELATIONSHIP ( 'dim_date'[date_key], 'fact_user_funnel'[signup_date_key] )
)
```

```DAX
Purchases by Purchase Date =
CALCULATE (
    [Purchases],
    USERELATIONSHIP ( 'dim_date'[date_key], 'fact_user_funnel'[purchase_date_key] )
)
```

## 10. Consultas SQL sugeridas

### 10.1 Funil geral

```sql
select
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate
from stg_saas_funnel_users;
```

### 10.2 Funil por canal

```sql
select
    channel,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_saas_funnel_users
group by channel
order by visit_to_purchase_rate desc;
```

### 10.3 Funil por dispositivo

```sql
select
    device,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate
from stg_saas_funnel_users
group by device
order by visit_to_purchase_rate desc;
```

### 10.4 NPS por comprador e nao comprador

```sql
select
    case when purchase = 1 then 'Purchaser' else 'Non purchaser' end as segment,
    count(*) filter (where nps_score is not null) as nps_responses,
    avg(nps_score) as avg_nps_score,
    (
        sum(case when nps_score >= 9 then 1 else 0 end)
        - sum(case when nps_score < 7 then 1 else 0 end)
    ) * 100.0 / nullif(count(*) filter (where nps_score is not null), 0) as nps
from stg_saas_funnel_users
where nps_score is not null
group by 1;
```

### 10.5 Evolucao mensal

```sql
select
    date_trunc('month', dt_visit) as visit_month,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_saas_funnel_users
group by 1
order by 1;
```

## 11. Analise estatistica recomendada

### 11.1 Intervalos de confianca

Para evitar interpretar diferencas pequenas como definitivas, usar intervalo de confianca para taxas de conversao, preferencialmente Wilson score interval.

Exemplo de leitura:

- `referral` tem visit to purchase de 18,23%, com intervalo aproximado de 15,94% a 20,77%.
- `paid` tem visit to purchase de 5,20%, com intervalo aproximado de 4,49% a 6,02%.
- A distancia entre `referral` e `paid` e grande o suficiente para sustentar uma recomendacao de negocio.

### 11.2 Testes de proporcao

Testes recomendados:

- `referral` vs `paid` para taxa de compra.
- `desktop` vs `mobile` para taxa de signup e compra.
- `email` vs `organic` para avaliar se email e realmente superior dado o menor volume.

### 11.3 Analise de coorte simples

Como ha data de visita, e possivel avaliar coortes mensais por `dt_visit`.

Perguntas:

- Usuarios que visitaram em setembro converteram mais por mudanca de produto, mix de canal ou campanha?
- A melhora de NPS em outubro veio de experiencia melhor ou mudanca na composicao de respondentes?

### 11.4 Segmentacao

Segmentos prioritarios:

- Canal x dispositivo
- Canal x pais
- Dispositivo x pais
- Plano x canal
- Comprador vs nao comprador no NPS

## 12. Proposta de dashboard

### 12.1 Pagina 1 - Executive overview

Objetivo:

- Dar leitura executiva rapida do funil e dos principais gargalos.

Componentes:

- Cards: visits, signups, purchases, visit to signup, signup to purchase, visit to purchase, NPS.
- Funnel chart: visitas -> signups -> purchases.
- Linha mensal: visit to purchase e NPS medio.
- Barras: compras por canal.
- Destaques textuais com principais oportunidades.

Filtros:

- Mes de visita
- Canal
- Dispositivo
- Pais
- Plano

### 12.2 Pagina 2 - Funnel diagnostics

Objetivo:

- Diagnosticar perdas por segmento.

Componentes:

- Matriz por canal com visitas, signups, compras e taxas.
- Matriz por dispositivo.
- Heatmap canal x dispositivo para visit to purchase.
- Barras de drop-off por etapa.
- Tooltip com dias medios ate signup e compra.

### 12.3 Pagina 3 - Channel performance

Objetivo:

- Apoiar decisao de investimento e priorizacao de canais.

Componentes:

- Scatterplot: volume de visitas vs visit to purchase, tamanho por compras, cor por NPS.
- Ranking de canais por eficiencia.
- Tabela com intervalos de confianca.
- Comparacao de mix de planos por canal.

Mensagem esperada:

- `referral` e `email` sao canais de alta qualidade.
- `paid` precisa de otimizacao antes de escala.
- `organic` merece investimento por combinar escala e eficiencia.

### 12.4 Pagina 4 - Device and UX

Objetivo:

- Evidenciar a oportunidade de melhorar mobile.

Componentes:

- Comparacao desktop vs mobile nas tres taxas principais.
- Canal x dispositivo para taxa de compra.
- Tempo medio ate signup e compra por dispositivo.
- NPS por dispositivo.

Mensagem esperada:

- Mobile e maior volume, mas menor conversao.
- Priorizar auditoria de UX e checkout mobile.

### 12.5 Pagina 5 - NPS and experience

Objetivo:

- Separar experiencia de compradores e nao compradores.

Componentes:

- NPS geral, NPS de compradores e NPS de nao compradores.
- Distribuicao de notas.
- NPS por canal.
- NPS por plano.
- Conversao por classe de NPS, com cuidado para nao inferir causalidade.

Mensagem esperada:

- Nao compradores estao muito menos satisfeitos.
- Entender motivos de nao conversao pode destravar crescimento.

## 13. Recomendacoes de negocio

### 13.1 Priorizar referral

Evidencia:

- Maior visit to purchase: 18,23%.
- Maior signup to purchase: 43,77%.
- Maior NPS medio por canal: 8,38.
- Menor tempo medio ate signup: 1,11 dia.
- Menor tempo medio ate compra: 5,56 dias.

Recomendacoes:

- Criar ou fortalecer programa de indicacao.
- Testar incentivos para quem indica e para quem recebe convite.
- Medir CAC, taxa de fraude, qualidade e retencao futura.
- Criar landing page especifica para indicados com prova social.

### 13.2 Otimizar paid antes de escalar investimento

Evidencia:

- Paid tem 3.247 visitas, segundo maior volume.
- Visit to purchase de apenas 5,20%.
- Signup to purchase de 20,41%, abaixo de organic, referral e email.
- NPS estimado por canal negativo quando calculado por promotores/detratores: -3,32.

Hipoteses:

- Segmentacao de midia pouco qualificada.
- Criativos prometem valor desalinhado ao produto.
- Landing page nao comunica bem o valor.
- Termos pagos atraem usuarios fora do ICP.
- Experiencia pos-clique ou onboarding nao sustenta a promessa.

Recomendacoes:

- Revisar campanhas por audiencia, palavra-chave, criativo e landing page.
- Separar campanhas de captura de demanda vs geracao de demanda.
- Criar experimentos A/B de proposta de valor.
- Medir CAC por purchase, nao apenas CPC ou signup.
- Usar listas de exclusao e lookalikes baseadas em compradores.

### 13.3 Melhorar fluxo mobile

Evidencia:

- Mobile representa 62,42% das visitas.
- Visit to purchase mobile: 6,82%.
- Visit to purchase desktop: 13,12%.
- Desktop converte quase 1,9x melhor que mobile.

Hipoteses:

- Formulario de signup longo.
- Checkout pouco amigavel em telas pequenas.
- Performance ruim em mobile.
- Falta de clareza de beneficios antes do signup.
- Usuarios mobile pesquisam, mas finalizam no desktop.

Recomendacoes:

- Auditar funil mobile ponta a ponta.
- Reduzir campos no signup.
- Melhorar velocidade de carregamento.
- Usar login social ou magic link.
- Salvar progresso entre dispositivos.
- Criar retargeting para usuarios mobile que nao concluiram signup ou compra.

### 13.4 Fortalecer organic

Evidencia:

- Maior volume de visitas: 4.271.
- Maior volume absoluto de compras: 459.
- Visit to purchase de 10,75%, acima da media geral.

Recomendacoes:

- Investir em SEO, conteudo e paginas de comparacao.
- Otimizar paginas organicas com melhor conversao.
- Mapear queries que geram usuarios com maior signup to purchase.
- Conectar conteudo a fluxos de signup mais contextualizados.

### 13.5 Explorar email/lifecycle

Evidencia:

- Email tem visit to purchase de 14,17%.
- Signup to purchase de 37,77%.
- Baixo volume: 501 visitas.

Recomendacoes:

- Criar jornadas de nutricao pos-visita e pos-signup.
- Segmentar mensagens por canal de origem, dispositivo e comportamento.
- Testar campanhas de recuperacao para signups sem purchase.
- Personalizar prova de valor por segmento.

### 13.6 Investigar nao compradores com NPS baixo

Evidencia:

- NPS de compradores: 33,33.
- NPS de nao compradores: -29,46.
- Existem 465 respostas de NPS de nao compradores.

Recomendacoes:

- Coletar motivo de nao compra.
- Cruzar NPS baixo com canal, dispositivo e etapa de abandono.
- Criar pesquisa qualitativa com usuarios que deram nota baixa e nao compraram.
- Revisar onboarding para reduzir frustracao antes da compra.

## 14. Hipoteses de teste

### 14.1 Experimentos de produto

| Hipotese                                    | Experimento                               | Metrica primaria       | Metrica secundaria            |
| ------------------------------------------- | ----------------------------------------- | ---------------------- | ----------------------------- |
| Signup mobile tem friccao                   | Reduzir campos ou usar login simplificado | Visit to signup mobile | Qualidade do signup, purchase |
| Usuarios nao percebem valor antes da compra | Onboarding com aha moment mais cedo       | Signup to purchase     | Days to purchase, NPS         |
| Checkout mobile reduz compras               | Checkout simplificado                     | Purchase rate mobile   | Abandono, tempo ate compra    |
| Plano BASIC e porta de entrada              | Destacar BASIC para novos usuarios        | Visit to purchase      | Mix de plano, MRR estimado    |

### 14.2 Experimentos de marketing

| Hipotese                                 | Experimento                         | Metrica primaria         | Metrica secundaria  |
| ---------------------------------------- | ----------------------------------- | ------------------------ | ------------------- |
| Referral traz usuarios mais qualificados | Programa de indicacao com incentivo | Purchases por referral   | CAC, taxa de fraude |
| Paid esta desalinhado                    | Novas landing pages por campanha    | Visit to purchase paid   | Signup quality, NPS |
| Email tem potencial subexplorado         | Jornada de nutricao                 | Signup to purchase email | Descadastro, NPS    |
| Social e topo de funil                   | Campanhas de retargeting            | Assisted conversion      | Purchase direto     |

## 15. Plano de execucao recomendado

### Dia 1 - Entendimento e qualidade

Entregas:

- Leitura do enunciado.
- Profiling do CSV.
- Validacoes de qualidade.
- Dicionario de dados.
- Definicao de metricas.

### Dia 2 - Analise exploratoria

Entregas:

- Funil geral.
- Segmentacao por canal, dispositivo, pais e mes.
- Analise de NPS.
- Analise de tempos de conversao.

### Dia 3 - Modelo e dashboard

Entregas:

- Views analiticas no DuckDB.
- Funcoes de metricas em Python usando SQL local.
- Paginas principais do dashboard Streamlit.
- Graficos Plotly para funil, segmentos, NPS e qualidade.
- Validacao cruzada dos numeros com Python, DuckDB e dashboard.

### Dia 4 - Storytelling e recomendacoes

Entregas:

- Principais achados.
- Gargalos e hipoteses.
- Recomendacoes priorizadas.
- Resumo executivo de ate 2 paginas.

### Dia 5 - Revisao final

Entregas:

- Revisao de consistencia.
- Ajuste visual do dashboard.
- Conferencia de metricas.
- Preparacao do pacote de envio.

## 16. Estrutura de repositorio implementada

```text
desafio-conta-azul/
  app.py
  requirements.txt
  README.md
  Desafio_tecnico_Business_Analytics_(1).pdf
  saas_funnel_case_10k_refresh_(4)_(2).csv
  src/
    __init__.py
    config.py
    data_pipeline.py
    metrics.py
  sql/
    01_create_views.sql
    02_funnel_analysis.sql
    03_nps_analysis.sql
  docs/
    documentacao_tecnica_funcional.md
    guia_celulas_notebook.md
    resumo_executivo.md
  scripts/
    export_summary_docx.py
    export_presentation_script_docx.py
    export_notebook_guide_docx.py
```

Observacao: as validacoes de qualidade estao implementadas em `src/data_pipeline.py` e expostas no dashboard.

### 16.1 Como executar localmente

Instalar dependencias:

```bash
py -3.13 -m pip install -r requirements.txt
```

Executar dashboard:

```bash
py -3.13 -m streamlit run app.py
```

Gerar resumo executivo em Word:

```bash
py -3.13 scripts/export_summary_docx.py
```

Gerar roteiro de apresentacao em Word:

```bash
py -3.13 scripts/export_presentation_script_docx.py
```

Gerar guia do notebook em Word:

```bash
py -3.13 scripts/export_notebook_guide_docx.py
```

URL local do dashboard:

```text
http://localhost:8501
```

### 16.2 Como abrir os documentos Word gerados localmente

Os arquivos `.docx` sao gerados localmente em `output/doc/` pelos scripts da pasta `scripts/`. Eles nao ficam versionados no repositorio, pois sao saidas de processamento que podem ser recriadas a qualquer momento.

Um arquivo `.docx` nao deve ser lido como texto no VS Code. O formato `.docx` e um pacote compactado do Microsoft Word; ao abrir diretamente no editor de texto, o conteudo aparece como caracteres ilegíveis.

Exemplo de arquivo gerado:

```text
output/doc/resumo_executivo_conta_azul.docx
```

Formas recomendadas de abrir:

- Abrir pelo Microsoft Word com duplo clique no Windows Explorer.
- No VS Code, clicar com o botao direito no arquivo e selecionar `Reveal in File Explorer`; depois abrir pelo Word.
- Pelo PowerShell:

```powershell
Start-Process .\output\doc\resumo_executivo_conta_azul.docx
```

Para leitura direta no VS Code, usar a versao Markdown:

```text
docs/resumo_executivo.md
```

### 16.3 Observacao sobre pip no ambiente local

Neste ambiente, o comando `pip install -r requirements.txt` pode apontar para o Python 3.12 em `C:\Python312`, que esta sem o modulo `pip`. Por isso, o comando recomendado no Windows e:

```bash
py -3.13 -m pip install -r requirements.txt
```

## 17. Criterios de aceite

### 17.1 Tecnicos

- O CSV e lido sem erro.
- Os tipos de dados sao tratados corretamente.
- As validacoes criticas passam.
- O numero de usuarios unicos e igual ao numero de linhas.
- As metricas calculadas em Python, DuckDB e Streamlit batem entre si.
- A camada SQL local usa definicoes consistentes e grao unico por usuario.
- As medidas DAX usam `DIVIDE` para evitar erro de divisao por zero.
- Campos tecnicos desnecessarios ficam ocultos no modelo semantico.

### 17.2 Funcionais

- O dashboard responde quais canais convertem melhor.
- O dashboard evidencia o principal gargalo do funil.
- A analise separa compradores e nao compradores no NPS.
- As recomendacoes estao ligadas a evidencias.
- O resumo executivo cabe em ate 2 paginas para submissao.
- As hipoteses sao testaveis e priorizadas.

## 18. Riscos e cuidados

### 18.1 Riscos analiticos

- Confundir correlacao com causalidade.
- Interpretar NPS geral sem segmentar compradores e nao compradores.
- Comparar canais sem considerar volume e incerteza estatistica.
- Tratar taxa de signup como sucesso final, ignorando purchase.
- Avaliar plano mais importante apenas por quantidade, sem receita.
- Ignorar que `days_to_purchase` e contado a partir do signup, nao necessariamente da visita.

### 18.2 Riscos de modelagem

- Criar uma unica tabela larga e depois fazer DAX complexo demais.
- Usar relacionamento bidirecional desnecessario.
- Nao criar calendario.
- Misturar data de visita, signup e compra sem declarar qual data orienta cada analise.
- Expor colunas tecnicas ao usuario final.

### 18.3 Riscos de negocio

- Escalar paid sem corrigir baixa qualidade.
- Concluir que social e ruim sem entender papel de awareness.
- Priorizar apenas canais de maior taxa e ignorar volume absoluto.
- Melhorar conversao de curto prazo reduzindo qualidade de cliente.
- Usar NPS como unica medida de experiencia.

## 19. Priorizacao recomendada

### Matriz impacto vs esforco

| Prioridade | Acao                         | Impacto esperado | Esforco     | Motivo                                    |
| ---------- | ---------------------------- | ---------------- | ----------- | ----------------------------------------- |
| Alta       | Auditar e otimizar mobile    | Alto             | Medio       | Mobile tem maior volume e baixa conversao |
| Alta       | Revisar paid                 | Alto             | Medio       | Alto volume com baixa eficiencia          |
| Alta       | Escalar referral             | Alto             | Medio       | Melhor canal em conversao e NPS           |
| Media      | Expandir email/lifecycle     | Medio            | Baixo/medio | Boa eficiencia e baixo volume             |
| Media      | Fortalecer organic           | Alto             | Medio/alto  | Maior volume e boa conversao              |
| Media      | Pesquisa com nao compradores | Medio            | Baixo       | NPS muito inferior no segmento            |
| Baixa      | Otimizar mix de planos       | Indeterminado    | Medio       | Falta dado de receita/MRR                 |

## 20. Conclusao

A solucao implementada para o desafio e uma abordagem local, reproduzivel e hibrida de Analytics Engineering e BI:

- Usar Python/Pandas para qualidade, tratamento e validacoes.
- Usar DuckDB para SQL local e metricas reproduziveis.
- Usar Plotly e Streamlit para dashboard executivo interativo.
- Usar Word para o resumo executivo exigido pelo desafio.
- Manter documentacao em Markdown para clareza e reproducibilidade.

Os dados indicam que o crescimento mais promissor passa por:

1. Explorar `referral` como canal de alta qualidade.
2. Corrigir a baixa eficiencia de `paid`.
3. Melhorar o funil mobile.
4. Preservar e ampliar `organic`.
5. Usar `email` para nutricao e recuperacao de usuarios.
6. Investigar profundamente a experiencia de nao compradores, onde o NPS e muito mais fraco.

## 21. Status da implementacao local

### 21.1 Artefatos criados

| Artefato | Status | Observacao |
|---|---|---|
| `app.py` | Criado | Dashboard Streamlit com abas de visao geral, segmentos, NPS, qualidade e resposta ao case |
| `src/config.py` | Criado | Configuracoes e caminhos centrais |
| `src/data_pipeline.py` | Criado | Carga, profiling, transformacao, validacao, conexao DuckDB e criacao de views |
| `src/metrics.py` | Criado | Consultas SQL usadas pelo dashboard |
| `sql/01_create_views.sql` | Criado | Views logicas de referencia |
| `sql/02_funnel_analysis.sql` | Criado | Consultas de funil |
| `sql/03_nps_analysis.sql` | Criado | Consultas de NPS |
| `docs/resumo_executivo.md` | Criado | Versao Markdown do resumo executivo |
| `docs/guia_celulas_notebook.md` | Criado | Guia explicando cada celula do notebook de EDA |
| `scripts/export_summary_docx.py` | Criado | Gerador do resumo executivo em Word |
| `scripts/export_presentation_script_docx.py` | Criado | Gerador do roteiro de apresentacao em Word, com textos curtos, bullets e blocos de `Fala sugerida` para explicar o dashboard Streamlit |
| `scripts/export_notebook_guide_docx.py` | Criado | Gerador da versao Word do guia celula a celula do notebook |
| `output/doc/resumo_executivo_conta_azul.docx` | Criado | Resumo executivo em Word, entregavel formal do desafio |
| `output/doc/*.docx` | Gerado localmente | Demais arquivos Word criados pelos scripts; tratados como apoio local e nao versionados no repositorio |
| `notebooks/01_eda_funil_saas.ipynb` | Criado | Notebook de EDA com leitura do CSV, profiling, validacoes, SQL, graficos Plotly e conclusoes |
| `README.md` | Criado | Instrucoes de execucao |
| `requirements.txt` | Criado | Dependencias do projeto |
| `.gitignore` | Criado | Evita envio/versionamento de caches Python, checkpoints Jupyter e arquivos temporarios |
| `.vscode/settings.json` | Criado | Configura o VS Code para usar Python 3.13, reduzir falsos alertas e abrir `.ipynb` como Jupyter Notebook |
| `.streamlit/config.toml` | Criado | Define tema global do Streamlit com cor primaria `#1B69C8` |

### 21.5 Paleta visual aplicada

A paleta dos graficos do notebook foi ajustada para evitar o vermelho padrao do Plotly e aproximar a apresentacao da identidade visual da Conta Azul.

| Uso | Cor |
|---|---|
| Azul principal | `#1B69C8` |
| Azul claro | `#14A7E0` |
| Ciano | `#00B8D9` |
| Verde | `#49C96D` |
| Amarelo de destaque | `#FDB913` |
| Azul escuro | `#0B2F6B` |

No notebook, a paleta fica definida como `CONTA_AZUL_COLORS` e e aplicada aos graficos Plotly.

## 22. Recomendacao de envio oficial

### 22.1 Arquivos recomendados para envio

```text
app.py
requirements.txt
README.md
saas_funnel_case_10k_refresh_(4)_(2).csv
src/
sql/
notebooks/01_eda_funil_saas.ipynb
docs/resumo_executivo.md
docs/documentacao_tecnica_funcional.md
output/doc/resumo_executivo_conta_azul.docx
```

Essa composicao cobre:

- Consultas SQL e views reproduziveis.
- Notebook de investigacao analitica.
- Dashboard Streamlit.
- Resumo executivo em Markdown e Word.
- Documentacao tecnica e instrucoes de execucao.

### 22.2 Arquivos que nao precisam ser enviados

| Arquivo ou pasta | Motivo |
|---|---|
| `Desafio_tecnico_Business_Analytics_(1).pdf` | E o enunciado recebido, nao um artefato produzido |
| `.vscode/` | Configuracao local do VS Code |
| `__pycache__/` | Cache gerado pelo Python |
| `.ipynb_checkpoints/` | Checkpoints automaticos do Jupyter |
| `output/doc/roteiro_apresentacao_conta_azul.docx` | Material pessoal de apoio para apresentacao |
| `output/doc/guia_celulas_notebook.docx` | Material pessoal de apoio para explicar o notebook |
| `docs/guia_celulas_notebook.md` | Material de apoio para explicar o notebook; enviar apenas se quiser documentacao extra |
| Prints, temporarios e copias antigas | Nao agregam valor e podem confundir a avaliacao |

O roteiro de apresentacao e o guia do notebook devem ser usados pelo candidato durante a apresentacao, mas nao sao obrigatorios como entrega formal.

### 21.2 Validacoes executadas

Foram executadas as seguintes validacoes tecnicas:

- Validacao estrutural do notebook com leitura JSON do arquivo `.ipynb`.
- Validacao de dependencia `nbformat`, necessaria para renderizar graficos Plotly no notebook do VS Code.
- Validacao de sintaxe e execucao logica das celulas do notebook, com renderizacao de graficos desativada apenas durante o teste em terminal.
- Compilacao dos arquivos Python com `python -m compileall app.py src scripts`.
- Carga do CSV original.
- Transformacao da base para 10.000 linhas e 18 colunas.
- Validacao das regras criticas de funil e NPS.
- Recalculo das metricas principais via DuckDB.
- Criacao das views analiticas `vw_funnel_*`, `vw_nps_*`, `vw_plan_mix` e `vw_channel_device`.
- Geracao local dos arquivos Word em `output/doc/`.
- Teste HTTP do Streamlit em `http://localhost:8501`, com retorno 200.

### 21.4 Resposta explicita ao resultado esperado do desafio

O dashboard inclui a aba `Resposta ao case`, criada para mostrar ao avaliador como a solucao atende diretamente ao resultado esperado do PDF:

| Capacidade avaliada | Como a solucao responde |
|---|---|
| Entender e investigar o comportamento dos usuarios | Mede o funil completo e segmenta por canal, dispositivo, pais, mes, plano e NPS |
| Identificar gargalos e oportunidades no funil | Evidencia perdas antes do signup, perdas pos-signup, baixa conversao mobile e baixa eficiencia de paid/social |
| Aplicar raciocinio analitico e estatistico | Usa SQL via DuckDB, validacoes de qualidade, comparacao de taxas e segmentacao de NPS |
| Transformar achados em recomendacoes de negocio | Converte os achados em acoes: escalar referral, otimizar paid, melhorar mobile, fortalecer organic, usar email/lifecycle e investigar nao compradores |

Metricas validadas:

| Metrica | Valor |
|---|---:|
| Visitas | 10.000 |
| Signups | 2.983 |
| Compras | 919 |
| Visit to signup | 29,83% |
| Visit to purchase | 9,19% |
| Signup to purchase | 30,81% |
| Respostas NPS | 1.206 |
| NPS medio | 8,11 |

### 21.3 Limitacao de verificacao visual do Word

O arquivo `.docx` foi gerado e validado por leitura textual com `python-docx`. A renderizacao visual automatizada nao foi executada porque o ambiente local nao possui `soffice` nem `pdftoppm` instalados. Recomenda-se abrir o arquivo no Microsoft Word antes do envio final para conferir paginacao, quebras de linha e limite de ate 2 paginas.

Essa combinacao entrega uma resposta aderente ao case, tecnicamente defensavel e orientada a decisao de negocio.

## 23. Revisao final pre-entrega

### 23.1 Ajustes aplicados

- README reestruturado como documentacao oficial do projeto, com foco em objetivo, stack, arquitetura, execucao, dashboard, SQL, qualidade e documentacao.
- Removidas do README as orientacoes pessoais de envio/nao envio para manter o arquivo com aparencia profissional.
- Guia celula a celula do notebook restaurado em `docs/guia_celulas_notebook.md`, mantendo o script `scripts/export_notebook_guide_docx.py` funcional.
- Arquivo `.gitignore` criado para evitar caches Python, checkpoints Jupyter e arquivos temporarios.
- Resumo executivo em Word mantido no versionamento como entregavel formal; documentos Word de apoio seguem ignorados no Git.
- Repositorio GitHub criado em `https://github.com/DiegoPablo2021/desafio-conta-azul`.
- Dependencias travadas em `requirements.txt` para reduzir risco de quebra no deploy.
- Geradores Word ajustados para padronizar a fonte Calibri nos documentos criados localmente.
- Guia celula a celula atualizado com explicacoes adicionais sobre base original vs base tratada, profiling categorico, grafico por dispositivo, grafico mensal e NPS.
- Guia do notebook simplificado para funcionar como cola de apresentacao, omitindo celulas Markdown que ja sao autoexplicativas e removendo marcadores de tipo de celula.

### 23.2 Validacoes finais executadas

| Validacao | Resultado |
|---|---|
| Compilacao Python com `py -3.13 -m compileall app.py src scripts` | OK |
| Carga do CSV original | OK |
| Transformacao da base | OK, 10.000 linhas |
| Metricas principais do funil | OK, 10.000 visitas, 2.983 signups, 919 compras |
| Validacoes criticas de qualidade | OK, zero inconsistencias criticas |
| Validacao estrutural do notebook | OK, 37 celulas |
| Geracao do resumo executivo Word | OK |
| Geracao do roteiro de apresentacao Word | OK |
| Geracao do guia do notebook Word | OK |
| Teste HTTP do Streamlit em `http://localhost:8501` | OK, status 200 |

### 23.3 Status final

O projeto esta pronto para demonstracao local. A solucao cobre os entregaveis do desafio com notebook, SQL, dashboard, resumo executivo, documentacao tecnica e validacoes reproduziveis.

### 23.4 Configuracao para deploy Streamlit

Configuracao recomendada no Streamlit Community Cloud:

| Campo | Valor |
|---|---|
| Repository | `DiegoPablo2021/desafio-conta-azul` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | `3.12` ou superior |

O app nao depende de secrets. A base CSV necessaria para o dashboard esta versionada no repositorio e as dependencias estao no arquivo `requirements.txt`.
