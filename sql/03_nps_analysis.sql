-- NPS de compradores elegiveis
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
group by segmento
order by nps desc;

-- Elegibilidade das respostas NPS
select
    sum(case when nps_score is not null then 1 else 0 end) as respostas_nps_na_base,
    sum(case when purchase = 1 and nps_score is not null then 1 else 0 end) as respostas_nps_elegiveis,
    sum(case when purchase = 0 and nps_score is not null then 1 else 0 end) as respostas_nps_nao_elegiveis,
    sum(case when purchase = 1 and nps_score is not null then 1 else 0 end) * 1.0
        / nullif(sum(case when nps_score is not null then 1 else 0 end), 0) as taxa_respostas_elegiveis
from stg_funnel_users;

-- Investigacao das respostas NPS nao elegiveis por canal
select
    channel,
    count(*) as respostas_nao_elegiveis,
    avg(nps_score) as nps_medio_observado,
    sum(case when nps_class = 'Promoter' then 1 else 0 end) as promotores,
    sum(case when nps_class = 'Passive' then 1 else 0 end) as passivos,
    sum(case when nps_class = 'Detractor' then 1 else 0 end) as detratores
from stg_funnel_users
where purchase = 0
  and nps_score is not null
group by channel
order by respostas_nao_elegiveis desc;

-- Investigacao das respostas NPS nao elegiveis por dispositivo
select
    device,
    count(*) as respostas_nao_elegiveis,
    avg(nps_score) as nps_medio_observado,
    sum(case when nps_class = 'Promoter' then 1 else 0 end) as promotores,
    sum(case when nps_class = 'Passive' then 1 else 0 end) as passivos,
    sum(case when nps_class = 'Detractor' then 1 else 0 end) as detratores
from stg_funnel_users
where purchase = 0
  and nps_score is not null
group by device
order by respostas_nao_elegiveis desc;

-- NPS por canal, considerando apenas compradores elegiveis
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
group by channel
order by nps desc;
