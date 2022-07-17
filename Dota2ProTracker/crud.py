from sqlalchemy import desc
from sqlalchemy.orm import Session

import models
import schemas


def create_match(db: Session, match: schemas.Match):
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def get_matches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Match).order_by(desc(models.Match.match_time)).offset(skip).limit(limit).all()


def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()


def update_match(db: Session, match_id: int, match: schemas.Match):
    desired_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    desired_match.pro_player_count = match.pro_player_count
    desired_match.string_description = match.string_description
    db.add(desired_match)
    db.commit()
    db.refresh(desired_match)
    return desired_match


def delete_match(db: Session, match_id: int):
    db.query(models.Match).filter(models.Match.id == match_id).delete()
    db.commit()
    return


def create_player(db: Session, player: schemas.Player):
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()


def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()


def update_player(db: Session, player_id: int, player: schemas.Player):
    desired_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    desired_player.nickname = player.nickname
    desired_player.real_name = player.real_name
    desired_player.win = player.win
    desired_player.lose = player.lose
    db.add(desired_player)
    db.commit()
    db.refresh(desired_player)
    return desired_player


def delete_player(db: Session, player_id: int):
    db.query(models.Player).filter(models.Player.id == player_id).delete()
    db.commit()
    return


def create_hero(db: Session, hero: schemas.Hero):
    db.add(hero)
    db.commit()
    db.refresh(hero)
    return hero


def get_heroes(db: Session):
    return db.query(models.Hero).all()


def get_hero(db: Session, hero_id: int):
    return db.query(models.Hero).filter(models.Hero.id == hero_id).first()


def update_hero(db: Session, hero_id: int, hero: schemas.Hero):
    desired_hero = db.query(models.Hero).filter(models.Hero.id == hero_id).first()
    desired_hero.hero_name = hero.hero_name
    desired_hero.original_name = hero.original_name
    desired_hero.win = hero.win
    desired_hero.lose = hero.lose
    db.add(desired_hero)
    db.commit()
    db.refresh(desired_hero)
    return desired_hero


def delete_hero(db: Session, hero_id: int):
    db.query(models.Hero).filter(models.Hero.id == hero_id).delete()
    db.commit()
    return


def create_match_player(db: Session, match_player: schemas.MatchPlayer):
    db.add(match_player)
    db.commit()
    db.refresh(match_player)
    return match_player


def get_matches_players(db: Session, match_id: int = None, player_id: int = None, skip: int = 0, limit: int = 100):
    matches_players = db.query(models.MatchPlayer)
    if player_id is not None:
        matches_players = matches_players.filter(models.MatchPlayer.player_id == player_id)
    if match_id is not None:
        matches_players = matches_players.filter(models.MatchPlayer.match_id == match_id)
    return matches_players.order_by(desc(models.MatchPlayer.match_id)).offset(skip).limit(limit).all()


def get_match_player(db: Session, match_id: int, player_id: int):
    return db.query(models.MatchPlayer) \
        .filter(models.MatchPlayer.match_id == match_id, models.MatchPlayer.player_id == player_id).first()


def update_match_player(db: Session, match_id: int, player_id: int, match_player: schemas.MatchPlayer):
    desired_match_player = db.query(models.MatchPlayer) \
        .filter(models.MatchPlayer.match_id == match_id, models.MatchPlayer.player_id == player_id).first()
    desired_match_player.hero_id = match_player.hero_id
    db.add(desired_match_player)
    db.commit()
    db.refresh(desired_match_player)
    return desired_match_player


def delete_match_player(db: Session, match_id: int, player_id: int):
    db.query(models.MatchPlayer) \
        .filter(models.MatchPlayer.match_id == match_id, models.MatchPlayer.player_id == player_id).delete()
    db.commit()
    return
