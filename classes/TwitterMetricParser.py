import re
import time
import pytz
import datetime
from sqlalchemy import desc
from json import JSONDecodeError
from urllib.parse import urlparse
from sqlalchemy import select, update
from sqlalchemy.orm import session, Query
from models.models import Resources, ResourceMetrics, Posts, PostMetrics, Accounts
from utilities.Utilities import serialize_result_to_list, serialize_response_to_json


class TwitterMetricParser:
    def __init__(self, header: dict, db_session: list[session.Session, session.Session], proxy: dict):
        self.headers = header
        self.cookie = None
        self.session_121: session.Session = db_session['session_121']
        self.session_122: session.Session = db_session['session_122']
        self.proxy = proxy
        self.resource_list = self.get_resources_up_to_date()
        self.profile_id = None
        self.s_date = None
        self.f_date = None

    def __del__(self):
        self.session_121.close()
        self.session_122.close()

    def update_resources_dates(self, res_id: int) -> None:
        self.session_121.execute(
            update(Resources)
            .where(Resources.id == res_id)
            .values(met_finish_date=datetime.datetime.now(tz=pytz.timezone('Asia/Almaty')))
        )

    def get_resources_up_to_date(self) -> list[tuple]:
        now = datetime.datetime.now(tz=pytz.timezone('Asia/Almaty'))
        hour_ago = now - datetime.timedelta(hours=1)
        resource_instance: Query = self.session_121\
            .query(Resources)\
            .where(Resources.met_finish_date < hour_ago,
                   Resources.type == 4)
        resource_list: list = serialize_result_to_list(resource_instance)
        return resource_list

    def add_post(self, post_object: Posts, post_metrics_object: PostMetrics) -> None:
        is_post_duplicated: bool = False
        post_list_statement: Query = self.session_121.query(Posts)
        post_list: list = serialize_result_to_list(post_list_statement)

        for item in post_list:
            if item['item_id'] == post_object.item_id:
                is_post_duplicated = True
        if is_post_duplicated:
            self.session_121.add(post_metrics_object)
            self.session_121.commit()
        else:
            self.session_121.add(post_object)
            self.session_121.commit()
            self.session_121.add(post_metrics_object)
            self.session_121.commit()