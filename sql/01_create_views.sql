-- Views analiticas criadas em memoria na conexao DuckDB usada pelo app Streamlit.
-- O dataframe tratado em Pandas e registrado como stg_funnel_users antes da execucao deste arquivo.

create or replace view vw_funnel_overall as
select
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(respondeu_nps) as nps_responses,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_funnel_users;

create or replace view vw_funnel_by_channel as
select
    channel,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_funnel_users
group by channel;

create or replace view vw_funnel_by_device as
select
    device,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_funnel_users
group by device;

create or replace view vw_funnel_by_country as
select
    country,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_funnel_users
group by country;

create or replace view vw_funnel_by_month as
select
    visit_month,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(nps_score) as avg_nps_score
from stg_funnel_users
group by visit_month;

create or replace view vw_plan_mix as
select
    plan,
    count(*) as purchases,
    avg(nps_score) as avg_nps_score,
    avg(days_to_purchase) as avg_days_to_purchase
from stg_funnel_users
where plan is not null
group by plan;

create or replace view vw_channel_device as
select
    channel,
    device,
    count(*) as visits,
    sum(purchase) as purchases,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate
from stg_funnel_users
group by channel, device;

create or replace view vw_nps_summary as
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
group by segmento;

create or replace view vw_nps_by_channel as
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
group by channel;
