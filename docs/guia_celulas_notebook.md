# Guia de apoio - Notebook `01_eda_funil_saas.ipynb`

Use este guia como uma cola de apresentacao. A ideia e explicar os resultados principais do notebook sem ler cada celula palavra por palavra.

Fala de abertura sugerida:

> Este notebook mostra a parte investigativa da analise. O dashboard traz a leitura executiva, mas aqui eu mostro como os dados foram carregados, validados, transformados e analisados antes de chegar nas recomendacoes.

## Pontos que podem gerar duvida

### Quando aparecer `WindowsPath(...)`

`WindowsPath(...)` e apenas o caminho local do CSV no Windows.

Fala sugerida:

> Esse retorno nao e erro. Ele apenas confirma o caminho do arquivo CSV usado na analise.

### Quando aparecer `(10000, 12)`

Esse resultado vem de `raw.shape` e representa:

- `10000`: linhas da base original.
- `12`: colunas originais do CSV.

Fala sugerida:

> Aqui eu confirmo que o CSV original tem 10.000 linhas e 12 colunas, exatamente a volumetria esperada para o desafio.

### Quando o profiling mostrar `colunas = 17`

O CSV original tem 12 colunas. Depois do tratamento, a base analitica ganha campos derivados:

- `visit_month`
- `signup_date`
- `purchase_date`
- `funnel_stage`
- `nps_class`

Fala sugerida:

> A diferenca e intencional: 12 colunas e o formato original do CSV; 17 colunas e a base ja preparada para analise, com campos derivados de data, funil e NPS.

### Quando aparecer `NaN`

`NaN` significa valor ausente ou nao aplicavel.

No funil, isso e esperado:

- quem nao fez signup nao tem `days_to_signup`;
- quem nao comprou nao tem `plan`;
- quem nao comprou nao tem `days_to_purchase`;
- quem nao respondeu NPS nao tem `nps_score`.

Fala sugerida:

> Esses nulos nao indicam erro por si so. Eles refletem a regra do funil: se o usuario nao avancou para uma etapa, alguns campos ficam naturalmente vazios.

## Celula 2 - Imports, caminhos e configuracao visual

Esta celula prepara o ambiente do notebook:

- importa as bibliotecas;
- identifica a raiz do projeto;
- aponta para o CSV;
- configura as cores inspiradas na Conta Azul;
- define o renderer dos graficos Plotly para o VS Code.

Fala sugerida:

> Aqui preparo o ambiente para deixar a analise reproduzivel. O notebook encontra o CSV, carrega as bibliotecas e configura a identidade visual dos graficos.

## Celula 4 - Leitura e amostra inicial

Esta celula le o CSV com Pandas e mostra as primeiras linhas.

Ela ajuda a confirmar:

- se o arquivo foi carregado;
- quais sao as colunas originais;
- como os dados aparecem antes de qualquer tratamento.

Fala sugerida:

> Primeiro eu leio o CSV e olho uma amostra da base para entender a estrutura original: usuario, data da visita, canal, dispositivo, pais, signup, compra, plano, tempos e NPS.

## Celula 5 - Dimensao da base original

Mostra o tamanho do CSV original.

Resultado:

- `linhas = 10000`
- `colunas = 12`

Fala sugerida:

> Aqui valido a volumetria original: 10.000 linhas e 12 colunas. Isso confirma que estou analisando a base completa do case.

## Celula 7 - Tratamento e campos derivados

Esta celula cria a base analitica `df`.

Principais tratamentos:

- converte `dt_visit` para data;
- ajusta tipos numericos;
- cria `visit_month`;
- cria datas estimadas de signup e compra;
- cria a etapa final do funil;
- classifica o NPS como promotor, passivo ou detrator.

Fala sugerida:

> Aqui eu transformo o CSV original em uma base analitica. A ideia nao e alterar o dado bruto, mas criar campos que facilitem as analises de funil, tempo e NPS.

## Celula 9 - Profiling da base tratada

Esta tabela resume a base depois do tratamento.

Resultado esperado:

