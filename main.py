from config import config
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from classes import InstagramMetricParser

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



def main():
    engine_121 = create_engine(f"mysql+pymysql://{db_username_121}:{db_password_121}@{db_url_121}:{db_port_121}/{db_name_121}", echo=False)
    engine_122 = create_engine(
        f"mysql+pymysql://{db_username_122}:{db_password_122}@{db_url_122}:{db_port_122}/{db_name_122}", echo=False)
    session_121 = Session(engine_121)
    session_122 = Session(engine_122)
    sessions = {"session_121": session_121, "session_122": session_122}
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 239.2.0.17.109 (iPhone12,1; iOS 15_5; en_US; en-US; scale=2.00; 828x1792; 376668393)'
    }
    proxies = {
        "https": f"socks5://94.247.130.58:5555",
        "http": f"socks5://94.247.130.58:5555",
    }
    insta = InstagramMetricParser(headers, sessions, proxies)
    insta.run()
    engine_121.dispose()
    engine_122.dispose()


if __name__ == "__main__":
    main()
