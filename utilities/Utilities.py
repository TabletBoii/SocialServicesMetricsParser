import json
import re
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Query


def serialize_result_to_list(statement: Query) -> list:
    """
        convert database query result to python list

        :param statement: SQLAlchemy query
        :type statement: Query
    """
    converted_list: list = []
    for item in statement:
        converted_list.append({column: str(getattr(item, column)) for column in item.__table__.c.keys()})
    return converted_list


def serialize_response_to_json(url: str, headers=None, proxies=None, cookies=None) -> dict:
    """
        serialize requests response to json format

        :param url:
        :type url: str

        :param headers:
        :type headers: dict, optional
        :param proxies:
        :type proxies: dict, optional
        :param cookies:
        :type cookies: dict, optional

        TODO: add json handler
    """
    response: str = requests.get(
        url=url,
        cookies=cookies,
        headers=headers,
        proxies=proxies,
        timeout=10).text
    try:
        response_json: dict = json.loads(response)
        return response_json
    except Exception as error:
        print("Serializer fucked up\n", error)
        return response
    #if response_json['status_code'] != 200:
    #    raise Exception(f"Request returned an error: {response_json['status_code']} {response}")

def parse_username_from_url(url: str) -> str:
    """
        getting usernames from url
        :params url:
        :type url: str
    """
    parsed_username = urlparse(url)
    parsed_username = re.sub('/', '', str(parsed_username.path))
    return parsed_username