- `linhas = 10000`
- `colunas = 17`
- `usuarios_unicos = 10000`
- `usuarios_duplicados = 0`
- `data_minima_visita = 2025-06-01`
- `data_maxima_visita = 2025-10-30`
- `canais = 5`
- `dispositivos = 2`
- `paises = 5`
- `planos = 3`

Fala sugerida:

> Essa tabela mostra que a base esta consistente: tenho 10.000 usuarios unicos, sem duplicidade, cobrindo visitas de junho a outubro de 2025. As 17 colunas aparecem porque a base ja esta tratada e enriquecida com campos derivados.

## Celula 10 - Perfil das categorias

Codigo da celula:

```python
df[['channel', 'device', 'country', 'plan']].describe(include='all')
```

Como ler a tabela:

- `count`: quantidade de valores preenchidos.
- `unique`: quantidade de categorias diferentes.
- `top`: categoria mais frequente.
- `freq`: quantidade de vezes em que a categoria mais frequente aparece.

Resultado principal:

- `channel`: canal mais frequente e `organic`, com 4.271 usuarios.
- `device`: dispositivo mais frequente e `mobile`, com 6.242 usuarios.
- `country`: pais mais frequente e `BR`, com 6.986 usuarios.
- `plan`: plano mais frequente e `BASIC`, com 526 compradores.

Ponto importante:

`plan` tem `count = 919`, e nao 10.000, porque plano so existe para quem comprou.

Fala sugerida:

> Esta tabela mostra o mix da base. Organic e o canal mais comum, mobile e o dispositivo mais frequente, BR concentra a maior parte dos usuarios e BASIC e o plano mais comprado. O plano aparece em apenas 919 linhas porque so usuarios compradores possuem plano.

## Celula 12 - Validacoes de qualidade

Esta celula valida se as regras principais do funil fazem sentido.

Ela verifica, por exemplo:

- compra sem signup;
- compra sem plano;
- plano sem compra;
- NPS fora do intervalo;
- datas ou tempos inconsistentes;
- usuarios duplicados.

Fala sugerida:

> Antes de tirar conclusoes, eu valido a qualidade dos dados. As regras criticas deram zero inconsistencias, entao as metricas do funil estao confiaveis.

## Celula 14 - DuckDB e views analiticas

Aqui a base tratada e registrada no DuckDB como `stg_funnel_users`.

Depois disso, o notebook executa `sql/01_create_views.sql` para criar views analiticas.

Fala sugerida:

> Aqui eu trago SQL para a analise. Em vez de calcular tudo manualmente no notebook, registro a base no DuckDB e crio views reproduziveis para funil, segmentos, planos e NPS.

## Celula 16 - Funil geral

Consulta a view `vw_funnel_overall`.

Principais resultados:

- visitas: 10.000;
- signups: 2.983;
- compras: 919;
- visit to signup: 29,83%;
- visit to purchase: 9,19%;
- signup to purchase: 30,81%.

Fala sugerida:

> Aqui esta o resumo do funil. De 10.000 visitantes, 2.983 criaram conta e 919 compraram. A conversao final sobre visitas foi de 9,19%.

## Celula 17 - Grafico de funil

Mostra visualmente a queda entre:

- visitas;
- signups;
- compras.

Fala sugerida:

> O grafico deixa claro que existe uma perda grande antes do signup e outra perda relevante depois do signup.

## Celula 20 - Analise por canal

Compara volume e eficiencia por canal.

Leituras principais:

- `referral` tem melhor eficiencia;
- `email` tambem performa bem;
- `organic` combina volume e conversao;
- `paid` e `social` precisam de otimizacao.

Fala sugerida:

> Aqui eu nao olho so volume. Eu comparo tambem eficiencia. Referral nao e o maior canal em volume, mas e o melhor em conversao.

## Celula 21 - Grafico por canal

Mostra a taxa `visit_to_purchase_rate` por canal.

Fala sugerida:

> Este grafico ajuda a enxergar quais canais transformam visita em compra com mais eficiencia. Referral aparece como destaque positivo, enquanto paid e social merecem investigacao.

