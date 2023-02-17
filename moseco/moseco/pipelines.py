import os

import pandas as pd
from dotenv import load_dotenv

from .services import PARAMETERS, SHEETS_SERVICE, STATIONS
from .spreadsheets import spreadsheet_update_values

load_dotenv()


class MosecoPipeline:
    def __init__(self, *args, **kwargs):
        self.values = {}
        for parameter in PARAMETERS:
            table = {'datetime': []}
            table.update({station: [] for station in STATIONS['stations']})
            self.values[parameter] = pd.DataFrame(table).set_index('datetime')

    def process_item(self, item, spider):
        self.values[item['parameter']][item['station']] = (
            item['datetime_concentration']
        )
        return f'Станция {item["station"]} обработана.'

    def close_spider(self, spider):
        for parameter in PARAMETERS:
            spreadsheet_update_values(
                SHEETS_SERVICE, os.getenv('SPREADSHEET_ID'),
                data=self.values[parameter],
                sheetname=parameter.replace('.', '')
            )
