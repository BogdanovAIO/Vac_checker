import os
import json
import requests
from colorama import init, Fore, Style
import numpy

API_KEY = 'СЮДА_НАПИСАТЬ_СВОЙ_API_KEY_В_КАВЫЧКИ_(ЛЮБОЙ_АКК)'
check_ban_url = 'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/'
id_banned_accs = []
id_not_banned_accs = []
DATA_ID_LOGIN = {}


class ApiError(Exception):
    pass


def check_ban_status_mafile_api(ids):
    """Проверка на VAC по id из maFile."""
    ids_array = numpy.array_split(ids, len(ids) // 10)
    game_bans = 0
    vac_bans = 0
    community_bans = 0
    for ids_list in ids_array:
        params = {
            'key': API_KEY,
            'steamids': f'{ids_list}'
        }
        try:
            response = requests.get(url=check_ban_url, params=params)
            response_info = response.json()
            accs_info = response_info.get('players')
        except Exception:
            raise ApiError('Ошибка api | Введите api ключ или повторите попытку')
        for acc in accs_info:
            try:
                number_of_game_bans = acc.get('NumberOfGameBans')
                number_of_vac_bans = acc.get('NumberOfVACBans')
                status_community_ban = acc.get('CommunityBanned')
                steam_id = int(acc.get('SteamId'))
                if number_of_game_bans > 0 or number_of_vac_bans > 0 or status_community_ban:
                    if number_of_vac_bans > 0:
                        vac_bans += 1
                    if number_of_game_bans > 0:
                        game_bans += 1
                    if status_community_ban:
                        community_bans += 1
                    id_banned_accs.append(steam_id)
                    days_last_ban = acc.get('DaysSinceLastBan')
                    print(Fore.RED + f'[SteamID: {steam_id}] '
                                     f'[login: {DATA_ID_LOGIN[steam_id]}] VAC найдет.')
                    print(f'Количество банов: {number_of_game_bans + number_of_vac_bans + status_community_ban} '
                          f'| Дней с последнего: {days_last_ban}')
                else:
                    print(Fore.GREEN + f'[SteamID: {steam_id}] '
                                       f'[login: {DATA_ID_LOGIN[steam_id]}] Бана нет.')
                    id_not_banned_accs.append(steam_id)
            except Exception as error:
                print(f'[ERROR] Ошибка получения статуса бана: {error}')
    return vac_bans, game_bans, community_bans


def open_mafile():
    try:
        for filename in os.listdir("maFiles"):
            with open(os.path.join("maFiles", filename), 'r') as file:
                text = file.read()
                text_json = json.loads(text)
                account_name = text_json.get('account_name')
                steam_id = text_json.get('Session').get('SteamID')
                DATA_ID_LOGIN[steam_id] = account_name
        ids = list(DATA_ID_LOGIN.keys())
        return check_ban_status_mafile_api(ids)
    except Exception as error:
        print(f'[ERROR] Ошибка чтения maFiles: {error}'
              f'account_name: {account_name}')


def check_ban_status():
    while True:
        choice = input("""Для проверки по maFiles должны быть maFiles в папке maFiles и прописан API ключ
[1] Проверка по maFiles
Ввод:""")
        if choice == '1':
            init()
            vac_bans, game_bans, community_bans = open_mafile()
            # Че-то блять ошибка какая-то впадлу разбираться
            # print(Fore.BLUE + f'Accs with ban:')
            # print('~' * 80)
            # if id_banned_accs:
            #     for id_ in id_banned_accs:
            #         print(f'id: {id_} login: {DATA_ID_LOGIN[id_]}')
            print('~' * 80)
            print(Fore.GREEN + f'Accs without ban:')
            print('~' * 80)
            if id_not_banned_accs:
                for id_ in id_not_banned_accs:
                    print(f'id: {id_} login: {DATA_ID_LOGIN[id_]}')
            print('~' * 80)
            print(f'''Проверка закончена.
Аккаунтов проверено: {len(DATA_ID_LOGIN.keys())}
Блокировок найдено: {len(id_banned_accs)}
Аккаунтов с Game ban: {game_bans}
Аккаунтов с VAC: {vac_bans}
Аккаунтов Community ban: {community_bans}''')
            print(Style.RESET_ALL)
            id_banned_accs.clear()
            DATA_ID_LOGIN.clear()
        continue


if __name__ == '__main__':
    check_ban_status()
