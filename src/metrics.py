from __future__ import annotations

import duckdb
import pandas as pd


def query_df(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return con.execute(sql).df()


def get_overall_funnel(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        select
            count(*) as visits,
            sum(signup) as signups,
            sum(purchase) as purchases,
            sum(case when purchase = 1 then respondeu_nps else 0 end) as nps_responses,
            sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
            sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
            sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
            sum(case when purchase = 1 then respondeu_nps else 0 end) * 1.0
                / nullif(sum(purchase), 0) as nps_response_rate,
            avg(case when purchase = 1 then nps_score end) as avg_nps_score
        from stg_funnel_users
        """,
    )


def get_funnel_steps(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        with totals as (
            select
                count(*) as visits,
                sum(signup) as signups,
                sum(purchase) as purchases
            from stg_funnel_users
        )
        select 'Visitas' as etapa, visits as usuarios, 1.0 as taxa_sobre_visitas from totals
        union all
        select 'Signups' as etapa, signups as usuarios, signups * 1.0 / visits from totals
        union all
        select 'Compras' as etapa, purchases as usuarios, purchases * 1.0 / visits from totals
        """,
    )


def get_segment_funnel(con: duckdb.DuckDBPyConnection, dimension: str) -> pd.DataFrame:
    allowed = {"channel", "device", "country", "visit_month", "plan"}
    if dimension not in allowed:
        raise ValueError(f"Dimensao nao permitida: {dimension}")

    filter_plan = "where plan is not null" if dimension == "plan" else ""
    return query_df(
        con,
        f"""
        select
            {dimension} as segmento,
            count(*) as visits,
            sum(signup) as signups,
            sum(purchase) as purchases,
            sum(case when purchase = 1 then respondeu_nps else 0 end) as nps_responses,
            avg(case when purchase = 1 then nps_score end) as avg_nps_score,
            avg(days_to_signup) as avg_days_to_signup,
            avg(days_to_purchase) as avg_days_to_purchase,
            sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
            sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
            sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate
        from stg_funnel_users
        {filter_plan}
        group by 1
        order by visit_to_purchase_rate desc, visits desc
        """,
    )


def get_channel_device_matrix(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        select
            channel,
            device,
            count(*) as visits,
            sum(purchase) as purchases,
            sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate
        from stg_funnel_users
        group by 1, 2
        order by channel, device
        """,
    )


def get_nps_summary(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        with scored as (
            select
                'Compradores' as segmento,
                nps_score,
                case
                    when nps_score >= 9 then 'Promoter'
                    when nps_score >= 7 then 'Passive'
                    else 'Detractor'
                end as nps_class
            from stg_funnel_users
            where purchase = 1
              and nps_score is not null
        )
        select
            segmento,
            count(*) as respostas,
            avg(nps_score) as nps_medio,
            sum(case when nps_class = 'Promoter' then 1 else 0 end) as promotores,
            sum(case when nps_class = 'Passive' then 1 else 0 end) as passivos,
            sum(case when nps_class = 'Detractor' then 1 else 0 end) as detratores,
            (
                sum(case when nps_class = 'Promoter' then 1 else 0 end)
                - sum(case when nps_class = 'Detractor' then 1 else 0 end)
            ) * 100.0 / count(*) as nps
        from scored
        group by 1
        order by segmento
        """,
    )


def get_nps_eligibility(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        select
            sum(case when nps_score is not null then 1 else 0 end) as respostas_nps_na_base,
            sum(case when purchase = 1 and nps_score is not null then 1 else 0 end)
                as respostas_nps_elegiveis,
            sum(case when purchase = 0 and nps_score is not null then 1 else 0 end)
                as respostas_nps_nao_elegiveis,
            sum(case when purchase = 1 and nps_score is not null then 1 else 0 end) * 1.0
                / nullif(sum(case when nps_score is not null then 1 else 0 end), 0)
                as taxa_respostas_elegiveis
        from stg_funnel_users
        """,
    )


def get_nps_by_channel(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        with scored as (
            select
                channel,
                nps_score,
                case
                    when nps_score >= 9 then 'Promoter'
                    when nps_score >= 7 then 'Passive'
                    else 'Detractor'
                end as nps_class
            from stg_funnel_users
            where purchase = 1
              and nps_score is not null
        )
        select
            channel,
            count(*) as respostas,
            avg(nps_score) as nps_medio,
            sum(case when nps_class = 'Promoter' then 1 else 0 end) as promotores,
            sum(case when nps_class = 'Detractor' then 1 else 0 end) as detratores,
            (
                sum(case when nps_class = 'Promoter' then 1 else 0 end)
                - sum(case when nps_class = 'Detractor' then 1 else 0 end)
            ) * 100.0 / count(*) as nps
        from scored
        group by 1
        order by nps desc
        """,
    )


def get_nps_non_eligible_breakdown(con: duckdb.DuckDBPyConnection, dimension: str) -> pd.DataFrame:
    dimensions = {
        "channel": "channel",
        "device": "device",
        "country": "country",
        "visit_month": "visit_month",
        "funnel_stage": "funnel_stage",
        "nps_class": "nps_class",
        "signup_status": "case when signup = 1 then 'Com signup' else 'Sem signup' end",
    }
    if dimension not in dimensions:
        raise ValueError(f"Dimensao nao permitida: {dimension}")

    expression = dimensions[dimension]
    return query_df(
        con,
        f"""
        select
            {expression} as segmento,
            count(*) as respostas_nao_elegiveis,
            avg(nps_score) as nps_medio_observado,
            sum(case when nps_class = 'Promoter' then 1 else 0 end) as promotores,
            sum(case when nps_class = 'Passive' then 1 else 0 end) as passivos,
            sum(case when nps_class = 'Detractor' then 1 else 0 end) as detratores
        from stg_funnel_users
        where purchase = 0
          and nps_score is not null
        group by 1
        order by respostas_nao_elegiveis desc, nps_medio_observado
        """,
    )


def get_nps_non_eligible_combinations(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return query_df(
        con,
        """
        select
            channel,
            device,
            country,
            case when signup = 1 then 'Com signup' else 'Sem signup' end as signup_status,
            count(*) as respostas_nao_elegiveis,
            avg(nps_score) as nps_medio_observado,
            sum(case when nps_class = 'Promoter' then 1 else 0 end) as promotores,
            sum(case when nps_class = 'Passive' then 1 else 0 end) as passivos,
            sum(case when nps_class = 'Detractor' then 1 else 0 end) as detratores
        from stg_funnel_users
        where purchase = 0
          and nps_score is not null
        group by 1, 2, 3, 4
        order by respostas_nao_elegiveis desc, nps_medio_observado
        limit 20
        """,
    )
