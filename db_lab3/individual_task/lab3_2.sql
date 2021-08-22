--2. Вывести динамику изменения доли заказов с доставкой от общего количества помесячно за 5 последних лет.
select sometable.count as count_with_del,
       sometable_all.count as count_all,
       (sometable.count::decimal / sometable_all.count::decimal) as dynamic,
       sometable.years as years_, 
       sometable.months as months_ 
from (select
            count(o.order_id) as count,
            extract(year from o.date_of_order) as years,
            extract(month from o.date_of_order) as months
      from "order" o
      where o.date_of_order > (now() - '5 year'::interval) AND o.order_id in (select ppd.order_id from pp_delivery ppd)
      group by years, months) as sometable
      inner join (
          select
             count(o.order_id) as count,
             extract(year from o.date_of_order) as years,
             extract(month from o.date_of_order) as months
          from "order" o
          where o.date_of_order > (now() - '5 year'::interval)
          group by years, months) as sometable_all
     on sometable.months = sometable_all.months and sometable.years = sometable_all.years
     order by years_, months_;