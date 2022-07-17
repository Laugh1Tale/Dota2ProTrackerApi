from sqlalchemy import desc, func, case
from sqlalchemy.orm import Session

import models


def get_matches_info(db: Session, find_player: str = None, find_hero: str = None,
                     skip: int = 0, limit: int = 100):
    records = \
        db.query(models.MatchPlayer.match_id, models.Player.nickname,
                 models.Hero.hero_name, models.Match.match_time, models.MatchPlayer.is_victory) \
            .join(models.Match) \
            .join(models.Player) \
            .join(models.Hero).order_by(desc(models.Match.match_time))
    if find_player is not None:
        records = records.filter(models.Player.nickname.ilike(f'%{find_player}%'))
    if find_hero is not None:
        records = records.filter(models.Hero.hero_name.ilike(f'%{find_hero}%'))
    return records.offset(skip).limit(limit).all()


def get_matches_info_by_nickname(db: Session, nickname: str, skip: int = 0, limit: int = 100):
    records = \
        db.query(models.MatchPlayer.match_id, models.Player.nickname,
                 models.Hero.hero_name, models.Match.match_time, models.MatchPlayer.is_victory) \
            .join(models.Match) \
            .join(models.Player) \
            .join(models.Hero) \
            .filter(func.lower(models.Player.nickname) == func.lower(nickname)) \
            .order_by(desc(models.Match.match_time)).offset(skip).limit(limit).all()
    return records


def get_players_stat(db: Session, find: str = None, order_by: str = None,
                     then_by: str = None, skip: int = 0, limit: int = 100):
    records = db.query(models.Player.id, models.Player.nickname, models.Player.win, models.Player.lose,
                       (models.Player.win + models.Player.lose).label("games_number"),
                       case([(models.Player.win == 0, 0.0)],
                            else_=(models.Player.win * 1.0 / (models.Player.win + models.Player.lose)) * 100) \
                       .label("win_rate"))
    if find is not None:
        records = records.filter(models.Player.nickname.ilike(f'%{find}%'))
    if order_by is not None:
        order_by = desc(order_by[:-5].replace('-', '_')) if order_by[-4:] == "desc" \
            else order_by.replace('-', '_')
        records = records.order_by(order_by)
    if then_by is not None:
        then_by = desc(then_by[:-5].replace('-', '_')) if then_by[-4:] == "desc" \
            else then_by.replace('-', '_')
        records = records.order_by(then_by)
    return records.offset(skip).limit(limit).all()


def get_player_stat_by_nickname(db: Session, nickname: str):
    record = db.query(models.Player.id, models.Player.nickname, models.Player.win, models.Player.lose,
                      (models.Player.win + models.Player.lose).label("games_number"),
                      case([(models.Player.win == 0, 0.0)],
                           else_=(models.Player.win * 1.0 / (models.Player.win + models.Player.lose)) * 100) \
                      .label("win_rate")) \
        .filter(func.lower(models.Player.nickname) == func.lower(nickname)) \
        .first()
    return record


def get_heroes_stat(db: Session, find: str, order_by: str = None,
                    then_by: str = None):
    records = db.query(models.Hero.id, models.Hero.hero_name, models.Hero.win, models.Hero.lose,
                       (models.Hero.win + models.Hero.lose).label("games_number"),
                       case([(models.Hero.win == 0, 0.0)],
                            else_=(models.Hero.win * 1.0 / (models.Hero.win + models.Hero.lose)) * 100) \
                       .label("win_rate"))
    if find is not None:
        records = records.filter(models.Hero.hero_name.ilike(f'%{find}%'))
    if order_by is not None:
        order_by = desc(order_by[:-5].replace('-', '_')) if order_by[-4:] == "desc" \
            else order_by.replace('-', '_')
        records = records.order_by(order_by)
    if then_by is not None:
        then_by = desc(then_by[:-5].replace('-', '_')) if then_by[-4:] == "desc" \
            else then_by.replace('-', '_')
        records = records.order_by(then_by)
    return records.all()


def get_hero_stat_by_hero_name(db: Session, hero_name: str):
    record = db.query(models.Hero.id, models.Hero.hero_name, models.Hero.win, models.Hero.lose,
                      (models.Hero.win + models.Hero.lose).label("games_number"),
                      case([(models.Hero.win == 0, 0.0)],
                           else_=(models.Hero.win * 1.0 / (models.Hero.win + models.Hero.lose)) * 100) \
                      .label("win_rate")) \
        .filter(func.lower(models.Hero.hero_name) == func.lower(hero_name)) \
        .first()
    return record
