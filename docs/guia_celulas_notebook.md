# Guia celula a celula - Notebook `01_eda_funil_saas.ipynb`

Este guia explica o papel de cada celula do notebook de EDA criado para o desafio Conta Azul.

## Como usar este guia na apresentacao

Use este documento como apoio de fala. A ideia nao e ler tudo palavra por palavra, mas ter uma explicacao curta para cada bloco do notebook.

Fala de abertura sugerida:

> Este notebook mostra a parte investigativa da analise. O dashboard traz a leitura executiva, mas aqui eu mostro como os dados foram carregados, validados, transformados e analisados antes de chegar nas recomendacoes.

## Falas prontas para pontos que podem gerar duvida

### Quando aparecer `WindowsPath(...)`

O que significa:

`WindowsPath('C:/Projetos/desafio-conta-azul/saas_funnel_case_10k_refresh_(4)_(2).csv')` e apenas o caminho local do arquivo CSV no Windows.

Fala sugerida:

> Essa primeira celula configura o ambiente do notebook e confirma qual arquivo CSV sera usado na analise. O retorno `WindowsPath` nao e erro; ele apenas mostra o caminho local do arquivo no Windows.

### Quando aparecer `(10000, 12)`

O que significa:

Esse resultado vem de `raw.shape`. Em Pandas, `shape` retorna `(linhas, colunas)`.

Fala sugerida:

> Aqui eu confiro a volumetria original da base. O resultado `(10000, 12)` significa que o CSV tem 10.000 linhas e 12 colunas, exatamente o esperado pelo enunciado do desafio.

### Quando aparecer `NaN`

O que significa:

`NaN` representa valor ausente ou nao aplicavel. No funil, isso e esperado quando o usuario nao avancou para determinada etapa.

Fala sugerida:

> Esses `NaN` nao indicam necessariamente erro. Por exemplo, se o usuario visitou mas nao fez signup, nao existe `days_to_signup`. Se nao comprou, nao existe plano nem `days_to_purchase`. Entao esses nulos sao esperados pela regra de negocio e foram validados antes das analises.

### Quando explicar as views DuckDB

Fala sugerida:

> Depois do tratamento em Pandas, eu registro a base tratada no DuckDB como `stg_funnel_users` e crio views analiticas. Isso deixa as metricas reproduziveis em SQL, evitando calculos manuais espalhados pelo notebook ou pelo dashboard.

### Quando explicar por que separar NPS de compradores e nao compradores

Fala sugerida:

> Eu separei o NPS entre compradores e nao compradores porque a media geral poderia esconder comportamentos diferentes. Compradores tem NPS bem mais positivo, enquanto nao compradores tem NPS negativo, o que sugere friccao ou desalinhamento de valor antes da compra.

## Celula 1 - Introducao do notebook

Tipo: Markdown

Explica o objetivo do notebook: demonstrar a investigacao analitica antes do dashboard, cobrindo leitura do CSV, profiling, validacoes, funil, segmentos, NPS, graficos e conclusoes.

Fala sugerida:

> Comeco o notebook deixando claro que ele e a trilha de investigacao. Ele nao substitui o dashboard; ele mostra o raciocinio usado para chegar nos achados.

## Celula 2 - Imports, caminhos e configuracao visual

Tipo: Codigo

Importa bibliotecas principais (`Path`, `sys`, `duckdb`, `pandas`, `plotly.express`, `plotly.io`), define o caminho raiz do projeto, localiza o CSV original e configura a paleta visual `CONTA_AZUL_COLORS`, inspirada nas cores da Conta Azul. Tambem define o renderer `vscode` para os graficos Plotly aparecerem dentro do VS Code.

Fala sugerida:

> Aqui preparo o ambiente: importo as bibliotecas, encontro automaticamente a raiz do projeto, aponto para o CSV e configuro a paleta visual inspirada na Conta Azul. Assim o notebook fica reproduzivel mesmo se eu abrir pela pasta raiz ou pela pasta `notebooks`.

