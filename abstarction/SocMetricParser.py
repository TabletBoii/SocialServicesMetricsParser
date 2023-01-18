import logging
from logging import Logger
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pytz
from sqlalchemy import update
from sqlalchemy.orm import Query, Session
import tg_logger
from utilities import serialize_result_to_list
from models.models import Resources, Posts, PostMetrics, Proxy


class SocMetricParserAbstraction(ABC):
    """
        Abstraction for social network parsers.
    """

    def __init__(self, header: dict, db_session: dict[Session], soc_type: int):
        """
            inits SocMetricParserAbstaction with meta data and database session

            :param header: steady header value
            :type header: dict
            :param db_session: dictionary of specified sql alchemy sessions
            :type db_session: dict
            :param soc_type: type of social network specified in SocTypes enum
            :type soc_type: int
        """
        self.headers = header
        self.cookie = None
        self.sessions: dict[Session] = db_session
        self.proxy = None
        self.proxy_instance: Proxy = None
        self.profile_id = None
        self.s_date = None
        self.f_date = None
        self.soc_type = soc_type
        self.resource_list = self.get_resources_up_to_date()
        self.logger: Logger = None
        self.parsed_posts_counter = 0
        self.parsed_resources_counter = 0
        self.parsed_posts_metrics_counter = 0
        self.used_accounts = 0

    def __del__(self):
        """
            closing all sessions when an instance of a class is destroyed
        """
        for value in self.sessions.values():
            value.close()

    def update_resources_dates(self, res_id: int) -> None:
        """
            method which updates metric collection date

            :param header: steady header value
            :type header: dict
        """
        self.sessions["session_121"].execute(
            update(Resources)
            .where(Resources.id == res_id)
            .values(met_finish_date=datetime.now(tz=pytz.timezone('Asia/Almaty')),
                    type=self.soc_type)
        )

    def get_resources_up_to_date(self) -> list[tuple]:
        """
            method of obtaining resources for at least the last hour
            :return: list of resources that was updated more than an hour ago
        """
        now = datetime.now(tz=pytz.timezone('Asia/Almaty'))
        hour_ago = now - timedelta(hours=1)
        resource_instance: Query = self.sessions["session_121"] \
            .query(Resources) \
            .where(Resources.met_finish_date < hour_ago,
                   Resources.type == self.soc_type)
        resource_list: list = serialize_result_to_list(resource_instance)
        return resource_list

    def add_post(self,
                 post_object: Posts,
                 post_metrics_object: PostMetrics,
                 db_session: Session
                ) -> None:
        """
            a common method for all parsers that adds posts and post metrics to the database.

            :param header: steady header value
            :type header: dict
            :param db_session: dictionary of specified sql alchemy sessions
            :type db_session: dict
            :param soc_type: type of social network specified in SocTypes enum
            :type soc_type: int
        """
        is_post_duplicated: bool = False
        post_list_statement: Query = db_session.query(Posts).filter(Posts.type==self.soc_type)
        post_list: list = serialize_result_to_list(post_list_statement)
        for item in post_list:
            if item['item_id'] == post_object.item_id:
                is_post_duplicated = True
        if is_post_duplicated:
            db_session.add(post_metrics_object)
            db_session.commit()
            self.parsed_posts_metrics_counter += 1
        else:
            db_session.add(post_object)
            db_session.commit()
            db_session.add(post_metrics_object)
            db_session.commit()
            self.parsed_posts_metrics_counter += 1
            self.parsed_posts_counter += 1

    def add_relevant_posts(self,
                           res_id,
                           item_id,
                           url,
                           text,
                           likes,
                           comment,
                           date,
                           db_session: Session,
                           reposts=0) -> None:
        """
            A common method for all parsers that adds posts and post metrics to the database
            via add_post method and updates metric collection date.

            :param res_id: resource id received from database
            :type res_id: int
            :param item_id: item id received from social network API
            :type item_id: dict
            :param url: url of resource
            :type url: str
            :param text: content of post
            :type text: str
            :param likes: number of post likes received from social network API 
            :type likes: int
            :param comment: number of comments likes received from social network API 
            :type comment: int
            :param date: date then post was created
            :type date: string
            :param db_session: session taken from list of sql alchemy session
            :type db_session: Session
            :param reposts: number of reposts likes received from social network API 
            :type reposts: int
        """
        post_object = Posts(
            type=self.soc_type,
            res_id=res_id,
            item_id=item_id,
            url=url,
            text=text,
            date=date,
            s_date=datetime.now(),
            attachments='',
            sentiment=0
        )
        post_metrics_object = PostMetrics(
            type=self.soc_type,
            res_id=res_id,
            url=url,
            item_id=item_id,
            date=date,
            s_date=datetime.now(),
            likes=likes,
            comments=comment,
            reposts=reposts,
        )
        self.add_post(post_object, post_metrics_object, db_session)
        self.update_resources_dates(res_id)
        db_session.commit()
        print(f"Post {item_id} added. Likes [{likes}]"
              f". Comments [{comment}]"
              f". Reposts [{reposts}]")

    def telegram_logger_init(self, token, user_list):
        """
            Method using tg_logger module to create logger attribute

            :param token: api token of telegram bot
            :type token: str
            :param user_list: list of user chat ids
            :type user_list: int
        """
        # Base logger
        logger = logging.getLogger(f"{self.soc_type}")
        logger.setLevel(logging.INFO)

        # Logging bridge setup
        tg_logger.setup(logger, token=token, users=user_list)

        self.logger = logger

    def send_statistic_to_telegram(self):
        """
            The method that the tg_logger module uses to send a message to the telegram bot
        """
        self.logger.info(
            """
                \n
                Parsed resources number: %s |\n
                Parsed posts number: %s |\n
                Parsed posts metrics number: %s |\n
                Used accounts: %s |\n
             """, str(self.parsed_resources_counter),
                  str(self.parsed_posts_counter),
                  str(self.parsed_posts_metrics_counter),
                  str(self.used_accounts)
        )

    @abstractmethod
    def set_proxy(self) -> None:
        """
            An abstract method responsible for passing
            to self.proxy a dictionary with a link to an authenticated proxy server.
        """
        pass

    @abstractmethod
    def parse_profile_metrics(self) -> None:
        """
            An abstract method responsible for different method of parsing profile metrics via social services api
        """
        pass

    @abstractmethod
    def parse_profile_posts(self, item: dict) -> None:
        """
            An abstract method responsible for different method of parsing posts metrics via social services api

            :param item: single post from posts list
            :type item: dict
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """
            method for running the parser
        """
        pass
