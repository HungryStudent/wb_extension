from pydantic import BaseModel
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN = config["settings"]["TOKEN"]
ADMINS = config["settings"]["admins"].split(",")
ADMINS = [int(admin) for admin in ADMINS]


class DB(BaseModel):
    user = config["db"]["user"]
    password = config["db"]["password"]
    database = config["db"]["database"]
    host = config["db"]["host"]
    port = config["db"]["port"]


SQLALCHEMY_DATABASE_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(**DB().dict())
