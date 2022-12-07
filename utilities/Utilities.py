import json

import requests
from sqlalchemy.orm import Query


def serialize_result_to_list(statement: Query) -> list:
    converted_list: list = []
    for item in statement:
        converted_list.append({column: str(getattr(item, column)) for column in item.__table__.c.keys()})
    return converted_list


def serialize_response_to_json(url: str, cookies: dict, headers: str, proxies: str) -> dict:
    response: str = requests.get(
        url=url,
        cookies=cookies,
        headers=headers,
        proxies=proxies).text
    response_json: dict = json.loads(response)
    return response_json


