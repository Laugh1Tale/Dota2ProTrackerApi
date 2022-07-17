from datetime import datetime
from datetime import timedelta

import database
import main
import models


def delete_data():
    eight_days = datetime.now() - timedelta(days=8)
    matches_for_delete = get_database().query(models.Match).filter(models.Match.match_time < eight_days).all()
    for match in matches_for_delete:
        delete_match(match.id)


def delete_match(match_id):
    matches_players = main.read_matches_players(match_id=match_id, db=get_database())
    for match_player in matches_players:
        delete_match_player(match_player)
    main.delete_match(match_id=match_id, db=get_database())


def delete_match_player(match_player):
    update_player(match_player.player_id, match_player.is_victory)
    update_hero(match_player.hero_id, match_player.is_victory)
    main.delete_match_player(match_id=match_player.match_id, player_id=match_player.player_id, db=get_database())


def update_player(player_id, is_victory):
    db_player = main.read_player(player_id=player_id, db=get_database())
    db_player.win -= 1 if is_victory else 0
    db_player.lose -= 0 if is_victory else 1
    main.update_player(player_id=player_id, player=db_player, db=get_database())


def update_hero(hero_id, is_victory):
    db_hero = main.read_hero(hero_id=hero_id, db=get_database())
    db_hero.win += 1 if is_victory else 0
    db_hero.lose += 0 if is_victory else 1
    main.update_hero(hero_id=hero_id, hero=db_hero, db=get_database())


def get_database():
    db = database.SessionLocal()
    try:
        return db
    finally:
        db.close()


if __name__ == "__main__":
    delete_data()
