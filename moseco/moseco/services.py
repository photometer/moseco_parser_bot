import os

import pytz
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient import discovery

MOSCOW = pytz.timezone('Europe/Moscow')

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

load_dotenv()
EMAIL_USER = os.environ['EMAIL']
SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
INFO = {
    'type':  os.environ['TYPE'],
    'project_id':  os.environ['PROJECT_ID'],
    'private_key_id':  os.environ['PRIVATE_KEY_ID'],
    'private_key':  os.environ['PRIVATE_KEY'],
    'client_email':  os.environ['CLIENT_EMAIL'],
    'client_id':  os.environ['CLIENT_ID'],
    'auth_uri':  os.environ['AUTH_URI'],
    'token_uri':  os.environ['TOKEN_URI'],
    'auth_provider_x509_cert_url':  os.environ['AUTH_PROVIDER_X509_CERT_URL'],
    'client_x509_cert_url':  os.environ['CLIENT_X509_CERT_URL']
}

CREDENTIALS = Credentials.from_service_account_info(
    info=INFO, scopes=SCOPES
)

SHEETS_SERVICE = discovery.build('sheets', 'v4', credentials=CREDENTIALS)
DRIVE_SERVICE = discovery.build('drive', 'v3', credentials=CREDENTIALS)

natural = ('mgu', 'losinyj-ostrov')
residential = ('chayanova', 'spiridonovka', 'kazakova', 'koptevskij',
               'ostankino-0', 'shabolovka', 'ochakovskoe-2', 'tolbuxina',
               'akademika-anoxina', 'turistskaya', 'zelenograd-6',
               'zelenograd-16', 'zelenograd-11', 'rogovo', 'shherbinka',
               'troitsk', 'semenkovo', 'salarevo', 'kuznecovo', 'troizk-2')
mixed = ('dolgoprudnaya', 'bazovskaya', 'polyarnaya', 'novokosino',
         'kozhuxovo', 'glebovskaya', 'texnopolis', 'marino', 'm2-zhulebino',
         'lyublino', 'kapotnya', 'guryanova', 'veshnyaki', 'brateevo',
         'yuzhnoe-chertanovo', 'proletarskij-prospekt', 'gurevskij-proezd',
         'birulevo', 'melitopolskaya', 'ochakovskaya')
roads = ('xamovniki', 'suxarevskaya-ploshhad', 'svetlyj-proezd',
         'nizhnyaya-maslovka', 'madi', 'ploshhad-gagarina',
         'kozhuxovskij-proezd', 'butlerova', 'narodnogo-opolcheniya',
         'spartakovskaya-ploshhad', 'mkad105', 'mkad-52-km-zapad')
indexes = [(1, len(natural) + 1), ]
for stype in (residential, mixed, roads):
    indexes.append((indexes[-1][-1], indexes[-1][-1] + len(stype)))

STATIONS = {
    'stations': (natural + residential + mixed + roads),
    'indexes': indexes,
    'colors': (
        {'red': 3 / 255, 'green': 242 / 255, 'blue': 13 / 255},
        {'red': 255 / 255, 'green': 253 / 255, 'blue': 85 / 255},
        {'red': 255 / 255, 'green': 184 / 255, 'blue': 72 / 255},
        {'red': 255 / 255, 'green': 78 / 255, 'blue': 78 / 255}
    )
}
PARAMETERS = ('PM10', 'PM2.5', 'NO2', 'NO', 'OZ', 'SO2', 'CO')

SHEETS, REQUESTS = [], []
for i, parameter in enumerate(PARAMETERS):
    SHEETS.append({
        'properties': {
            'sheetType': 'GRID',
            'sheetId': i,
            'title': parameter.replace('.', ''),
            'gridProperties': {
                'rowCount': 10000,
                'columnCount': 100
            }
        }
    })
    for j in range(len(STATIONS['colors'])):
        REQUESTS.append({
            'repeatCell': {
                'range': {
                    'sheetId': i,
                    'startRowIndex': 0, 'endRowIndex': 1,
                    'startColumnIndex': STATIONS['indexes'][j][0],
                    'endColumnIndex': STATIONS['indexes'][j][1],
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': STATIONS['colors'][j],
                        "textFormat": {"bold": True}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor, textFormat)'
            },
        })
