from __future__ import annotations

import duckdb
import pandas as pd

from src.config import (
    CREATE_VIEWS_SQL,
    DATA_FILE,
    EXPECTED_CHANNELS,
    EXPECTED_COUNTRIES,
    EXPECTED_DEVICES,
    EXPECTED_PLANS,
)


def load_raw_data() -> pd.DataFrame:
    """Carrega o CSV original mantendo a base local como fonte unica."""
    return pd.read_csv(DATA_FILE)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["dt_visit"] = pd.to_datetime(data["dt_visit"], errors="coerce")
    data["signup"] = data["signup"].astype("int64")
    data["purchase"] = data["purchase"].astype("int64")
    data["respondeu_nps"] = data["respondeu_nps"].astype("int64")

    data["days_to_signup"] = data["days_to_signup"].astype("Int64")
    data["days_to_purchase"] = data["days_to_purchase"].astype("Int64")
    data["nps_score"] = data["nps_score"].astype("Float64")

    data["visit_month"] = data["dt_visit"].dt.to_period("M").astype(str)
    data["signup_date"] = data["dt_visit"] + pd.to_timedelta(data["days_to_signup"], unit="D")
    data["purchase_date"] = data["signup_date"] + pd.to_timedelta(data["days_to_purchase"], unit="D")

    data["visited_flag"] = 1
    data["funnel_stage"] = "Visit only"
    data.loc[(data["signup"] == 1) & (data["purchase"] == 0), "funnel_stage"] = "Signup only"
    data.loc[data["purchase"] == 1, "funnel_stage"] = "Purchased"

    data["nps_class"] = "No response"
    data.loc[data["nps_score"].notna() & (data["nps_score"] < 7), "nps_class"] = "Detractor"
    data.loc[data["nps_score"].notna() & (data["nps_score"] >= 7) & (data["nps_score"] < 9), "nps_class"] = "Passive"
    data.loc[data["nps_score"].notna() & (data["nps_score"] >= 9), "nps_class"] = "Promoter"

    return data


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("linhas", len(df)),
        ("usuarios_unicos", df["user_id"].nunique()),
        ("usuarios_duplicados", int(df["user_id"].duplicated().sum())),
        ("datas_invalidas", int(df["dt_visit"].isna().sum())),
        ("purchase_sem_signup", int(((df["purchase"] == 1) & (df["signup"] == 0)).sum())),
        ("plan_sem_purchase", int((df["plan"].notna() & (df["purchase"] == 0)).sum())),
        ("purchase_sem_plan", int(((df["purchase"] == 1) & df["plan"].isna()).sum())),
        ("days_signup_sem_signup", int((df["days_to_signup"].notna() & (df["signup"] == 0)).sum())),
        ("signup_sem_days_signup", int(((df["signup"] == 1) & df["days_to_signup"].isna()).sum())),
        ("days_purchase_sem_purchase", int((df["days_to_purchase"].notna() & (df["purchase"] == 0)).sum())),
        ("purchase_sem_days_purchase", int(((df["purchase"] == 1) & df["days_to_purchase"].isna()).sum())),
        ("nps_score_sem_resposta", int((df["nps_score"].notna() & (df["respondeu_nps"] == 0)).sum())),
        ("resposta_sem_nps_score", int(((df["respondeu_nps"] == 1) & df["nps_score"].isna()).sum())),
        ("nps_fora_intervalo", int(((df["nps_score"] < 0) | (df["nps_score"] > 10)).sum())),
        ("days_to_signup_negativo", int((df["days_to_signup"] < 0).sum())),
        ("days_to_purchase_negativo", int((df["days_to_purchase"] < 0).sum())),
        ("canais_inesperados", int((~df["channel"].isin(EXPECTED_CHANNELS)).sum())),
        ("devices_inesperados", int((~df["device"].isin(EXPECTED_DEVICES)).sum())),
        ("paises_inesperados", int((~df["country"].isin(EXPECTED_COUNTRIES)).sum())),
        ("planos_inesperados", int((df["plan"].notna() & ~df["plan"].isin(EXPECTED_PLANS)).sum())),
        ("respostas_nps_nao_compradores", int(((df["respondeu_nps"] == 1) & (df["purchase"] == 0)).sum())),
    ]
    return pd.DataFrame(checks, columns=["regra", "resultado"])


def profile_data(df: pd.DataFrame) -> pd.DataFrame:
    profile = [
        ("linhas", len(df)),
        ("colunas", df.shape[1]),
        ("usuarios_unicos", df["user_id"].nunique()),
        ("data_minima_visita", df["dt_visit"].min().date().isoformat()),
        ("data_maxima_visita", df["dt_visit"].max().date().isoformat()),
        ("canais", df["channel"].nunique()),
        ("dispositivos", df["device"].nunique()),
        ("paises", df["country"].nunique()),
        ("planos", df["plan"].nunique(dropna=True)),
    ]
    return pd.DataFrame(profile, columns=["metrica", "valor"])


def create_analytical_views(con: duckdb.DuckDBPyConnection) -> None:
    sql = CREATE_VIEWS_SQL.read_text(encoding="utf-8")
    con.execute(sql)


def create_connection(df: pd.DataFrame) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.register("stg_funnel_users", df)
    create_analytical_views(con)
    return con


def load_validated_connection() -> tuple[pd.DataFrame, pd.DataFrame, duckdb.DuckDBPyConnection]:
    raw = load_raw_data()
    transformed = transform_data(raw)
    validations = validate_data(transformed)
    con = create_connection(transformed)
    return transformed, validations, con
