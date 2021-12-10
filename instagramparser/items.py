# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    username = scrapy.Field()
    relationship = scrapy.Field()
    is_private = scrapy.Field()
    photo = scrapy.Field()

    """ Followers """
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()
    follower_full_name = scrapy.Field()
    followers_data = scrapy.Field()

    """ Following """
    following_id = scrapy.Field()
    following_name = scrapy.Field()
    following_full_name = scrapy.Field()
    following_data = scrapy.Field()
