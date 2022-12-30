import pytz
from sqlalchemy import update
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from sqlalchemy.orm import Query, Session
from utilities import serialize_result_to_list
from models.models import Resources, Posts, PostMetrics


class SocMetricParserAbstraction(ABC):
    def __init__(self, header: dict, db_session: dict[Session], proxy: dict, soc_type: int):
        self.headers = header
        self.cookie = None
        self.sessions: dict[Session] = db_session
        self.proxy = proxy
        self.profile_id = None
        self.s_date = None
        self.f_date = None
        self.soc_type = soc_type
        self.resource_list = self.get_resources_up_to_date()

    def __del__(self):
        for value in self.sessions.values():
            value.close()

    def update_resources_dates(self, res_id: int) -> None:
        self.sessions["session_121"].execute(
            update(Resources)
            .where(Resources.id == res_id)
            .values(met_finish_date=datetime.now(tz=pytz.timezone('Asia/Almaty')), type=self.soc_type)
        )

    def get_resources_up_to_date(self) -> list[tuple]:
        now = datetime.now(tz=pytz.timezone('Asia/Almaty'))
        hour_ago = now - timedelta(hours=1)
        resource_instance: Query = self.sessions["session_121"] \
            .query(Resources) \
            .where(Resources.met_finish_date < hour_ago,
                   Resources.type == self.soc_type)
        resource_list: list = serialize_result_to_list(resource_instance)
        return resource_list

    def add_post(self, post_object: Posts, post_metrics_object: PostMetrics) -> None:
        is_post_duplicated: bool = False
        post_list_statement: Query = self.sessions["session_121"].query(Posts).filter(Posts.type==self.soc_type)
        post_list: list = serialize_result_to_list(post_list_statement)
        for item in post_list:
            if item['item_id'] == post_object.item_id:
                is_post_duplicated = True
        if is_post_duplicated:
            self.sessions["session_121"].add(post_metrics_object)
            self.sessions["session_121"].commit()
        else:
            self.sessions["session_121"].add(post_object)
            self.sessions["session_121"].commit()
            self.sessions["session_121"].add(post_metrics_object)
            self.sessions["session_121"].commit()

    def add_relevant_posts(self, res_id, item_id, url, text, likes, comment, date, reposts=0):
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
        self.add_post(post_object, post_metrics_object)
        self.update_resources_dates(res_id)
        self.sessions["session_121"].commit()
        print(f"Post {item_id} added. Likes [{likes}]"
              f". Comments [{comment}]"
              f". Reposts [{reposts}]")

    @abstractmethod
    def parse_profile_metrics(self) -> None:
        pass

    @abstractmethod
    def parse_profile_posts(self, item: dict) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass