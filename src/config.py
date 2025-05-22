from configparser import ConfigParser
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class Login:
    username: str
    password: str

@dataclass
class Betting:
    minimum_bet: int
    game_link: str

@dataclass
class Behaviour:
    pause_min: int
    pause_max: int

@dataclass
class Sleep:
    start_time: str
    end_time: str

class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")
        
        self.login = self._get_login()
        self.betting = self._get_betting()
        self.behaviour = self._get_behaviour()
        self.sleep = self._get_sleep()

    def _get_login(self):
        return Login(
            username=self.config["LOGIN"]["username"],
            password=self.config["LOGIN"]["password"]
        )

    def _get_betting(self):
        return Betting(
            minimum_bet=int(self.config["BETTING"]["minimum_bet"]),
            game_link=self.config["BETTING"]["game_link"]
        )

    def _get_behaviour(self):
        return Behaviour(
            pause_min=int(self.config["BEHAVIOUR"]["pause_min"]),
            pause_max=int(self.config["BEHAVIOUR"]["pause_max"])
        )

    def _get_sleep(self):
        return Sleep(
            start_time=self.config["SLEEP"]["start_time"],
            end_time=self.config["SLEEP"]["end_time"]
        )
    
@lru_cache
def get_config():
    return Config()

if __name__ == "__main__":
    print(get_config().betting.minimum_bet)