## Celula 24 - Consulta por dispositivo

Compara desktop e mobile.

Ponto principal:

- mobile tem mais volume;
- desktop tem melhores taxas de conversao.

Fala sugerida:

> Aqui aparece uma diferenca importante entre volume e eficiencia. Mobile concentra mais usuarios, mas desktop converte melhor.

## Celula 25 - Grafico de taxas por dispositivo

As barras representam taxas, nao volume absoluto.

Desktop aparece melhor nas tres taxas:

- visita para signup;
- visita para compra;
- signup para compra.

Mesmo assim, mobile e importante porque concentra mais visitas.

Fala sugerida:

> O grafico mostra que desktop converte melhor em todas as taxas. A oportunidade esta em mobile porque ele tem muito volume; se a conversao mobile melhorar um pouco, o impacto absoluto pode ser relevante.

## Celula 28 - Analise por pais

Compara a performance por pais.

Leitura principal:

- BR concentra a maior parte da base;
- as taxas entre paises sao relativamente proximas;
- nao ha um pais com desvio extremo que mude toda a leitura do funil.

Fala sugerida:

> Aqui eu verifico se algum pais foge muito do padrao. O Brasil concentra o maior volume, mas as taxas entre paises ficam relativamente proximas.

## Celula 29 - Tabela mensal

Mostra a evolucao mensal das metricas do funil.

Fala sugerida:

> Esta tabela ajuda a entender se houve mudanca de comportamento ao longo do tempo, como efeito de campanha, sazonalidade ou melhoria de produto.

## Celula 30 - Grafico mensal

Mostra a evolucao das taxas ao longo dos meses.

Leitura principal:

- setembro apresenta a melhor taxa de compra sobre visitas;
- setembro tambem tem a melhor conversao pos-signup.

Fala sugerida:

> No grafico mensal, setembro aparece como o melhor mes em conversao para compra e conversao pos-signup. Aqui o foco e a variacao ao longo do tempo, nao a comparacao por pais.

## Celula 33 - NPS geral e por segmento

A tabela mostra:

- `respostas`: quantidade de usuarios que responderam NPS;
- `nps_medio`: media da nota NPS de 0 a 10;
- `promotores`: numero real de respostas com nota maior ou igual a 9;
- `passivos`: numero real de respostas com nota entre 7 e menor que 9;
- `detratores`: numero real de respostas com nota menor que 7;
- `nps`: indicador calculado como percentual de promotores menos percentual de detratores.

Ponto importante:

`promotores`, `passivos` e `detratores` sao contagens absolutas. O campo `nps` e o indicador percentual consolidado, em escala de -100 a 100.

Fala sugerida:

> Aqui eu separo compradores e nao compradores. Isso e importante porque o NPS geral pode esconder experiencias muito diferentes.

## Celula 34 - Grafico de NPS por segmento

Mostra a diferenca entre:

- compradores;
- nao compradores;
- geral.

Fala sugerida:

> O grafico mostra que compradores avaliam melhor, enquanto nao compradores tem NPS negativo. Isso sugere friccao ou baixa percepcao de valor antes da compra.

## Celula 35 - NPS por canal

Compara satisfacao por origem do usuario.

Fala sugerida:

> Aqui eu vejo se os canais que convertem melhor tambem trazem usuarios mais satisfeitos. Referral aparece bem tambem em NPS, reforcando que e um canal de maior qualidade.

## Celula 37 - Conclusoes

Principais conclusoes:

- o funil tem gargalo antes do signup;
- tambem existe perda relevante depois do signup;
- referral e o canal de melhor qualidade;
- paid e social precisam de otimizacao;
- mobile e oportunidade por volume;
- NPS deve ser lido separando compradores e nao compradores.

Fala sugerida:

> No final, conecto os achados as recomendacoes: escalar referral, otimizar paid, melhorar mobile, fortalecer organic, trabalhar email/lifecycle e investigar nao compradores com NPS baixo.
