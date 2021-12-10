import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from instagramparser.items import InstagramparserItem
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'alenchik_belova'
    inst_pwd = '*******'
    users = ['nadia75bel', 'tomulia1']
    friendships_link = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_pwd},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables_followers = {'count': 12, 'search_surface': 'follow_list_page'}
        url_followers = f'{self.friendships_link}{user_id}/followers/?{urlencode(variables_followers)}'

        yield response.follow(
            url_followers,
            callback=self.user_followers_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables_followers': deepcopy(variables_followers)},
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}
        )

        variables_following = {'count': 12}
        url_following = f'{self.friendships_link}{user_id}/following/?{urlencode(variables_following)}'

        yield response.follow(
            url_following,
            callback=self.user_following_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables_following': deepcopy(variables_following)},
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}
        )

    def user_followers_parse(self, response: HtmlResponse, username, user_id, variables_followers):
        j_data = response.json()
        if 'next_max_id' in j_data:
            variables_followers['max_id'] = j_data['next_max_id']
            url_followers = f'{self.friendships_link}{user_id}/followers/?{urlencode(variables_followers)}'

            yield response.follow(
                url_followers,
                callback=self.user_followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_followers': deepcopy(variables_followers)},
                headers={'User-Agent': 'Instagram 155.0.0.37.107'}
            )

        followers = j_data['users']
        for follower in followers:
            item = InstagramparserItem(
                user_id=user_id,
                username=username,
                relationship='follower',
                follower_id=follower['pk'],
                follower_name=follower['username'],
                follower_full_name=follower['full_name'],
                is_private=follower['is_private'],
                photo=followers['profile_pic_url'],
                followers_data=follower
            )

            yield item

    def user_following_parse(self, response: HtmlResponse, username, user_id, variables_following):
        j_data = response.json()
        if 'next_max_id' in j_data:
            variables_following['max_id'] = j_data['next_max_id']
            url_following = f'{self.friendships_link}{user_id}/following/?{urlencode(variables_following)}'

            yield response.follow(
                url_following,
                callback=self.user_following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables_following': deepcopy(variables_following)},
                headers={'User-Agent': 'Instagram 155.0.0.37.107'}
            )

        followings = j_data['users']
        for following in followings:
            item = InstagramparserItem(
                user_id=user_id,
                username=username,
                relationship='following',
                followinf_id=following['pk'],
                following_name=following['username'],
                following_full_name=following['full_name'],
                is_private=following['is_private'],
                photo=followings['profile_pic_url'],
                following_data=following
            )

            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
