import multiprocessing
from time import sleep
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status, Query
from sqlalchemy.orm import Session

import statistics
import crud
import deleteData
import models
import schemas
import uploadData
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

description = """
Dota2ProTracker Api helps you get dota2 statistics.

## Matches

You can: 

* **Create match**.
* **Read matches**.
* **Read match by id**.
* **Update match by id**.
* **Delete match by id**.

## Players

You can:

* **Create player**.
* **Read players**.
* **Read player by id**.
* **Update player by id**.
* **Delete player by id**.

## Heroes

You can:

* **Create hero**.
* **Read heroes**.
* **Read hero by id**.
* **Update hero by id**.
* **Delete hero by id**.

## Matches-Players

You can:

* **Create match-player**.
* **Read matches-players**.
* **Read matches-players by match id or/and player id**.
* **Update match-player by match id and player id**.
* **Delete match-player by match id and player id**.


## Matches-Info:

You can:

* **read matches-info**.
* **Read matches-info by player's nickname**.


## Player-Statistics:

You can:

* **read player-statistics, search by player's nickname and filter by different values**.
* **Read player-statistics by player's nickname**.


## Hero-Statistics:

You can:

* **read hero-statistics, search by hero's name and filter by different values**.
* **Read hero-statistics by hero's name**.
"""

app = FastAPI(
    title="Dota2ProTracker Api",
    description=description,
    version="0.1.0",
    contact={
        "name": "Laugh1Tale",
        "url": "https://github.com/Laugh1Tale",
        "email": "saharus@outlook.com",
    }
)


class FilterParams:
    def __init__(
            self,
            order_by: str = Query(default=None,
                                  description="You can set this parameter for filtering using any "
                                              "field of the response of this request in the format "
                                              "win-rate or win-rate-desc in case of decreasing. "
                                              "(it can also be specified in the format win_rate or "
                                              "win_rate_desc)."),
            then_by: str = Query(default=None,
                                 description="You can set this parameter for secondary filtering using any "
                                             "field of the response of this request in the format "
                                             "win-rate or win-rate-desc in case of decreasing. "
                                             "(it can also be specified in the format win_rate or win_rate_desc).")
    ):
        self.order_by = order_by
        self.then_by = then_by


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    t = multiprocessing.Process(target=update_data)
    t.start()
    t = multiprocessing.Process(target=delete_data)
    t.start()


def update_data():
    while True:
        uploadData.upload_data()
        sleep(300)


def delete_data():
    while True:
        deleteData.delete_data()
        sleep(300)


@app.post("/matches/", tags=["matches"], response_model=schemas.Match, status_code=status.HTTP_201_CREATED)
def create_match(match: schemas.Match, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id=match.id)
    if db_match:
        raise HTTPException(status_code=400, detail="Match already exist")
    return crud.create_match(db=db, match=match)


@app.get("/matches/", tags=["matches"], response_model=List[schemas.Match])
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches = crud.get_matches(db, skip=skip, limit=limit)
    return matches


@app.get("/matches/{match_id}", tags=["matches"], response_model=schemas.Match)
def read_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match


