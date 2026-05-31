-- NPS geral, compradores e nao compradores
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
group by segmento
order by nps desc;

-- NPS por canal
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
group by channel
order by nps desc;
