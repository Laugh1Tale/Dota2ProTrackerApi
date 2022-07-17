import json
from datetime import datetime, time
from time import sleep

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from requests.structures import CaseInsensitiveDict

import database
import main
import models

api_url = "https://api.stratz.com/graphql"
stratz_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJodH" \
               "RwczovL3N0ZWFtY29tbXVuaXR5LmNvbS9vcGVuaWQvaWQvNzY1NjExOTgz" \
               "NjQ3NTc1MTMiLCJ1bmlxdWVfbmFtZSI6ImRpc2FwcG9pbnRtZW50LmlkYyIsI" \
               "lN1YmplY3QiOiJmYzI0Njc2Yi1kMzg1LTRhNWItOTkzNi1kYjA3M2UzNDU0NjMiL" \
               "CJTdGVhbUlkIjoiNDA0NDkxNzg1IiwibmJmIjoxNjU3Njk5MDEyLCJleHAiOjE2ODkyM" \
               "zUwMTIsImlhdCI6MTY1NzY5OTAxMiwiaXNzIjoiaHR0cHM6Ly9hcGkuc3RyYXR6LmNvbSJ9.7" \
               "bSUiBSERtcDAfWYDb7l2i1tLuA_d63MhKSk5HjrQqc"
api_headers = CaseInsensitiveDict()
api_headers["Accept"] = "application/json"
api_headers["Authorization"] = f"Bearer {stratz_token}"
user_agent_headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.0.0 Safari/537.36 '
}


def upload_data():
    recently_matches = parse_Dota2ProTracker()
    for match in recently_matches:
        match_id = int(match.find('a', {'class': 'copy-id'})['data'])
        is_exist = None
        try:
            is_exist = main.read_match(db=get_database(), match_id=match_id)
        except HTTPException:
            pass
        if not is_exist:
            match_info = get_match_info(match_id)
            sleep(10)
            if match_info['data']['match'] is None:
                continue
            add_match_to_database(get_match(match, match_info, match_id))
            add_players_and_heroes_to_database(match, match_info, match_id)


def get_match(match, match_info, match_id):
    average_mmr = int(match.find('td', {'class': 'td-mmr'}).text)
    pro_player_count = int(match.find('td', {'class': 'td-np'}).text)
    match_duration = get_match_duration(match_info)
    string_description = get_match_string_description(match)
    match_time = get_match_DateTime(match_info)
    return models.Match(
        id=match_id,
        average_mmr=average_mmr,
        pro_player_count=pro_player_count,
        match_duration=match_duration,
        string_description=string_description,
        match_time=match_time,
    )


def add_match_to_database(match: models.Match):
    try:
        main.create_match(match=match, db=get_database())
    except HTTPException as e:
        print(f"status code: {e.status_code},   detail: {e.detail};")


def add_player_to_database(player: models.Player, is_victory: bool):
    try:
        main.create_player(player=player, db=get_database())
    except HTTPException:
        db_player = main.read_player(player_id=player.id, db=get_database())
        db_player.win += 1 if is_victory else 0
        db_player.lose += 0 if is_victory else 1
        main.update_player(player_id=player.id, player=db_player, db=get_database())


def add_hero_to_database(hero: models.Hero, is_victory: bool):
    try:
        main.create_hero(hero=hero, db=get_database())
    except HTTPException:
        db_hero = main.read_hero(hero_id=hero.id, db=get_database())
        db_hero.win += 1 if is_victory else 0
        db_hero.lose += 0 if is_victory else 1
        main.update_hero(hero_id=hero.id, hero=db_hero, db=get_database())


def add_match_player_to_database(match_player: models.MatchPlayer):
    try:
        main.create_match_player(match_player=match_player, db=get_database())
    except HTTPException as e:
        print(f"status code: {e.status_code},   detail: {e.detail};")


def add_players_and_heroes_to_database(match, match_info, match_id):
    pro_players = match.find('td', {'class': 'pros'}).find_all('a')
    my_dict = {}
    for i in range(1, len(pro_players), 2):
        my_dict[pro_players[i - 1]['title']] = pro_players[i].get_text()
    for player in match_info['data']['match']['players']:
        is_victory = player['isVictory']
        if player['hero']['displayName'] in my_dict:
            new_player = create_player(player, my_dict)
            match_player = create_match_player(player, match_id)
            add_player_to_database(new_player, is_victory)
            add_match_player_to_database(match_player)
        hero = create_hero(player)
        add_hero_to_database(hero, is_victory)


