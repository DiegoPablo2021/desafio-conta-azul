from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "saas_funnel_case_10k_refresh_(4)_(2).csv"
DOCS_DIR = ROOT_DIR / "docs"
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DOC_DIR = OUTPUT_DIR / "doc"
SQL_DIR = ROOT_DIR / "sql"
CREATE_VIEWS_SQL = SQL_DIR / "01_create_views.sql"

EXPECTED_CHANNELS = {"organic", "paid", "referral", "social", "email"}
EXPECTED_DEVICES = {"mobile", "desktop"}
EXPECTED_COUNTRIES = {"BR", "MX", "AR", "CL", "US"}
EXPECTED_PLANS = {"BASIC", "PRO", "PREMIUM"}
