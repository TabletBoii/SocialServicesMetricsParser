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



def instagram_parser_run():
    engine_121 = create_engine(f"mysql+pymysql://{db_username_121}:{db_password_121}@{db_url_121}:{db_port_121}/{db_name_121}", echo=False)
    engine_122 = create_engine(
        f"mysql+pymysql://{db_username_122}:{db_password_122}@{db_url_122}:{db_port_122}/{db_name_122}", echo=False)
    session_121 = Session(engine_121)
    session_122 = Session(engine_122)
    sessions = {"session_121": session_121, "session_122": session_122}
    headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US;     en-US; scale=2.00     ; 828x1792; 190542906)'}
    #headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'}
    #proxies = {
    #    "https": f"socks5://94.247.130.58:5555",
    #    "http": f"socks5://94.247.130.58:5555",
    #}
    proxies = {
        'https': 'http://indy361890:Xitv6136rN@185.156.178.105:20420'
    }
    insta = InstagramMetricParser(headers, sessions, proxies, soc_type=SocialEnum.instagram.value)
    insta.run()
    engine_121.dispose()
    engine_122.dispose()


def test():
    engine_121 = create_engine(
        f"mysql+pymysql://{db_username_121}:{db_password_121}@{db_url_121}:{db_port_121}/{db_name_121}", echo=False)
    session_121 = Session(engine_121)
    sessions = {"session_121": session_121}
    headers = {
        "User-Agent": "v2UserLookupPython"
    }
    proxies = {
        "https": f"socks5://94.247.130.58:5555",
        "http": f"socks5://94.247.130.58:5555",
    }
    tw_parser = TwitterMetricParser(headers, sessions, proxies, SocialEnum.twitter.value)
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
    instagram_parser_run()
