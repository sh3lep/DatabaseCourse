--1. Вывести месяцы за последний год, в которых заказов от новых покупателей
-- (без карт лояльности) было больше, чем от заказывавших ранее.
select
       table_without_cards.count as count_orders_without_cards,
       table_with_cards.count as count_orders_with_cards,
       table_with_cards.years as years_,
       table_with_cards.months as month_
from (select 
       count(o.order_id) as count,
       extract(year from o.date_of_order) as years,
       extract(month from o.date_of_order) as months
    from (
        select c.customer_id
        from customer c
        where c.customer_id not in (
            select lc.customer_id
            from loyalty_card lc)) as sometable
    inner join "order" o on sometable.customer_id = o.customer_id
    where o.date_of_order > ('2021-04-01'::date - '1 year'::interval)
    group by years, months) as table_without_cards
    inner join (
        select
            count(o.order_id) as count,
            extract(year from o.date_of_order) as years,
            extract(month from o.date_of_order) as months
        from (
            select c.customer_id
            from customer c
            where c.customer_id in (
                select lc.customer_id
                from loyalty_card lc)) as sometable
        inner join "order" o on sometable.customer_id = o.customer_id
        where o.date_of_order > ('2021-04-01'::date - '1 year'::interval)
        group by years, months) as table_with_cards
    on table_without_cards.years = table_with_cards.years and table_without_cards.months = table_with_cards.months
where table_with_cards.count < table_without_cards.count order by years_, month_;
