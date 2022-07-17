from pydantic import BaseModel
from datetime import datetime, time


class MatchBase(BaseModel):
    id: int
    average_mmr: int
    pro_player_count: int
    match_duration: time
    string_description: str
    match_time: datetime


class Match(MatchBase):

    class Config:
        orm_mode = True


class PlayerBase(BaseModel):
    id: int
    nickname: str
    win: int
    lose: int


class PlayerStat(PlayerBase):
    win_rate: float = None
    games_number: int


class Player(PlayerBase):
    real_name: str

    class Config:
        orm_mode = True


class HeroBase(BaseModel):
    id: int
    hero_name: str
    win: int
    lose: int


class HeroStat(HeroBase):
    win_rate: float
    games_number: int


class Hero(HeroBase):
    original_name: str

    class Config:
        orm_mode = True


class MatchPlayerBase(BaseModel):
    match_id: int
    is_victory: bool = None


class MatchPlayerInfo(MatchPlayerBase):
    nickname: str
    hero_name: str
    match_time: datetime


class MatchPlayer(MatchPlayerBase):
    player_id: int
    hero_id: int

    class Config:
        orm_mode = True
