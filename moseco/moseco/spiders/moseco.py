import datetime as dt
import json

import pandas as pd
import scrapy

try:
    from items import MosecoItem
    from services import PARAMETERS, STATIONS
except ModuleNotFoundError:
    from ..items import MosecoItem
    from ..services import PARAMETERS, STATIONS


class MosecoSpider(scrapy.Spider):
    name = "moseco"
    allowed_domains = ["mosecom.mos.ru"]

    def start_requests(self):
        for station in STATIONS['stations']:
            yield scrapy.Request('https://mosecom.mos.ru/' + station,
                                 self.parse,
                                 meta={'station': station})

    def parse(self, response):
        airchart = response.css(
            'script:contains("AirChart")::text'
        ).get().strip()
        val_dict = json.loads(
            airchart[15:airchart.index(', {"months"')].replace('null', "null")
        )['units']['h']
        data = {'station': response.meta['station']}
        for parameter in PARAMETERS:
            if val_dict and val_dict.get(parameter):
                data['parameter'] = parameter
                data['datetime_concentration'] = pd.DataFrame(
                    val_dict[parameter]['data'],
                    columns=['datetime', response.meta['station']]
                )
                data['datetime_concentration']['datetime'] = list(map(
                    lambda x: (
                        dt.datetime.fromtimestamp(
                            x / 1000
                        ) + dt.timedelta(hours=-3)
                    ),
                    data['datetime_concentration']['datetime']
                ))
                data['datetime_concentration'].set_index(
                    'datetime', inplace=True
                )
                yield MosecoItem(data)