## Celula 3 - Secao de leitura do CSV

Tipo: Markdown

Abre a primeira etapa analitica: leitura do arquivo CSV com Pandas.

Fala sugerida:

> A partir daqui comeco a trabalhar com a base original do case.

## Celula 4 - Leitura e amostra inicial

Tipo: Codigo

Le o arquivo `saas_funnel_case_10k_refresh_(4)_(2).csv` com `pd.read_csv()` e mostra as primeiras linhas com `head()`. Serve para confirmar que o arquivo foi carregado e visualizar as colunas originais.

Fala sugerida:

> Primeiro leio o CSV e olho as primeiras linhas para entender a estrutura original: identificador do usuario, data da visita, canal, dispositivo, pais, signup, purchase, plano, tempos e NPS.

## Celula 5 - Dimensao da base

Tipo: Codigo

Mostra o tamanho da base com `raw.shape`. A expectativa do desafio e uma base de 10.000 linhas.

Fala sugerida:

> Aqui confirmo que a base tem 10.000 linhas e 12 colunas. Isso valida que estou trabalhando com a volumetria esperada do enunciado.

## Celula 6 - Secao de tratamento inicial

Tipo: Markdown

Explica que a base tem grao de uma linha por usuario e que serao criados campos derivados para facilitar analise de funil, datas e NPS.

Fala sugerida:

> Antes de calcular metricas, declaro o grao da base: uma linha por usuario visitante. Isso e importante para nao misturar contagem de usuarios com eventos.

## Celula 7 - Tratamento, tipagem e campos derivados

Tipo: Codigo

Cria uma copia da base original, converte `dt_visit` para data, ajusta campos numericos nullable, cria `visit_month`, `signup_date`, `purchase_date`, `funnel_stage` e `nps_class`. Essa celula prepara a base para analise sem alterar o CSV original.

Fala sugerida:

> Aqui eu preparo a base analitica. Converto datas, trato campos numericos e crio variaveis derivadas para facilitar a leitura do funil e do NPS. A base original permanece preservada.

## Celula 8 - Secao de profiling

Tipo: Markdown

Inicia a etapa de profiling da base.

Fala sugerida:

> Depois da preparacao, faco um profiling para entender volume, periodo e cardinalidade dos principais campos.

## Celula 9 - Tabela de profiling

Tipo: Codigo

Cria uma tabela resumo com quantidade de linhas, colunas, usuarios unicos, duplicidades, periodo de visitas, quantidade de canais, dispositivos, paises e planos. Serve para validar a volumetria e o escopo da base.

Fala sugerida:

> Essa tabela confirma que tenho 10.000 usuarios unicos, sem duplicidade de `user_id`, cobrindo visitas de junho a outubro de 2025.

## Celula 10 - Perfil das categorias

Tipo: Codigo

Usa `describe(include='all')` para resumir as colunas categoricas principais: `channel`, `device`, `country` e `plan`. Ajuda a entender distribuicoes, categorias mais frequentes e valores ausentes.

Fala sugerida:

> Aqui eu olho os campos categoricos para entender quais canais, dispositivos, paises e planos existem, alem de verificar valores ausentes esperados, como plano nulo para quem nao comprou.

## Celula 11 - Secao de validacoes de qualidade

Tipo: Markdown

Introduz as regras de qualidade usadas para garantir que o funil nao tenha inconsistencias basicas.

## Celula 12 - Validacoes de consistencia

Tipo: Codigo

Cria uma tabela de checks para identificar problemas como compra sem signup, compra sem plano, plano sem compra, dias preenchidos indevidamente, NPS preenchido sem resposta, NPS fora do intervalo e respostas de NPS de nao compradores. Mostra que a base e confiavel para analise.

Fala sugerida:

> Antes de tirar conclusoes, valido regras criticas do funil. O objetivo e garantir que nao existem compras sem signup, compras sem plano ou NPS fora do intervalo. Isso aumenta a confianca nas metricas.

