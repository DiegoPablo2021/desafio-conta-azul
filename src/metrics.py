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
            sum(respondeu_nps) as nps_responses,
            sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
            sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
            sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
            sum(respondeu_nps) * 1.0 / count(*) as nps_response_rate,
            avg(nps_score) as avg_nps_score
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
            sum(respondeu_nps) as nps_responses,
            avg(nps_score) as avg_nps_score,
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
                case when purchase = 1 then 'Compradores' else 'Nao compradores' end as segmento,
                nps_score,
                case
                    when nps_score >= 9 then 'Promoter'
                    when nps_score >= 7 then 'Passive'
                    else 'Detractor'
                end as nps_class
            from stg_funnel_users
            where nps_score is not null
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
        union all
        select
            'Geral' as segmento,
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
        order by segmento
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
            where nps_score is not null
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
