-- Funil geral
select
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate
from stg_funnel_users;

-- Funil por canal
select
    channel,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(days_to_signup) as avg_days_to_signup,
    avg(days_to_purchase) as avg_days_to_purchase
from stg_funnel_users
group by channel
order by visit_to_purchase_rate desc;

-- Funil por dispositivo
select
    device,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate
from stg_funnel_users
group by device
order by visit_to_purchase_rate desc;

-- Evolucao mensal por data de visita
select
    visit_month,
    count(*) as visits,
    sum(signup) as signups,
    sum(purchase) as purchases,
    sum(signup) * 1.0 / count(*) as visit_to_signup_rate,
    sum(purchase) * 1.0 / count(*) as visit_to_purchase_rate,
    sum(purchase) * 1.0 / nullif(sum(signup), 0) as signup_to_purchase_rate,
    avg(case when purchase = 1 then nps_score end) as avg_nps_score
from stg_funnel_users
group by visit_month
order by visit_month;