def create_player(player, my_dict):
    player_id = int(player['steamAccount']['id'])
    is_victory = player['isVictory']
    if player['steamAccount']['proSteamAccount'] is None:
        new_player = models.Player(
            id=player_id,
            nickname=my_dict[player['hero']['displayName']],
            real_name=my_dict[player['hero']['displayName']],
            win=1 if is_victory else 0,
            lose=0 if is_victory else 1,
        )
    else:
        new_player = models.Player(
            id=player_id,
            nickname=player['steamAccount']['proSteamAccount']['name'],
            real_name=player['steamAccount']['proSteamAccount']['realName'],
            win=1 if is_victory else 0,
            lose=0 if is_victory else 1,
        )
    return new_player


def create_hero(player):
    is_victory = player['isVictory']
    hero_id = int(player['hero']['id'])
    hero = models.Hero(
        id=hero_id,
        hero_name=player['hero']['displayName'],
        original_name=player['hero']['name'],
        win=1 if is_victory else 0,
        lose=0 if is_victory else 1,
    )
    return hero


def create_match_player(player, match_id):
    player_id = int(player['steamAccount']['id'])
    is_victory = player['isVictory']
    hero_id = int(player['hero']['id'])
    match_player = models.MatchPlayer(
        match_id=match_id,
        player_id=player_id,
        hero_id=hero_id,
        is_victory=is_victory
    )
    return match_player


def get_match_string_description(match):
    pro_players = match.find('td', {'class': 'pros'}).find_all('a')
    del pro_players[1::2]
    a = match.find('td', {'class': 'pros'}).text.split('\n')
    split_description = [x.split() for x in a if len(x.split()) > 0]
    string_description = ""
    counter = 0
    for i in range(len(pro_players)):
        player = ""
        for j in range(len(split_description[counter])):
            player += split_description[counter][j]
            player += "" if j == len(split_description[counter]) - 1 else " "
        player = player.replace(',', '')
        string_description += pro_players[i]['title'] + " " + player
        counter += 1
        string_description += ", " if i < len(pro_players) - 1 and counter < len(split_description) - 1 and \
                                      split_description[counter][0] != "lost" and \
                                      split_description[counter][0] != "won" and \
                                      (len(split_description[counter]) < 3 or
                                       split_description[counter][2] != "ago") else " "
        while counter < len(split_description) - 1 and \
                ((split_description[counter][0] == "lost" or split_description[counter][0] == "won") or
                 (len(split_description[counter]) == 3 and split_description[counter][2] == "ago")):
            for e in split_description[counter]:
                string_description += e + " "
            counter += 1
    return string_description


def parse_Dota2ProTracker():
    url = 'https://www.dota2protracker.com/'
    headers = user_agent_headers
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'lxml')
    recently_matches = soup.find('div', {'class': 'pub-stats-rf'}).find('tbody').find_all('tr')
    return recently_matches


def get_match_DateTime(match_info):
    timestamp = match_info['data']['match']['startDateTime']
    match_datetime = datetime.utcfromtimestamp(timestamp)
    return match_datetime


def get_match_duration(match_info):
    seconds = match_info['data']['match']['durationSeconds']
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    match_duration = time(hour=hours, minute=minutes, second=seconds)
    return match_duration


def get_match_info(match_id):
    query = f"""query {{
        match(id: {match_id}) {{
            durationSeconds
            startDateTime
            players{{
            isVictory
            steamAccount{{
                id
                proSteamAccount{{
                    name
                    realName
                    }}
                }}
            hero {{
                id
                name
                displayName
                }}
            }}
        }}
    }}"""
    return get_json_from_request(query)


def get_json_from_request(query):
    r = requests.post(url=api_url, json={'query': query}, headers=api_headers)
    received_json = json.loads(r.text)
    while 'data' not in received_json:
        sleep(15)
        r = requests.post(url=api_url, json={'query': query}, headers=api_headers)
        received_json = json.loads(r.text)
    return received_json


def get_database():
    db = database.SessionLocal()
    try:
        return db
    finally:
        db.close()
