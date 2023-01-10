import logging
import random
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from classes.Protagonist import Protagonist
from classes.NPC import NPC
from classes.Enemy import Enemy
from classes.Direction import Direction
from ORM.Tables import *

import random

class Controller:
    def __init__(self, db_name: str):
        self.connection = sqlite3.connect(f'data/{db_name}')
        self.sql = create_engine(f'sqlite:///data/{db_name}')
        self.session = sessionmaker(bind=self.sql)()
        self.protagonist = None
        self.names = ['Bob', 'Alice', 'Alex', 'Liza', 'Gosha', 'Maksim', 'Nikita', 'John', 'Anakin', 'Luke',
                      'Dart', 'Vader', 'Palpatin', 'Asoka', 'Naruto', 'Sasha', 'Masha', 'Petya', 'Vasya', 'Kolya',
                      'Sveta', 'Katya', 'Misha', 'Dima', 'Vova', 'Sasha', 'Masha', 'Petya', 'Vasya', 'Kolya',
                      'Tim', 'Tom', 'Jerry', 'Mickey', 'Donald', 'Goofy', 'Pluto', 'Minnie', 'Daisy', 'Minnie',
                      'Leya', 'Boba', 'Fett', 'Jango', 'Dooku', 'Yoda', 'Obi-Wan', 'Qui-Gon', 'Hutt', 'Jabba',
                      'Jar-Jar', 'Binks', 'R2-D2', 'C-3PO', 'Chewbacca', 'Han', 'Leia', 'Luke', 'Lando', 'Calrissian',
                      'Padme', 'Amidala', 'Anakin', 'Skywalker', 'Mace', 'Windu', 'Palpatin', 'Darth', 'Sidious',]

    def start_game(self, telegram_id: str, new: bool = False):
        """Запускает игру"""
        logging.info('Запуск игры для пользователя ' + str(telegram_id))
        if new:
            logging.info('Удаление старого персонажа')
            self.session.query(ProtagonistTable).filter(ProtagonistTable.telegram_id == telegram_id).delete()
            self.session.commit()
        self.protagonist = Protagonist(random.choice(self.names), telegram_id)
        logging.info('Игра запущена')
        self.protagonist.save_protagonist()

    def get_location(self, ob, id: int):
        """Возвращает локацию"""
        try:
            if ob == ProtagonistTable:
                logging.info('Получение локации персонажа')
                ob.id = id
                location = self.session.query(ob).filter(ob.id == id).first().location
                return self.session.query(Locations).filter(Locations.id == location).first()
        except AttributeError:
            logging.error('Персонаж не найден')
            return None

    def get_npc(self, id: int):
        """Возвращает NPC"""
        try:
            logging.info('Получение NPC')
            npc = self.session.query(NPCTable).filter(NPCTable.id == id).first()
            logging.info('NPC получен')
            return npc
        except AttributeError:
            logging.error('NPC не найден')
            return None

    def get_enemy(self, id: int):
        """Возвращает врага"""
        try:
            logging.info('Получение врага')
            enemy = self.session.query(EnemyTable).filter(EnemyTable.id == id).first()
            logging.info('Враг получен')
            return enemy
        except AttributeError:
            logging.error('Враг не найден')
            return None

    def get_npc_inventory(self, id: int):
        """Возвращает инвентарь NPC"""
        try:
            logging.info('Получение инвентаря NPC')
            npc = self.session.query(NPCTable).filter(NPCTable.id == id).first()
            logging.info('Инвентарь NPC получен')
            return npc.inventory
        except AttributeError:
            logging.error('Инвентарь NPC не найден')
            return None

    def get_protagonist_inventory(self, id: int):
        """Возвращает инвентарь персонажа"""
        try:
            logging.info('Получение инвентаря персонажа')
            inventory = self.session.query(ProtagonistInventoryTable).filter(ProtagonistInventoryTable.character_id == id).first()
            return inventory
        except AttributeError:
            logging.error('Инвентарь персонажа не найден')
            return None

    def get_inventory_item(self, id: int):
        """Возвращает предмет инвентаря"""
        try:
            logging.info('Получение предмета инвентаря')
            inventory_item = self.session.query(InventoryItemsTable).filter(InventoryItemsTable.id == id).first()
            logging.info('Предмет инвентаря получен')
            return inventory_item
        except AttributeError:
            logging.error('Предмет инвентаря не найден')
            return None

    def get_npc_phrases(self, id: int):
        """Возвращает фразы NPC"""
        try:
            logging.info('Получение фраз NPC')
            npc = NPC(id)
            phrases = npc.load_phrases(NPCPhraseTable, npc.id)
            logging.info('Фразы NPC получены')
            return phrases
        except AttributeError:
            logging.error('Фразы NPC не найдены')
            return None

    def get_enemy_phrases(self, id: int):
        """Возвращает фразу врага"""
        try:
            logging.info('Получение фразы врага')
            enemy = Enemy(id)
            phrases = enemy.load_phrases(EnemyPhraseTable, enemy.id)
            logging.info('Фраза врага получена')
            return phrases
        except AttributeError:
            logging.error('Фраза врага не найдена')
            return None

    def attack_enemy(self, id: int):
        """Сражаться с врагом"""
        try:
            logging.info("Начало сражения")
            enemy = Enemy(id)
            kill_enemy, phrases = self.protagonist.attack(enemy)
            logging.info("Фразы получены")
            if kill_enemy:
                logging.info("Враг убит")
            return kill_enemy, phrases
        except Exception as e:
            logging.error("Сражение прервано")
            raise e


    def get_npc_in_location(self, location_id):
        """Возвращает NPC в локации"""
        try:
            logging.info('Получение NPC в локации')
            npc = self.session.query(NPCTable).filter(NPCTable.location == location_id).all()
            logging.info('NPC в локации получен')
            return npc
        except AttributeError:
            logging.error('NPC в локации не найден')
            return None

    def get_enemy_in_location(self, location_id):
        """Возвращает врага в локации"""
        try:
            logging.info('Получение врага в локации')
            enemy = self.session.query(EnemyTable).filter(EnemyTable.location == location_id).all()
            logging.info('Враг в локации получен')
            return enemy
        except AttributeError:
            logging.error('Враг в локации не найден')
            return None

    def get_locations_to_go(self):
        """Возвращает локации, куда можно пойти"""
        try:
            self.protagonist.locations.check()
            links = self.protagonist.locations.link
            locations = []
            for link in links:
                location = self.session.query(Locations).filter(Locations.id == link).first()
                if location:
                    locations.append(location)
            return locations
        except AttributeError:
            logging.error('Нет доступных локаций')
            return None

    def get_protagonist_info(self, id: int):
        """Возвращает информацию о персонаже"""
        try:
            logging.info("Получение информации о персонаже")
            info = self.session.query(ProtagonistTable).filter(ProtagonistTable.telegram_id == id).first()
            return info
        except Exception as e:
            logging.error("Персонаж не создан")
            return None


    def go(self, location: Locations):
        self.protagonist.go(Direction(location.id))

    def get_current_location(self):
        return self.protagonist.locations

    def interact(self, npc_id):
        npc = self.session.query(NPCTable).filter(NPCTable.id == npc_id).first()
        if npc.npc_type == 1:
            self.protagonist.heal()
            return (None, 'You are healed, your health is now ' + str(self.protagonist.hp))
        elif npc.npc_type == 2:
            return (None, "I can't trade")
        elif npc.npc_type == 3:
            return (None, 'You must obliterate younlings!') if self.session.query(EnemyTable).count() > 0 else (True, 'You are the best')
        else:
            return (None, self.protagonist.talk_to(npc))

    def end_game(self):
        self.session.query(ProtagonistTable).filter(ProtagonistTable.telegram_id == self.protagonist.telegram_id).delete()
        self.session.query(ProtagonistInventoryTable).filter(ProtagonistInventoryTable.character_id == self.protagonist.id).delete()