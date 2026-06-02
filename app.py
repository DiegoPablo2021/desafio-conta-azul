from __future__ import annotations

import plotly.express as px
import pandas as pd
import streamlit as st

from src.data_pipeline import create_connection, load_validated_connection, profile_data, validate_data
from src.metrics import (
    get_channel_device_matrix,
    get_funnel_steps,
    get_nps_eligibility,
    get_nps_by_channel,
    get_nps_non_eligible_breakdown,
    get_nps_non_eligible_combinations,
    get_nps_summary,
    get_overall_funnel,
    get_segment_funnel,
)


PRIMARY_COLOR = "#1B69C8"


def apply_custom_styles() -> None:
    st.markdown(
        f"""
        <style>
            div[data-baseweb="tag"] {{
                background-color: {PRIMARY_COLOR} !important;
                border-color: {PRIMARY_COLOR} !important;
            }}

            div[data-baseweb="tag"] span {{
                color: #FFFFFF !important;
                font-weight: 600 !important;
            }}

            div[data-baseweb="tag"] svg {{
                color: #FFFFFF !important;
                fill: #FFFFFF !important;
            }}

            .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                color: {PRIMARY_COLOR} !important;
            }}

            .stTabs [data-baseweb="tab-highlight"] {{
                background-color: {PRIMARY_COLOR} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Desafio Conta Azul - Business Analytics",
    layout="wide",
)
apply_custom_styles()


@st.cache_data(show_spinner=False)
def load_data():
    df, validations, _ = load_validated_connection()
    return df, validations


def fmt_pct(value: float) -> str:
    return f"{value:.2%}".replace(".", ",")


def fmt_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def build_filtered_connection(df):
    return create_connection(df)


df, validation_df = load_data()

st.title("Desafio Conta Azul - Business Analytics")
st.caption("Dashboard local em Streamlit com metricas calculadas em SQL via DuckDB.")

with st.sidebar:
    st.header("Filtros")
    months = sorted(df["visit_month"].dropna().unique().tolist())
    channels = sorted(df["channel"].dropna().unique().tolist())
    devices = sorted(df["device"].dropna().unique().tolist())
    countries = sorted(df["country"].dropna().unique().tolist())

    selected_months = st.multiselect("Mes da visita", months, default=months)
    selected_channels = st.multiselect("Canal", channels, default=channels)
    selected_devices = st.multiselect("Dispositivo", devices, default=devices)
    selected_countries = st.multiselect("Pais", countries, default=countries)

filtered = df[
    df["visit_month"].isin(selected_months)
    & df["channel"].isin(selected_channels)
    & df["device"].isin(selected_devices)
    & df["country"].isin(selected_countries)
].copy()

if filtered.empty:
    st.warning("Nenhum registro encontrado para a combinacao de filtros selecionada.")
    st.stop()

con = build_filtered_connection(filtered)
overall = get_overall_funnel(con).iloc[0]

tab_overview, tab_segments, tab_nps, tab_quality, tab_response = st.tabs(
    ["Visao geral", "Segmentos", "NPS", "Qualidade dos dados", "Resposta ao case"]
)

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Visitas", fmt_number(overall["visits"]))
    c2.metric("Signups", fmt_number(overall["signups"]), fmt_pct(overall["visit_to_signup_rate"]))
    c3.metric("Compras", fmt_number(overall["purchases"]), fmt_pct(overall["visit_to_purchase_rate"]))
    c4.metric("Signup -> compra", fmt_pct(overall["signup_to_purchase_rate"]))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Respostas NPS compradores", fmt_number(overall["nps_responses"]), fmt_pct(overall["nps_response_rate"]))
    c6.metric("NPS medio", f"{overall['avg_nps_score']:.2f}".replace(".", ","))
    c7.metric("Drop-off visita -> signup", fmt_pct(1 - overall["visit_to_signup_rate"]))
    c8.metric("Drop-off signup -> compra", fmt_pct(1 - overall["signup_to_purchase_rate"]))

    funnel_steps = get_funnel_steps(con)
    monthly = get_segment_funnel(con, "visit_month").sort_values("segmento")

    left, right = st.columns([1, 1])
    with left:
        fig = px.funnel(
            funnel_steps,
            x="usuarios",
            y="etapa",
            title="Funil de conversao",
            color="etapa",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.line(
            monthly,
            x="segmento",
            y=["visit_to_signup_rate", "visit_to_purchase_rate", "signup_to_purchase_rate"],
            markers=True,
            title="Evolucao mensal das taxas",
            labels={"segmento": "Mes", "value": "Taxa", "variable": "Metrica"},
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Leitura executiva")
    st.markdown(
        """
        - O maior gargalo absoluto esta antes do signup: cerca de 70% dos visitantes nao criam conta.
        - A perda pos-signup tambem e relevante: aproximadamente 69% dos signups nao viram compra.
        - A analise por canal e dispositivo mostra onde priorizar experimentos de crescimento e UX.
        """
    )

with tab_segments:
    channel = get_segment_funnel(con, "channel")
    device = get_segment_funnel(con, "device")
    country = get_segment_funnel(con, "country")
    plan = get_segment_funnel(con, "plan")
    channel_device = get_channel_device_matrix(con)

    st.subheader("Performance por canal")
    fig = px.bar(
        channel.sort_values("visit_to_purchase_rate"),
        x="visit_to_purchase_rate",
        y="segmento",
        orientation="h",
        text="purchases",
        title="Taxa visit to purchase por canal",
        labels={"visit_to_purchase_rate": "Visit to purchase", "segmento": "Canal"},
    )
    fig.update_xaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(channel, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            device,
            x="segmento",
            y=["visit_to_signup_rate", "visit_to_purchase_rate", "signup_to_purchase_rate"],
            barmode="group",
            title="Conversao por dispositivo",
            labels={"segmento": "Dispositivo", "value": "Taxa", "variable": "Metrica"},
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        pivot = channel_device.pivot(index="channel", columns="device", values="visit_to_purchase_rate")
        fig = px.imshow(
            pivot,
            color_continuous_scale="Blues",
            title="Heatmap visit to purchase - canal x dispositivo",
            labels={"color": "Taxa"},
        )
        fig.update_traces(texttemplate="%{z:.1%}", text=pivot.values)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Performance por pais")
        st.dataframe(country, use_container_width=True, hide_index=True)
    with c2:
        st.subheader("Mix por plano")
        st.dataframe(plan, use_container_width=True, hide_index=True)

with tab_nps:
    nps_summary = get_nps_summary(con)
    nps_eligibility = get_nps_eligibility(con).iloc[0]
    nps_channel = get_nps_by_channel(con)
    non_eligible_channel = get_nps_non_eligible_breakdown(con, "channel")
    non_eligible_device = get_nps_non_eligible_breakdown(con, "device")
    non_eligible_country = get_nps_non_eligible_breakdown(con, "country")
    non_eligible_signup = get_nps_non_eligible_breakdown(con, "signup_status")
    non_eligible_class = get_nps_non_eligible_breakdown(con, "nps_class")
    non_eligible_combinations = get_nps_non_eligible_combinations(con)

    st.subheader("NPS - compradores elegiveis")
    st.markdown(
        """
        Nesta leitura, NPS e considerado uma pesquisa pos-compra. Por isso, o indicador
        e calculado apenas para usuarios que compraram.
        """
    )
    if nps_eligibility["respostas_nps_nao_elegiveis"] > 0:
        st.warning(
            "Foram encontradas "
            f"{fmt_number(nps_eligibility['respostas_nps_nao_elegiveis'])} respostas de NPS "
            "em usuarios sem compra no dataset filtrado. Elas nao entram no calculo do NPS "
            "e devem ser investigadas como regra de negocio, janela de atribuição ou tracking."
        )

    fig = px.bar(
        nps_summary,
        x="segmento",
        y="nps",
        color="segmento",
        text="nps",
        title="NPS por segmento",
    )
    fig.update_traces(texttemplate="%{text:.1f}")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(nps_summary, use_container_width=True, hide_index=True)

    st.subheader("Elegibilidade das respostas NPS")
    st.dataframe(pd.DataFrame([nps_eligibility]), use_container_width=True, hide_index=True)

    st.subheader("Investigacao das respostas NPS nao elegiveis")
    st.markdown(
        """
        Esta secao nao recalcula NPS. Ela ajuda a investigar os registros que possuem
        nota NPS, mas nao possuem compra associada no dataset filtrado.
        """
    )

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            non_eligible_channel.sort_values("respostas_nao_elegiveis"),
            x="respostas_nao_elegiveis",
            y="segmento",
            orientation="h",
            text="respostas_nao_elegiveis",
            title="Respostas nao elegiveis por canal",
            labels={"segmento": "Canal", "respostas_nao_elegiveis": "Respostas"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            non_eligible_device,
            x="segmento",
            y="respostas_nao_elegiveis",
            text="respostas_nao_elegiveis",
            title="Respostas nao elegiveis por dispositivo",
            labels={"segmento": "Dispositivo", "respostas_nao_elegiveis": "Respostas"},
        )
        st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### Por pais")
        st.dataframe(non_eligible_country, use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### Por status de signup")
        st.dataframe(non_eligible_signup, use_container_width=True, hide_index=True)
    with c3:
        st.markdown("#### Por classe da nota")
        st.dataframe(non_eligible_class, use_container_width=True, hide_index=True)

    st.markdown("#### Principais combinacoes")
    st.dataframe(non_eligible_combinations, use_container_width=True, hide_index=True)

    st.subheader("NPS por canal")
    fig = px.bar(
        nps_channel.sort_values("nps"),
        x="nps",
        y="channel",
        orientation="h",
        text="nps",
        title="NPS por canal",
    )
    fig.update_traces(texttemplate="%{text:.1f}")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(nps_channel, use_container_width=True, hide_index=True)

with tab_quality:
    current_validation = validate_data(filtered)
    current_profile = profile_data(filtered)
    st.subheader("Profiling da base filtrada")
    st.dataframe(current_profile, use_container_width=True, hide_index=True)
    st.subheader("Validacoes da base completa")
    st.dataframe(validation_df, use_container_width=True, hide_index=True)
    st.subheader("Validacoes com filtros aplicados")
    st.dataframe(current_validation, use_container_width=True, hide_index=True)

    st.markdown(
        """
        As regras criticas do funil nao apresentaram inconsistencias na base completa:
        nao ha compra sem signup, compra sem plano, plano sem compra, nem NPS preenchido sem resposta.
        Como NPS foi tratado como pesquisa pos-compra, respostas NPS associadas a usuarios sem compra
        aparecem como ponto de investigacao e nao entram no indicador final.
        """
    )

with tab_response:
    st.subheader("Como a solucao responde ao resultado esperado")
    st.markdown(
        """
        O desafio avalia quatro capacidades principais. A leitura abaixo conecta cada uma
        delas aos artefatos e conclusoes desta analise.
        """
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 1. Entender e investigar o comportamento dos usuarios")
        st.markdown(
            """
            - O funil foi medido de visita para signup e de signup para compra.
            - A analise foi segmentada por canal, dispositivo, pais, mes e plano.
            - O NPS foi calculado apenas para compradores, respeitando a regra de pesquisa pos-compra.
            """
        )

        st.markdown("#### 2. Identificar gargalos e oportunidades no funil")
        st.markdown(
            """
            - O maior gargalo absoluto esta antes do signup: 70,17% dos visitantes nao criam conta.
            - O segundo gargalo esta depois do signup: 69,19% dos cadastrados nao compram.
            - Mobile tem alto volume, mas conversao bem menor que desktop.
            - Paid e social geram volume, mas apresentam baixa eficiencia de compra.
            """
        )

    with c2:
        st.markdown("#### 3. Aplicar raciocinio analitico e estatistico")
        st.markdown(
            """
            - As metricas foram calculadas por SQL no DuckDB, reduzindo risco de calculos manuais.
            - A base passou por validacoes de unicidade, nulos, consistencia de funil e dominios.
            - As taxas foram comparadas por segmento para diferenciar volume, eficiencia e qualidade.
            - A leitura de NPS evita conclusao superficial ao separar respostas elegiveis de registros que exigem investigacao.
            """
        )

        st.markdown("#### 4. Transformar achados em recomendacoes de negocio")
        st.markdown(
            """
            - Escalar referral, pois combina melhor conversao e melhor NPS.
            - Otimizar paid antes de aumentar investimento.
            - Melhorar UX e checkout mobile.
            - Fortalecer organic por combinar escala e eficiencia.
            - Usar email/lifecycle para recuperar signups sem compra.
            - Investigar usuarios sem compra por pesquisa qualitativa, eventos de jornada ou motivos de abandono.
            """
        )

    st.markdown("#### Investigacao adicional: respostas NPS nao elegiveis")
    st.markdown(
        """
        - Foram identificadas respostas NPS em usuarios sem compra associada.
        - Esses registros nao entram no NPS final, pois o NPS foi tratado como pesquisa pos-compra.
        - A investigacao foi adicionada ao dashboard para segmentar esses registros por canal, dispositivo, pais, signup e classe da nota.
        - Na base completa, a maior concentracao esta em `organic` e `paid`, em `mobile`, e principalmente em usuarios com signup sem compra.
        - Possiveis resolucoes: validar regra de disparo da pesquisa, auditar tracking de purchase, checar compras fora da janela e criar pesquisa especifica para abandono.
        """
    )

    st.info(
        "Em resumo: a entrega mostra o que acontece no funil, onde o produto perde usuarios, "
        "quais hipoteses explicam essas perdas e quais acoes de negocio devem ser priorizadas."
    )
