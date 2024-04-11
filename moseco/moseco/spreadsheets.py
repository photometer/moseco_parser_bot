import argparse
import datetime as dt

from pandas import concat, DataFrame

try:
    from .services import (DRIVE_SERVICE, EMAIL_USER, MOSCOW, REQUESTS, SHEETS,
                           SHEETS_SERVICE, STATIONS)
except (ModuleNotFoundError, ImportError):
    from services import (DRIVE_SERVICE, EMAIL_USER, MOSCOW, REQUESTS, SHEETS,
                          SHEETS_SERVICE, SPREADSHEET_ID, STATIONS)

FORMAT = '%d.%m.%Y %H:%M'
RANGE = '!A1:BI10000'


def get_list_obj(service):
    """Get list of files on the disk."""
    response = service.files().list(
        q='mimeType="application/vnd.google-apps.spreadsheet"'
    ).execute()
    return response['files']


def delete_sheets(service, spreadsheet_id):
    """Delete the spreadsheet with certain id."""
    response = service.files().delete(fileId=spreadsheet_id)
    response.execute()
    return 'Документ удален'


def set_user_permissions(service, spreadsheet_id, data=None):
    """Set permissions to a user."""
    if data:
        role, email = data.split(',')
    else:
        role, email = None, None
    permissions_body = {'type': 'user',
                        'role': role or 'writer',
                        'emailAddress': email or EMAIL_USER}
    service.permissions().create(
        fileId=spreadsheet_id,
        body=permissions_body,
        fields='id'
    ).execute()


def read_values(service, spreadsheet_id, sheetname):
    """Read all values from the spreadsheet with certain id."""
    response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=sheetname + RANGE
    ).execute()
    return response['values']


def spreadsheet_update_values(service, spreadsheet_id, data=None,
                              sheetname=None, default=False):
    """Add new values to the spreadsheet with certain id."""
    counter = 0
    if default:
        request = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': REQUESTS}
        ).execute()
        table_values = [
            [
                'Дата и время',
                *[station.upper() for station in STATIONS['stations']]
            ],
        ]
        counter = 1
        values = []
        for sheet in SHEETS:
            values.append({
                'majorDimension': 'ROWS',
                'values': table_values,
                'range': sheet['properties']['title'] + RANGE
            })
    else:
        table_values = read_values(service, spreadsheet_id, sheetname)
        if table_values[-1][0] != 'Дата и время':
            while (
                data.index.values.any()
            ) and (
                data.index[0] <= dt.datetime.strptime(
                    table_values[-1][0], FORMAT
                ).replace(tzinfo=MOSCOW)
            ):
                data = data.drop(index=data.index[0])
            empty_counter = 0
            while (
                data.index.values.any()
            ) and (
                data.index[0] > dt.datetime.strptime(
                    table_values[-1][0], FORMAT
                ).replace(tzinfo=MOSCOW) + dt.timedelta(hours=1)
            ):
                empty_line = DataFrame(
                    {
                        pollutant: [data.index[0] - dt.timedelta(hours=1)] if (
                            pollutant == 'datetime'
                        ) else None for pollutant in (
                            ['datetime'] + table_values[0][1:]
                        )
                    },
                )
                empty_line = empty_line.set_index('datetime')
                data = concat([empty_line, data])
                empty_counter += 1
            if empty_counter:
                REQUESTS.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': spreadsheet_id,
                            'startRowIndex': len(table_values[:][0]),
                            'endRowIndex': len(table_values[:][0]) + empty_counter,
                            'startColumnIndex': 0,
                            'endColumnIndex': data.shape[1] - 2,
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 1,
                                                    'green': 0,
                                                    'blue': 0}
                            }
                        },
                        'fields': (
                            'userEnteredFormat(backgroundColor, textFormat)'
                        )
                    },
                })
        data = data.fillna('').reset_index()
        data['datetime'] = list(map(
            lambda x: x.strftime(FORMAT), data['datetime']
        ))
        for row in list(map(list, data.values)):
            table_values.append(row)
            counter += 1
        values = [{
            'majorDimension': 'ROWS',
            'values': table_values,
            'range': sheetname + RANGE
        }]
    body = {'data': values, 'valueInputOption': 'USER_ENTERED'}
    request = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    )
    request.execute()
    return f'В документ добавлено по {counter} новых строк'


def create_spreadsheet(service):
    """Create a spreasheet."""
    spreadsheet_body = {
        'properties': {
            'title': 'Данные Мосэкомониторинга',
            'locale': 'ru_RU'
        },
        'sheets': SHEETS,
    }
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    spreadsheet_id = response['spreadsheetId']
    set_user_permissions(DRIVE_SERVICE, spreadsheet_id)
    spreadsheet_update_values(SHEETS_SERVICE,
                              spreadsheet_id,
                              default=True)
    print(f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}')
    return f'Был создан документ с ID {spreadsheet_id}'


def main(args):
    if args.create:
        return create_spreadsheet(SHEETS_SERVICE)
    spreadsheet_id = None
    if args.set_permissions is not None:
        return set_user_permissions(
            DRIVE_SERVICE, SPREADSHEET_ID, args.set_permissions
        )
    if args.id is not None:
        spreadsheet_id = args.id
    else:
        spreadsheets = get_list_obj(DRIVE_SERVICE)
        if spreadsheets:
            spreadsheet_id = spreadsheets[0]['id']
    if args.update_reinit:
        return spreadsheet_update_values(SHEETS_SERVICE, spreadsheet_id,
                                         default=True)
    if args.delete_sheet:
        return delete_sheets(DRIVE_SERVICE, spreadsheet_id)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Данные Мосэкомониторинга')
    parser.add_argument('-c', '--create', action='store_true',
                        help='Создать файл')
    parser.add_argument('-i', '--id', help='Указать id spreadsheet')
    parser.add_argument('-sp', '--set_permissions',
                        help='Настройки доступа для нового пользователя. '
                             'Введите "роль[reader, writer],email')
    parser.add_argument('-ur', '--update_reinit', action='store_true',
                        help='Реинициализировать форматирование таблицы')
    parser.add_argument('-del', '--delete_sheet', action='store_true',
                        help='Удалить таблицу')
    args = parser.parse_args()
    print(main(args))
