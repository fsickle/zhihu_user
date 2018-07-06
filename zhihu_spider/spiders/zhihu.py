# -*- coding: utf-8 -*-
import json

from scrapy import Spider, Request

from zhihu_spider.items import UserItem


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?offset{offset}=&limit={limit}&include={include}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?offset{offset}=&limit={limit}&include={include}'
    followees_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
                        callback=self.parse_followers)
        yield Request(self.followees_url.format(user=self.start_user, include=self.followees_query, offset=0, limit=20),
                        callback=self.parse_followees)

    def parse_user(self, response):
        results = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in results.keys():
                item[field] = results.get(field)
        yield item

        yield Request(self.followers_url.format(user=results.get('url_token'), include=self.followers_query, offset=0, limit=20),
                        callback=self.parse_followers)
        yield Request(self.followees_url.format(user=results.get('url_token'), include=self.followees_query, offset=0, limit=20),
                      callback=self.parse_followees)

    def parse_followers(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
                yield Request(results.get('paging').get('next'), callback=self.parse_followers)




    def parse_followees(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            yield Request(results.get('paging').get('next'), callback=self.parse_followees)