## Celula 13 - Secao DuckDB e SQL

Tipo: Markdown

Explica que, a partir dali, o notebook usa DuckDB para calcular metricas em SQL local.

Fala sugerida:

> Nesta etapa eu trago SQL para a analise. O DuckDB permite executar consultas localmente, sem precisar de BigQuery, Snowflake ou outro ambiente externo.

## Celula 14 - Conexao DuckDB e criacao das views

Tipo: Codigo

Cria uma conexao DuckDB em memoria, registra o dataframe tratado como `stg_funnel_users`, executa `sql/01_create_views.sql` e lista as views criadas. Essa celula conecta Pandas e SQL.

Fala sugerida:

> Aqui a base tratada vira uma staging no DuckDB. Em seguida eu crio views analiticas para funil, canais, dispositivos, paises, meses, planos e NPS. Isso deixa as consultas reproduziveis.

## Celula 15 - Secao de funil geral

Tipo: Markdown

Abre a analise do funil geral.

## Celula 16 - Consulta do funil geral

Tipo: Codigo

Consulta `vw_funnel_overall` para trazer visitas, signups, compras, respostas de NPS e taxas principais. Essa e a tabela base para entender a performance geral.

Fala sugerida:

> Aqui calculo o funil geral. Essa tabela resume quantos usuarios visitaram, quantos fizeram signup, quantos compraram e quais sao as taxas principais de conversao.

## Celula 17 - Grafico de funil

Tipo: Codigo

Monta um dataframe com as etapas `Visitas`, `Signups` e `Compras`, e gera um grafico de funil com Plotly. Mostra visualmente a queda entre as etapas.

Fala sugerida:

> O grafico de funil ajuda a visualizar rapidamente onde ocorre a maior perda. Ele deixa claro que a queda de visita para signup e muito forte.

## Celula 18 - Leitura do funil geral

Tipo: Markdown

Interpreta o funil: 10.000 visitas, 2.983 signups e 919 compras, destacando que os principais gargalos estao antes do signup e depois do signup.

## Celula 19 - Secao de analise por canal

Tipo: Markdown

Abre a investigacao por canal de origem.

## Celula 20 - Consulta por canal

Tipo: Codigo

Consulta `vw_funnel_by_channel`, ordenando por taxa de compra sobre visitas. Permite comparar volume e eficiencia entre `organic`, `paid`, `referral`, `social` e `email`.

Fala sugerida:

> Aqui eu comparo os canais nao apenas por volume, mas por eficiencia. Isso e importante porque um canal pode trazer muito trafego e ainda assim converter mal.

## Celula 21 - Grafico por canal

Tipo: Codigo

Cria um grafico de barras horizontais para comparar `visit_to_purchase_rate` por canal. Ajuda a evidenciar que `referral` e `email` sao mais eficientes e `paid/social` menos eficientes.

Fala sugerida:

> Este grafico mostra que referral e email sao os canais com maior eficiencia de compra, enquanto paid e social precisam de investigacao antes de escalar investimento.

## Celula 22 - Leitura por canal

Tipo: Markdown

Interpreta os canais: `referral` e `email` sao mais eficientes, `organic` combina escala e conversao, e `paid/social` precisam de otimizacao.

## Celula 23 - Secao de analise por dispositivo

Tipo: Markdown

Abre a investigacao por dispositivo.

## Celula 24 - Consulta por dispositivo

Tipo: Codigo

Consulta `vw_funnel_by_device`, trazendo taxas por `desktop` e `mobile`. Mostra a diferenca de eficiencia entre os dispositivos.

Fala sugerida:

> Nesta consulta eu vejo a diferenca entre desktop e mobile. O ponto importante e que mobile tem muito volume, mas converte pior.

## Celula 25 - Grafico por dispositivo

Tipo: Codigo