@app.put("/matches/{match_id}", tags=["matches"], response_model=schemas.Match)
def update_match(match_id: int, match: schemas.Match, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    db_match = crud.update_match(db, match_id, match)
    return db_match


@app.delete("/matches/{match_id}", tags=["matches"])
def delete_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    try:
        crud.delete_match(db, match_id)
    except Exception as e:
        raise HTTPException(status_code=403, detail="You can't delete a match")


@app.post("/players/", tags=["players"], response_model=schemas.Player, status_code=200)
def create_player(player: schemas.Player, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player.id)
    if db_player:
        raise HTTPException(status_code=400, detail="Player already exist")
    return crud.create_player(db=db, player=player)


@app.get("/players/", tags=["players"], response_model=List[schemas.Player], status_code=200)
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = crud.get_players(db, skip=skip, limit=limit)
    return players


@app.get("/players/{player_id}", tags=["players"], response_model=schemas.Player, status_code=200)
def read_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@app.put("/players/{player_id}", tags=["players"], response_model=schemas.Player)
def update_player(player_id: int, player: schemas.Player, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    db_player = crud.update_player(db, player_id, player)
    return db_player


@app.delete("/players/{player_id}", tags=["players"])
def delete_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    crud.delete_player(db, player_id)


@app.post("/heroes/", tags=["heroes"], response_model=schemas.Hero, status_code=200)
def create_hero(hero: schemas.Hero, db: Session = Depends(get_db)):
    db_hero = crud.get_hero(db, hero_id=hero.id)
    if db_hero:
        raise HTTPException(status_code=400, detail="Hero already exist")
    return crud.create_hero(db=db, hero=hero)


@app.get("/heroes/", tags=["heroes"], response_model=List[schemas.Hero], status_code=200)
def read_heroes(db: Session = Depends(get_db)):
    heroes = crud.get_heroes(db)
    return heroes


@app.get("/heroes/{hero_id}", tags=["heroes"], response_model=schemas.Hero, status_code=200)
def read_hero(hero_id: int, db: Session = Depends(get_db)):
    db_hero = crud.get_hero(db, hero_id=hero_id)
    if db_hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    return db_hero


@app.put("/heroes/{hero_id}", tags=["heroes"], response_model=schemas.Hero)
def update_hero(hero_id: int, hero: schemas.Hero, db: Session = Depends(get_db)):
    db_hero = crud.get_hero(db, hero_id=hero_id)
    if db_hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    db_hero = crud.update_hero(db, hero_id, hero)
    return db_hero


@app.delete("/heroes/{hero_id}", tags=["heroes"])
def delete_hero(hero_id: int, db: Session = Depends(get_db)):
    db_hero = crud.get_hero(db, hero_id=hero_id)
    if db_hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    crud.delete_hero(db, hero_id)


@app.post("/matches-players/", tags=["matches-players"], response_model=schemas.MatchPlayer)
def create_match_player(match_player: schemas.MatchPlayer, db: Session = Depends(get_db)):
    db_match_player = crud.get_match_player(db, match_id=match_player.match_id, player_id=match_player.player_id)
    if db_match_player:
        raise HTTPException(status_code=400, detail="Player already in match")
    return crud.create_match_player(db=db, match_player=match_player)


@app.get("/matches-players/", tags=["matches-players"], response_model=List[schemas.MatchPlayer])
def read_matches_players(match_id: int = None, player_id: int = None, skip: int = 0,
                         limit: int = 100, db: Session = Depends(get_db)):
    matches_players = crud.get_matches_players(db, match_id=match_id,
                                               player_id=player_id, skip=skip, limit=limit)
    return matches_players


@app.put("/matches-players/match/{match_id}/player/{player_id}/", tags=["matches-players"],
         response_model=schemas.MatchPlayer)
def update_match_player(match_id: int, player_id: int,
                        match_player: schemas.MatchPlayer, db: Session = Depends(get_db)):
    db_match_player = crud.get_match_player(db, match_id=match_id, player_id=player_id)
    if db_match_player is None:
        raise HTTPException(status_code=404, detail="Player not in match")
    db_match_player = crud.update_match_player(db, match_id=match_id, player_id=player_id, match_player=match_player)
    return db_match_player


@app.delete("/matches-players/match/{match_id}/player/{player_id}/", tags=["matches-players"])
def delete_match_player(match_id: int, player_id: int, db: Session = Depends(get_db)):
    db_match_player = crud.get_match_player(db, match_id=match_id, player_id=player_id)
    if db_match_player is None:
        raise HTTPException(status_code=404, detail="Player not in match")
    crud.delete_match_player(db, match_id=match_id, player_id=player_id)


@app.get("/matches-info/", tags=["matches-info"], response_model=List[schemas.MatchPlayerInfo])
def read_matches_info(find_player: str = None, find_hero: str = None,
                      skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches_info = statistics.get_matches_info(db, find_player=find_player, find_hero=find_hero, skip=skip, limit=limit)
    return matches_info


@app.get("/matches-info/player/{nickname}", tags=["matches-info"], response_model=List[schemas.MatchPlayerInfo])
def read_matches_info_by_player_nickname(nickname: str, db: Session = Depends(get_db)):
    matches_info = statistics \
        .get_matches_info_by_nickname(db, nickname=nickname)
    if matches_info is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return matches_info


@app.get("/players-statistics/", tags=["players-statistics"], response_model=List[schemas.PlayerStat])
def read_players_stat(params: FilterParams = Depends(), find: str = None,
                      skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players_stat = statistics.get_players_stat(db, order_by=params.order_by, find=find,
                                         then_by=params.then_by, skip=skip, limit=limit)
    return players_stat


@app.get("/players-statistics/{nickname}", tags=["players-statistics"], response_model=schemas.PlayerStat)
def read_player_stat_by_nickname(nickname: str, db: Session = Depends(get_db)):
    player_stat = statistics.get_player_stat_by_nickname(db, nickname=nickname)
    if player_stat is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player_stat


@app.get("/heroes-statistics/", tags=["heroes-statistics"], response_model=List[schemas.HeroStat])
def read_heroes_stat(params: FilterParams = Depends(),
                     find: str = None, db: Session = Depends(get_db)):
    heroes_stat = statistics.get_heroes_stat(db, order_by=params.order_by, then_by=params.then_by, find=find)
    return heroes_stat


@app.get("/heroes-statistics/{hero_name}", tags=["heroes-statistics"], response_model=schemas.HeroStat)
def read_hero_stat_by_hero_name(hero_name: str, db: Session = Depends(get_db)):
    hero_stat = statistics.get_hero_stat_by_hero_name(db, hero_name=hero_name)
    if hero_stat is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero_stat
