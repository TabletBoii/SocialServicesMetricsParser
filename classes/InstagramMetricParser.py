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


class InstagramMetricParser:

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

    def __get_instagram_accounts_cookie(self):
        available_cookies: Accounts = self.session_122.execute(
            select(Accounts)
            .where(Accounts.soc_type == 4, Accounts.type == "INST_METRIC_PARSER", Accounts.work == 1)
        ).fetchone()[0]
        self.cookie = {'sessionid': available_cookies.sessionid}

    def update_session(self):
        self.session_122.execute(
            update(Accounts)
            .where(Accounts.sessionid == self.cookie)
            .values(Accounts.work == 0)
        )
        self.__get_instagram_accounts_cookie()

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

    def parse_profile_metrics(self, item: dict) -> None:
        parsed_username = urlparse(item['url'])
        parsed_username = re.sub('/', '', str(parsed_username.path))
        profile_json_info: dict = dict()
        while True:
            try:
                profile_json_info = serialize_response_to_json(
                    f'https://i.instagram.com/api/v1/users/web_profile_info/?username={parsed_username}',
                    self.cookie,
                    self.headers,
                    self.proxy)
                break
            except JSONDecodeError:
                print("Either the account is banned, or fuck Alibek.")
                self.update_session()
                continue

        self.s_date = item['s_date']
        self.f_date = item['f_date']
        profile_followers: int = profile_json_info['data']['user']['edge_followed_by']['count']
        profile_follow: int = profile_json_info['data']['user']['edge_follow']['count']

        last_date_updated = self.session_121.execute(
            select(ResourceMetrics.date)
            .filter(ResourceMetrics.type == 4, ResourceMetrics.res_id == item['id'])
            .order_by(desc(ResourceMetrics.date))
            .limit(2)
        ).all()

        if len(item["owner_id"]) <= 2:
            self.session_121.execute(
                update(Resources)
                .where(Resources.id == item['id'])
                .values(owner_id=profile_json_info['data']['user']['id']))

        if len(last_date_updated) == 0 or last_date_updated[0][0] < datetime.date.today():
            insert_object = [
                ResourceMetrics(
                    type=4,
                    res_id=item['id'],
                    sf_type='members',
                    count=profile_followers,
                    date=datetime.date.today()
                ),
                ResourceMetrics(
                    type=4,
                    res_id=item['id'],
                    sf_type='friends',
                    count=profile_follow,
                    date=datetime.date.today()
                )
            ]
            print("Getting metrics of resource ", item['url'])
            print("Followers: ", profile_followers)
            print("Follows: ", profile_follow)
            self.session_121.bulk_save_objects(insert_object)
            self.session_121.commit()
        print(f"Resource {item['url']} is up-to-date")
        profile_id = profile_json_info['data']['user']['id']
        self.profile_id = profile_id

    def parse_profile_posts(self, item: dict) -> None:
        profile_cursor = ''
        while True:
            resource_posts: dict = dict()
            while True:
                try:
                    resource_posts: dict = serialize_response_to_json(
                        f'https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B"id":{self.profile_id}, "first": "50", "after": "{profile_cursor}"%7D',
                        self.cookie,
                        self.headers,
                        self.proxy)
                    break
                except JSONDecodeError:
                    print("Either the account is banned, or fuck Alibek.")
                    self.update_session()
                    continue
            # If data keyword error then account was banned
            number_of_posts_per_cursor = resource_posts['data']['user']['edge_owner_to_timeline_media']['count']
            if number_of_posts_per_cursor == 0:
                print('No posts')
                break
            posts = resource_posts['data']['user']['edge_owner_to_timeline_media']['edges']
            s_date_unixtime = time.mktime(datetime.datetime.strptime(item['s_date'], "%Y-%m-%d").timetuple())
            f_date_unixtime = (datetime.datetime.fromtimestamp(
                time.mktime(datetime.datetime.strptime(item['f_date'], "%Y-%m-%d").timetuple())) + datetime.timedelta(
                days=1)).timestamp()
            in_between_dates_posts = []
            for post in posts:
                if s_date_unixtime <= post['node']['taken_at_timestamp'] <= f_date_unixtime:
                    in_between_dates_posts.append(post)
            if posts[len(posts) - 1]['node']['taken_at_timestamp'] >= f_date_unixtime:
                profile_cursor = resource_posts['data']['user']['edge_owner_to_timeline_media']['page_info'][
                    'end_cursor']
                continue
            if len(in_between_dates_posts) == 0:
                break

            for post in in_between_dates_posts:
                if len(post['node']['edge_media_to_caption']['edges']) == 0:
                    text = ''
                else:
                    text = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
                post_object = Posts(
                    type=4,
                    res_id=item['id'],
                    item_id=post['node']['id'],
                    url=f"https://www.instagram.com/p/{post['node']['shortcode']}/",
                    text=text,
                    date=datetime.datetime.utcfromtimestamp(post['node']['taken_at_timestamp']).strftime(
                        '%Y-%m-%d'),
                    s_date=datetime.datetime.now(),
                    attachments='',
                    sentiment=0
                )
                post_metrics_object = PostMetrics(
                    type=4,
                    res_id=item['id'],
                    url=f"https://www.instagram.com/p/{post['node']['shortcode']}/",
                    item_id=post['node']['id'],
                    date=datetime.datetime.utcfromtimestamp(post['node']['taken_at_timestamp']).strftime(
                        '%Y-%m-%d'),
                    s_date=datetime.datetime.now(),
                    likes=post['node']['edge_media_preview_like']['count'],
                    comments=post['node']['edge_media_to_comment']['count'],
                    reposts=0,
                )
                self.add_post(post_object, post_metrics_object)
                self.session_121.execute(
                    update(Resources)
                    .where(Resources.id == item['id'])
                    .values(met_finish_date=datetime.datetime.now(tz=pytz.timezone('Asia/Almaty')))
                )
                print(f"Post {post['node']['id']} added. Likes [{post['node']['edge_media_preview_like']['count']}]"
                      f". Comments [{post['node']['edge_media_to_comment']['count']}]")
            if number_of_posts_per_cursor >= 50:
                profile_cursor = resource_posts['data']['user']['edge_owner_to_timeline_media']['page_info'][
                    'end_cursor']
                continue
            break

    def run(self) -> None:
        for item in self.resource_list:
            self.__get_instagram_accounts_cookie()
            self.parse_profile_metrics(item)
            self.parse_profile_posts(item)
            self.update_resources_dates(item['id'])

    def __repr__(self):
        return str(self.resource_list)
