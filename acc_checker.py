from typing import Union

import requests
from bs4 import BeautifulSoup
import json
# import instaloader
# from db import DataBase
# from db_info import DB_TEMP_local
import requests.auth

# L = instaloader.Instaloader()
# USER = 'nadir_bombardir2'
# PASSWORD = 'endermen_kriper'
# # Optionally, login or load session
# L.login(USER, PASSWORD)        # (login)
# L.interactive_login(USER)      # (ask password on terminal)
# L.load_session_from_file(USER)
#
# comm = L.download_comments
# print(comm)


class InstParser:
    # def __init__(self):
    #     self.db = DataBase()
    #     self.db.DB_INFO = DB_TEMP_local

    def select_items(self):
        query = """SELECT * FROM resource_social LIMIT 1"""
        answer = self.db.query_get(query)

        return answer

    def update_user(self, data, res_id):
        query = f"""UPDATE resource_social SET resource_name=%s, screen_name=%s, image_profile=%s, members=%s, follows=%s, info_check = 1 WHERE id = {res_id}"""

        self.db.query_send(query, data)

    def get_json(self, resourse_url, resource_id):
        session_id = "56577518341%3ALF2s08C6EtLiQQ%3A20%3AAYdbQtEtQRIdPBx3_L_R64fpFFPJWKfYzrQk-xU8Lw"
        cookies = {'sessionid': session_id}
        c = 0

        # headers_ = {'user-agent': 'Instagram 219.0.0.12.117 Android'}
        headers_ = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 123.1.0.26.115 (iPhone11,8; iOS 13_3; en_US; en-US; scale=2.00     ; 828x1792; 190542906)'}
        proxies = {
            'https': 'http://indy361890:Xitv6136rN@185.156.178.105:20418'
        }
        #proxies = {
        #    "https": f"socks5://94.247.130.58:5555",
        #    "http": f"socks5://94.247.130.58:5555",
        #}

        html = requests.get(resourse_url, cookies=cookies, proxies=proxies, headers=headers_)
        print(html.text)

        # if user['message'] == 'checkpoint_required':
        #     print('BAN')
        # else:
        #     print('NORM')

    def main(self):
        # all_items = self.select_items()
        # for one_item in all_items:
        #     resource_url = one_item.get('link')
        #     resource_id = one_item.get('id')
        #     print(f"Scraping: {resource_url}")
        # self.get_json('https://www.instagram.com/kaztwitter/', 1)
        # self.get_json('https://i.instagram.com/api/v1/media/2861756652335304276/info/', 1)
        # self.get_json('https://i.instagram.com/api/v1/media/2866012130697177550/info/', 1)
        # self.get_json('https://www.instagram.com/p/Ci5HXBhgM-v/?__a=1&__d=dis', 1)
        # self.get_json('https://i.instagram.com/api/v1/users/?__id=310108057', 1)
        # self.get_json('https://www.instagram.com/nuragaidar_usa_brands/', 1)
        # self.get_json('https://codeofaninja.com/tools/find-instagram-id-answer.php?instagram_username={kaztwitter}', 1)
        # self.get_json('https://www.instagram.com/graphql/query/?query_id=17888483320059182&id=10149343297&first=50', 1)1949894869
        # self.get_json('https://www.instagram.com/graphql/query/?query_id=17852405266163336&id=CfbjUk-IN6f&first=500}', 1)17841453659583106
        # self.get_json('https://www.instagram.com/graphql/query/?query_id=17888483320059182&variables=%7B%22id%22%3A%2210149343297%22%2C%22first%22%3A50%7D', 1)
        # self.get_json('https://www.instagram.com/graphql/query/?query_id=17888483320059182&id=7093881806&first=1', 1)
        # self.get_json('https://i.instagram.com/api/v1/tags/logged_out_web_info/?tag_name=аәк', 1)
        # self.get_json('https://i.instagram.com/api/v1/tags/web_info/?tag_name=айтуарқошмамбетов', 1)
        # self.get_json('https://i.instagram.com/api/v1/users/619682345/info/', 1)
        # self.get_json('https://www.instagram.com/explore/locations/216416212/alma-ata-almaty-kazakhstan/', 1)
        self.get_json('https://i.instagram.com/api/v1/users/web_profile_info/?username=police__astana', 7036810623)
        # self.get_json("https://www.instagram.com/graphql/query/?query_id=17841400841714852&id=310108057", 1)


# SELECT * FROM `resource_social` WHERE id in (520354589,520079831,519888055,519094971,517186701,514116359,512678085,505779661,498167283,496940279,495130097,478691949,469252107,459927457,450424363,431164771,415900447,414248163,413875588,383681675,383489918,354740934,342560900,341876001,320872803,316619505,315950105,312569052,286142149,276886358,275977433,261149634,261145464,253184816,253184765,236429519,234809948,232253012,222580792,220982845,219702642,217015504,209753902,209445527,209130331,207322352,200554401,199741973,199741971,196521137,196169270,195526086,194922714,194264320,192312923,191761832,188247775,183254892,183254668,182898734,182711413,182705540,182672617,182665279,171776210,167152131,164144095,152356722,146779334,146776238,140754447,135992912,135539227,133017734,130592892,130101616,126162090,122995858,119809648,116411960,114131757,112527167,108616224,108507393,107083968,105885707,104030660,102596298,91592808,90119543,89930360,89500842,89500834,89444880,82751746,81605100,75366022,73406387,72826010,69095281,66352038,65133938,64719385,64050759,63940448,63929105,59415388,55003640,52716227,49074259,48436546,48361023,47450662,46155059,44857500,41559764,34964600,34221205,31002114,28030828,26775723,26752027,26066490,24428516,19436997,9271447,6553666,4849502,1566121,1301760,1258906,1172598,728255,702611,504379,456929,450237,447309,251308,248550,247880,246429,245486,244427,244069,137726,133956,133831,131105,130874,130042,129418,127487,124216,116821,94635,93623,93504,92823,91129,80727,80320,15578,2912,2510,2503) ORDER BY id DESC
if __name__ == '__main__':
    parser = InstParser()
    for _ in range(5):
        parser.main()
