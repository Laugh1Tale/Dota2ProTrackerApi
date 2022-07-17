from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, PrimaryKeyConstraint, DateTime, Time
from database import Base


class Match(Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key=True)
    average_mmr = Column(Integer)
    pro_player_count = Column(Integer)
    match_duration = Column(Time)
    string_description = Column(String)
    match_time = Column(DateTime)


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    real_name = Column(String)
    win = Column(Integer, default=0)
    lose = Column(Integer, default=0)


class Hero(Base):
    __tablename__ = "hero"

    id = Column(Integer, primary_key=True)
    hero_name = Column(String)
    original_name = Column(String)
    win = Column(Integer, default=0)
    lose = Column(Integer, default=0)


class MatchPlayer(Base):
    __tablename__ = "match_player"
    __table_args__ = (
        PrimaryKeyConstraint('match_id', 'player_id'),
    )

    match_id = Column(Integer, ForeignKey(Match.id))
    player_id = Column(Integer, ForeignKey(Player.id))
    hero_id = Column(Integer, ForeignKey(Hero.id))
    is_victory = Column(Boolean)
