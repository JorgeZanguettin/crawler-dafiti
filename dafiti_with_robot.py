import json

import logging
from robot import Robot
from robot.collector.shortcut import *

logging.basicConfig(level=logging.DEBUG)



collector = pipe(
    const('https://www.dafiti.com.br/'),
    get(),
    css('li.menu-dropdown-title a[href].menu-dropdown-link'),
    attr('href'),
    foreach(
        get(),
        css('ul.pagination-list li.page:nth-last-child(2)'),
        as_text(),
        fn( lambda it: int(it or 0)),
        fn( lambda pages: range(1, pages + 1)),
        foreach(
            fn( lambda page: '?page={}'.format(page) ),
            get(),
            css('div.product-box a[href].product-box-link.is-lazyloaded.image.product-image-rotate'),
            attr('href'),
            foreach(
                suppress(
                    get(),
                    dict(
                        name=pipe( css('[itemprop=name]'), as_text() ),
                        url=pipe( context(), jsonpath('$.url'), any() ),
                        details=pipe( css('[itemprop=description]'), as_text() ),
                        brand=pipe( css('[itemprop=brand]'), as_text() ),
                        value_with_discount=pipe( css('[data-field=finalPrice]'), as_text() ),
                    ),
                ),
            ),
            filter( lambda it: it is not None ),
            tap(dict_csv(const('products-with-robot.csv'), mode='a+')),
            limit=1,
        ),
        flat(),
        limit=1,
    ),
    flat(),
)

with Robot() as robot:
    result = robot.sync_run(collector)
    print(json.dumps(result, indent=2))
