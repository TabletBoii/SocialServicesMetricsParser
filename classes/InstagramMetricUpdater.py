import time
import urllib
from datetime import datetime, timedelta

import requests
import urllib3
import pytz
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from utilities import serialize_result_to_list, serialize_response_to_json
from models.models import Resources, Posts, PostMetrics


class InstagramMetricUpdater:
    def __init__(self, header: dict, cookie: dict, db_session: Session, proxy: dict):
        self.headers = header
        self.cookie = cookie
        self.session = db_session
        self.proxy = proxy

    def update_resources_dates(self, res_id: int) -> None:
        self.session.execute(
            update(Resources)
            .where(Resources.id == res_id)
            .values(met_finish_date=datetime.now(tz=pytz.timezone('Asia/Almaty')))
        )

    def get_resources_up_to_date(self) -> list[tuple]:
        now = datetime.now(tz=pytz.timezone('Asia/Almaty'))
        hour_ago = now - timedelta(hours=1)
        resource_list = self.session.execute(
            select(Resources.id, Resources.date)
            .filter(Resources.met_finish_date < hour_ago, Resources.type == 4)
        ).all()
        resource_list_ids = [resource[0] for resource in resource_list]
        return resource_list_ids

    def update_post_metrics(self, item: dict) -> None:
        profile_cursor = ''
        while True:
            resource_posts: dict = serialize_response_to_json(
                f'https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B"id":{self.profile_id}, "first": "50", "after": "{profile_cursor}"%7D',
                self.cookie,
                self.headers,
                self.proxy)
            # If data keyword error then account was banned
            number_of_posts_per_cursor = resource_posts['data']['user']['edge_owner_to_timeline_media']['count']
            current_posts_list_statement = self.session.execute(
                select(Posts.item_id)
            ).all()
            current_posts_list = [current_post[0] for current_post in current_posts_list_statement]

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
                if post['node']['id'] in current_posts_list:
                    continue
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
                    date=datetime.utcfromtimestamp(post['node']['taken_at_timestamp']).strftime(
                        '%Y-%m-%d'),
                    s_date=datetime.now(),
                    attachments='',
                    sentiment=0
                )
                post_metrics_object = PostMetrics(
                    type=4,
                    res_id=item['id'],
                    url=f"https://www.instagram.com/p/{post['node']['shortcode']}/",
                    item_id=post['node']['id'],
                    date=datetime.utcfromtimestamp(post['node']['taken_at_timestamp']).strftime(
                        '%Y-%m-%d'),
                    s_date=datetime.now(),
                    likes=post['node']['edge_media_preview_like']['count'],
                    comments=post['node']['edge_media_to_comment']['count'],
                    reposts=0,
                )
                # TODO: get rid of adding metrics for one post several times a day
                self.add_post(post_object, post_metrics_object)
                self.session.execute(
                    update(Resources)
                    .where(Resources.id == item['id'])
                    .values(met_finish_date=datetime.now(tz=pytz.timezone('Asia/Almaty')))
                )
                print(f"Post {post['node']['id']} added. Likes [{post['node']['edge_media_preview_like']['count']}]"
                      f". Comments [{post['node']['edge_media_to_comment']['count']}]")
            if number_of_posts_per_cursor >= 50:
                profile_cursor = resource_posts['data']['user']['edge_owner_to_timeline_media']['page_info'][
                    'end_cursor']
                continue
            break

    def run(self):
        resource_id_list = self.get_resources_up_to_date()
        if len(resource_id_list)==0:
            print("No resources to update")
            return
        # for resource_id in resource_id_list:
        #     try:
        #         self.parse_profile_posts(post)
        #     except TypeError as te:
        #         print(te)

        # self.update_resource_met_date(resource_set)
