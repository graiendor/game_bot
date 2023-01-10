import logging
import sqlite3
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ORM.Tables import Locations

def load_map():
    """Загружает карту из файла"""
    sqlite3.connect('data/game.db')
    sql = create_engine('sqlite:///data/game.db')
    session = sessionmaker(bind=sql)()

    Locations.metadata.create_all(sql)

    with open('data/map.json', 'r', encoding='utf-8') as file:
        locations = json.load(file)['members']
    try:
        for location in locations:
            session.add(Locations(id=location['id'], name=location['name'], description=location['description'],
                                  linkUp=location['linkUp'], linkDown=location['linkDown'], linkLeft=location['linkLeft'],
                                  linkRight=location['linkRight']))
            session.commit()
    except Exception as e:
        session.rollback()

    session.close()