Gera um grafico de barras agrupadas com `visit_to_signup_rate`, `visit_to_purchase_rate` e `signup_to_purchase_rate` para desktop e mobile. A paleta evita o vermelho padrao e usa cores da Conta Azul.

Fala sugerida:

> Esse grafico reforca a oportunidade em mobile. Como mobile representa grande parte das visitas, pequenas melhorias na jornada podem gerar impacto relevante.

## Celula 26 - Leitura por dispositivo

Tipo: Markdown

Interpreta que desktop converte melhor que mobile e que, como mobile tem alto volume, melhorar essa experiencia pode gerar impacto relevante.

## Celula 27 - Secao de pais e mes

Tipo: Markdown

Abre a analise geografica e temporal.

## Celula 28 - Consulta por pais

Tipo: Codigo

Consulta `vw_funnel_by_country`, ordenando por volume de visitas. Permite avaliar se algum pais tem comportamento muito diferente.

Fala sugerida:

> Aqui verifico se existe algum pais com comportamento muito diferente. A maior parte da base esta no Brasil, mas tambem olho outros paises para identificar possiveis desvios.

## Celula 29 - Consulta mensal

Tipo: Codigo

Consulta `vw_funnel_by_month`, trazendo a evolucao mensal das taxas do funil.

Fala sugerida:

> Aqui olho a evolucao mensal para entender se a conversao mudou ao longo do tempo, o que poderia indicar efeito de campanha, sazonalidade ou mudanca no produto.

## Celula 30 - Grafico mensal

Tipo: Codigo

Gera um grafico de linhas com as taxas de conversao ao longo dos meses. Ajuda a identificar meses com melhor ou pior performance.

Fala sugerida:

> O grafico mensal mostra que setembro foi um periodo mais forte em conversao para compra e conversao pos-signup.

## Celula 31 - Leitura por pais e mes

Tipo: Markdown

Interpreta que as taxas por pais sao proximas e que setembro se destaca em taxa de compra sobre visitas e conversao pos-signup.

## Celula 32 - Secao de NPS

Tipo: Markdown

Abre a analise de satisfacao/NPS.

## Celula 33 - Consulta de NPS geral e por segmento

Tipo: Codigo

Consulta `vw_nps_summary` e adiciona uma linha geral. Calcula respostas, NPS medio, promotores, passivos, detratores e NPS para compradores, nao compradores e geral.

Fala sugerida:

> Aqui separo NPS por compradores e nao compradores. Essa separacao e essencial porque a media geral pode esconder experiencias muito diferentes.

## Celula 34 - Grafico de NPS por segmento

Tipo: Codigo

Gera um grafico de barras para comparar NPS geral, compradores e nao compradores. Mostra que a media geral mascara diferencas relevantes.

Fala sugerida:

> Esse grafico mostra a diferenca de percepcao: compradores avaliam melhor, enquanto nao compradores tem NPS negativo. Isso aponta para friccao ou baixa percepcao de valor antes da compra.

## Celula 35 - Consulta de NPS por canal

Tipo: Codigo

Consulta `vw_nps_by_channel`, ordenando os canais por NPS. Permite comparar satisfacao por origem do usuario.

Fala sugerida:

> Aqui comparo a satisfacao por canal. A ideia e entender se canais com melhor conversao tambem trazem usuarios mais satisfeitos.

## Celula 36 - Leitura de NPS

Tipo: Markdown

Interpreta que compradores possuem NPS positivo e nao compradores possuem NPS negativo, sugerindo friccao ou desalinhamento de valor antes da compra.

## Celula 37 - Conclusoes antes do dashboard

Tipo: Markdown

Consolida os principais achados do notebook: gargalos do funil, qualidade de referral, necessidade de otimizar paid, oportunidade em mobile, importancia de organic, cuidado com NPS geral e recomendacoes de negocio.

Fala sugerida:

> No final, eu conecto os achados as recomendacoes: escalar referral, otimizar paid, melhorar mobile, fortalecer organic, trabalhar email/lifecycle e investigar nao compradores com NPS baixo.
