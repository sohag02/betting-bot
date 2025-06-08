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
class Demo:
    enabled: bool
    assumed_balance: int

@dataclass
class Behaviour:
    pause_min: int
    pause_max: int

@dataclass
class Sleep:
    start_time: str
    end_time: str

@dataclass
class Notification:
    balance_threshold: int
    loss_streak_threshold: int
    
@dataclass
class Telegram:
    api_id: str
    api_hash: str
    bot_token: str
    admin_username: str

class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")
        
        self.login = self._get_login()
        self.betting = self._get_betting()
        self.demo = self._get_demo()
        self.behaviour = self._get_behaviour()
        self.sleep = self._get_sleep()
        self.notification = self._get_notification()
        self.telegram = self._get_telegram()

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

    def _get_demo(self):
        return Demo(
            enabled=self.config.getboolean("DEMO", "enabled"),
            assumed_balance=int(self.config["DEMO"]["assumed_balance"])
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
    
    def _get_notification(self):
        return Notification(
            balance_threshold=int(self.config["NOTIFICATION"]["balance_threshold"]),
            loss_streak_threshold=int(self.config["NOTIFICATION"]["loss_streak_threshold"])
        )

    def _get_telegram(self):
        return Telegram(
            api_id=self.config["TELEGRAM"]["api_id"],
            api_hash=self.config["TELEGRAM"]["api_hash"],
            bot_token=self.config["TELEGRAM"]["bot_token"],
            admin_username=self.config["TELEGRAM"]["admin_username"]
        )
    
@lru_cache
def get_config():
    return Config()

if __name__ == "__main__":
    print(get_config().betting.minimum_bet)