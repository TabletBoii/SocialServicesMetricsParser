import time
from abc import ABC
from sqlalchemy import desc
from sqlalchemy import select, update
from datetime import datetime, date, timedelta
from abstarction import SocMetricParserAbstraction
from models.models import Resources, ResourceMetrics, Accounts
from utilities.Utilities import serialize_response_to_json, parse_username_from_url


class InstagramMetricParser(SocMetricParserAbstraction, ABC):

    def __init__(self, header: dict, db_session: dict, proxy: dict, soc_type: int):
        super().__init__(header, db_session, proxy, soc_type)

    def __get_instagram_accounts_cookie(self):
        available_cookies: Accounts = self.sessions["session_122"].execute(
            select(Accounts)
            .where(Accounts.soc_type == 4, Accounts.type == "INST_METRIC_PARSER", Accounts.work == 1)
        ).fetchone()[0]
        self.cookie = {'sessionid': available_cookies.sessionid}

    def update_session(self):
        self.sessions["session_122"].execute(
            update(Accounts)
            .where(Accounts.sessionid == self.cookie['sessionid'])
            .values(work=0)
        )
        self.sessions["session_122"].commit()
        self.__get_instagram_accounts_cookie()

    def response_by_url(self, url) -> dict:
        while True:
            resource_posts: dict = serialize_response_to_json(
                url,
                cookies=self.cookie,
                headers=self.headers,
                proxies=self.proxy)

            if not isinstance(resource_posts, dict):
                print("Either the account is banned, or fuck Alibek.")
                self.update_session()
                continue

            if resource_posts['status'] == 'fail':
                print("Either the account is banned, or fuck Alibek.")
                self.update_session()
                continue

            return resource_posts

    def parse_profile_metrics(self, item: dict) -> None:
        parsed_username = parse_username_from_url(item['url'])
        get_resources_url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={parsed_username}'
        profile_json_info = self.response_by_url(get_resources_url)
        # print(profile_json_info)
        self.s_date = item['s_date']
        self.f_date = item['f_date']
        profile_followers: int = profile_json_info['data']['user']['edge_followed_by']['count']
        profile_follow: int = profile_json_info['data']['user']['edge_follow']['count']

        last_date_updated = self.sessions["session_121"].execute(
            select(ResourceMetrics.date)
            .filter(ResourceMetrics.type == self.soc_type, ResourceMetrics.res_id == item['id'])
            .order_by(desc(ResourceMetrics.date))
            .limit(2)
        ).all()

        if len(item["owner_id"]) == '':
            self.sessions["session_121"].execute(
                update(Resources)
                .where(Resources.id == item['id'])
                .values(owner_id=profile_json_info['data']['user']['id']))

        if len(last_date_updated) == 0 or last_date_updated[0][0] < date.today():
            insert_object = [
                ResourceMetrics(
                    type=self.soc_type,
                    res_id=item['id'],
                    sf_type='members',
                    count=profile_followers,
                    date=date.today()
                ),
                ResourceMetrics(
                    type=self.soc_type,
                    res_id=item['id'],
                    sf_type='friends',
                    count=profile_follow,
                    date=date.today()
                )
            ]
            print("Getting metrics of resource ", item['url'])
            print("Followers: ", profile_followers)
            print("Follows: ", profile_follow)
            self.sessions["session_121"].bulk_save_objects(insert_object)
            self.sessions["session_121"].commit()
        print(f"Resource {item['url']} is up-to-date")
        profile_id = profile_json_info['data']['user']['id']
        self.profile_id = profile_id

    def parse_profile_posts(self, item: dict) -> None:
        profile_cursor = ''
        while True:
            get_posts_url = f'https://www.instagram.com/graphql/query/?' \
                            f'query_id=17888483320059182&' \
                            f'variables=%7B"id":{self.profile_id}, "first": "50", "after": "{profile_cursor}"%7D'
            resource_posts = self.response_by_url(get_posts_url)
            number_of_posts_per_cursor = resource_posts['data']['user']['edge_owner_to_timeline_media']['count']
            if number_of_posts_per_cursor == 0:
                print('No posts')
                break
            posts = resource_posts['data']['user']['edge_owner_to_timeline_media']['edges']
            s_date_unixtime = time.mktime(datetime.strptime(item['s_date'], "%Y-%m-%d").timetuple())
            f_date_unixtime = (datetime.fromtimestamp(
                time.mktime(datetime.strptime(item['f_date'], "%Y-%m-%d").timetuple())) + timedelta(
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
                self.add_relevant_posts(
                    res_id=item['id'],
                    item_id=post['node']['id'],
                    url=f"https://www.instagram.com/p/{post['node']['shortcode']}/",
                    text=text,
                    likes=post['node']['edge_media_preview_like']['count'],
                    comment=post['node']['edge_media_to_comment']['count'],
                    date=datetime.utcfromtimestamp(post['node']['taken_at_timestamp'])
                    .strftime('%Y-%m-%d'),
                )
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

    def __repr__(self):
        return str(self.resource_list)
