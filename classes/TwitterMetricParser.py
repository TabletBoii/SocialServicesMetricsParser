from abc import ABC
from datetime import date
from sqlalchemy import select, update, desc
from abstarction import SocMetricParserAbstraction
from models.models import Tokens, Resources, ResourceMetrics
from utilities.Utilities import parse_username_from_url, serialize_response_to_json

class TwitterMetricParser(SocMetricParserAbstraction, ABC):
    def __init__(self, header: dict, db_session: dict, soc_type: int):
        super().__init__(header, db_session, soc_type)
        self.twitter_tokens: list[Tokens] = self.get_twitter_tokens()
    def get_twitter_tokens(self) -> list[tuple[Tokens]]:
        twitter_tokens = self.sessions["session_121"].execute(
            select(Tokens)
            .where(Tokens.requests < Tokens.requests_limit)
            .limit(1)
        ).all()
        return twitter_tokens

    def parse_profile_metrics(self) -> None:
        usernames: str = "usernames="
        for index, resource in enumerate(self.resource_list):
            if index == len(self.resource_list)-1:
                username = parse_username_from_url(resource['url'])
                usernames += username
                break
            username = parse_username_from_url(resource['url'])
            usernames += username + ","

        user_fields = "user.fields=public_metrics,url"
        url = f"https://api.twitter.com/2/users/by?{usernames}&{user_fields}"
        self.headers["Authorization"] = f"Bearer {self.twitter_tokens[0][0].bearer_token}"

        twitter_json_response = serialize_response_to_json(url, headers=self.headers)['data']
        db_twitter_zipped_list = list(zip(twitter_json_response, self.resource_list))
        self.resource_list = db_twitter_zipped_list
        for resource in db_twitter_zipped_list:
            print("Getting metrics of resource ", resource[1]['url'])
            profile_followers = resource[0]['public_metrics']['followers_count']
            profile_follow = resource[0]['public_metrics']['following_count']

            if resource[1]['owner_id'] == '':
                self.sessions["session_121"].execute(
                    update(Resources)
                    .where(Resources.url==resource[1]['url'])
                    .values(owner_id=resource[0]['id'])
                )
                self.sessions["session_121"].commit()
            last_date_updated = self.sessions["session_121"].execute(
                select(ResourceMetrics.date)
                .filter(ResourceMetrics.type == self.soc_type, ResourceMetrics.res_id == resource[1]['id'])
                .order_by(desc(ResourceMetrics.date))
                .limit(2)
            ).all()

            if len(last_date_updated) == 0 or last_date_updated[0][0] < date.today():
                insert_object = [
                    ResourceMetrics(
                        type=self.soc_type,
                        res_id=resource[1]['id'],
                        sf_type='members',
                        count=profile_followers,
                        date=date.today()
                    ),
                    ResourceMetrics(
                        type=self.soc_type,
                        res_id=resource[1]['id'],
                        sf_type='friends',
                        count=profile_follow,
                        date=date.today()
                    )
                ]
                print("Followers: ", profile_followers)
                print("Follows: ", profile_follow)
                self.sessions["session_121"].bulk_save_objects(insert_object)
                self.sessions["session_121"].commit()
            print(f"Resource {resource[1]['url']} is up-to-date")
            self.parsed_resources_counter += 1

    def parse_profile_posts(self) -> None:
        parsed_posts_buffered: list = []
        for resource in self.resource_list:
            profile_cursor = ''
            while True:
                tweet_fields = "tweet.fields=created_at,public_metrics"
                url = f"https://api.twitter.com/2/users/{resource[0]['id']}/tweets?" \
                      f"max_results=100&{tweet_fields}&" \
                      f"{profile_cursor}" \
                      f"end_time={resource[1]['f_date']}T00:00:00Z&" \
                      f"start_time={resource[1]['s_date']}T00:00:00Z"
                self.headers["Authorization"] = f"Bearer {self.twitter_tokens[0][0].bearer_token}"

                twitter_json_response = serialize_response_to_json(url, headers=self.headers)
                if twitter_json_response['meta']['result_count'] == 0:
                    print(f"Resource {resource[0]['id']} hasn't posts in period {resource[1]['s_date']} - {resource[1]['f_date']}")
                    break

                twitter_parsed_posts = twitter_json_response['data']
                for twitter_parsed_post in twitter_parsed_posts:
                    parsed_posts_buffered.append(twitter_parsed_post)
                if 'next_token' in twitter_json_response['meta']:
                    profile_cursor = f"pagination_token={twitter_json_response['meta']['next_token']}&"
                if twitter_parsed_posts[len(twitter_parsed_posts)-1]['created_at'][:10] > resource[1]['s_date']:
                    continue
                for parsed_post in parsed_posts_buffered:
                    self.add_relevant_posts(
                        res_id=int(resource[1]['id']),
                        item_id=parsed_post['id'],
                        url=f"https://twitter.com/9Dq4ItB4bWzJvxd/status/{parsed_post['id']}/",
                        text=parsed_post['text'],
                        likes=parsed_post['public_metrics']['like_count'],
                        comment=parsed_post['public_metrics']['reply_count'],
                        reposts=parsed_post['public_metrics']['retweet_count'],
                        date=parsed_post['created_at'][:10],
                    )
                break

    def set_proxy(self) -> None:
        pass
        

    def run(self) -> None:
        token = "5744501838:AAHyz308WweSvGV9bzt-d43-Ihke2KAKI9I"
        users = [-845330765]

        self.telegram_logger_init(token, users)
        self.parse_profile_metrics()
        self.parse_profile_posts()
        self.send_statistic_to_telegram()

