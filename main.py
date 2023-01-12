from multiprocessing import Process

from config import config
from enums import SocialEnum
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from classes import InstagramMetricParser, TwitterMetricParser


db_username_121: str = config['DATABASES']['MYSQL']['MYSQL.121']['user']
db_password_121: str = config['DATABASES']['MYSQL']['MYSQL.121']['passwd']
db_url_121: str = config['DATABASES']['MYSQL']['MYSQL.121']['host']
db_port_121: int = config['DATABASES']['MYSQL']['MYSQL.121']['port']
db_name_121: str = config['DATABASES']['MYSQL']['MYSQL.121']['db']

db_username_122: str = config['DATABASES']['MYSQL']['MYSQL.122']['user']
db_password_122: str = config['DATABASES']['MYSQL']['MYSQL.122']['passwd']
db_url_122: str = config['DATABASES']['MYSQL']['MYSQL.122']['host']
db_port_122: int = config['DATABASES']['MYSQL']['MYSQL.122']['port']
db_name_122: str = config['DATABASES']['MYSQL']['MYSQL.122']['db']

db_username_52: str = config['DATABASES']['MYSQL']['MYSQL.52']['user']
db_password_52: str = config['DATABASES']['MYSQL']['MYSQL.52']['passwd']
db_url_52: str = config['DATABASES']['MYSQL']['MYSQL.52']['host']
db_port_52: int = config['DATABASES']['MYSQL']['MYSQL.52']['port']
db_name_52: str = config['DATABASES']['MYSQL']['MYSQL.52']['db']


def instagram_parser_run():
    engine_121 = create_engine(
        f"mysql+pymysql://{db_username_121}:{db_password_121}@{db_url_121}:{db_port_121}/{db_name_121}", echo=False
    )
    engine_122 = create_engine(
        f"mysql+pymysql://{db_username_122}:{db_password_122}@{db_url_122}:{db_port_122}/{db_name_122}", echo=False
    )
    engine_52 = create_engine(
        f"mysql+pymysql://{db_username_52}:{db_password_52}@{db_url_52}:{db_port_52}/{db_name_52}", echo=False
    )

    session_121 = Session(engine_121)
    session_122 = Session(engine_122)
    session_52 = Session(engine_52)

    sessions = {"session_121": session_121, "session_122": session_122, "session_52": session_52}
    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US;     en-US; scale=2.00     ; 828x1792; 190542906)'}

    insta = InstagramMetricParser(headers, sessions, soc_type=SocialEnum.instagram.value)
    insta.run()
    engine_121.dispose()
    engine_122.dispose()


def twitter_parser_run():
    engine_121 = create_engine(
        f"mysql+pymysql://{db_username_121}:{db_password_121}@{db_url_121}:{db_port_121}/{db_name_121}", echo=False
    )

    session_121 = Session(engine_121)
    
    sessions = {"session_121": session_121}
    headers = {
        "User-Agent": "v2UserLookupPython"
    }
    tw_parser = TwitterMetricParser(headers, sessions, SocialEnum.twitter.value)
    tw_parser.run()
    engine_121.dispose()


def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()


if __name__ == "__main__":
    runInParallel(instagram_parser_run, twitter_parser_run)
