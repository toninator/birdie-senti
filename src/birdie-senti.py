#!/usr/bin/env python
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import auth_config
import json


def load_list(fname):
    with open(fname, "r") as f:
        lst = f.read().split()
    return lst


def count_senti(txt, lst):
    total = 0
    for x in txt.replace("#", "").split():
        if x in lst:
            total += 1
    return total


def compare_tags(tag, txt, good, bad, good_tags, bad_tags):
    if count_senti(txt, bad) == count_senti(txt, good):
        pass
    elif count_senti(txt, bad) > count_senti(txt, good):
        bad_tags[tag] += 1
    else:
        good_tags[tag] += 1

    b_tags = [key for key in bad_tags if bad_tags[key] == max(bad_tags.values())]
    g_tags = [key for key in good_tags if good_tags[key] == max(good_tags.values())]

    positive = "Most Positive: %s (%d)" % (g_tags, max(good_tags.values()))
    negative = "Most Negative: %s (%d)" % (b_tags, max(bad_tags.values()))
    print positive + ' ' + negative


class MyListener(StreamListener):
    """Custom StreamListener for streaming data."""

    def on_data(self, data):
        try:
            # print data
            payload = json.loads(data)
            txt = payload['text']
            # print txt  # debug field

            if "#Xbox".lower() in txt.lower() \
                    and ("#Playstation".lower() not in txt.lower() or "#Switch".lower() not in txt.lower()):
                compare_tags("#Xbox", txt, good, bad, good_tags, bad_tags)

            if "#Playstation".lower() in txt.lower() \
                    and ("#Xbox".lower() not in txt.lower() or "#Switch".lower() not in txt.lower()):
                compare_tags("#Playstation", txt, good, bad, good_tags, bad_tags)

            if "#Switch".lower() in txt.lower() \
                    and ("#Xbox".lower() not in txt.lower() or "#Playstation".lower() not in txt.lower()):
                compare_tags("#Switch", txt, good, bad, good_tags, bad_tags)

            # print [key for key in bad_tags if bad_tags[key] == max(bad_tags.values()) and max(bad_tags.values()) != 0]
            # print bad_tags.values()

        except BaseException as e:
            print("Error on_data: %s" % str(e))
            time.sleep(5)
        return True

    def on_error(self, status):
        print(status)
        return True


if __name__ == '__main__':

    # Using keys from auth_config.py to authenticate with Twitter API
    auth = OAuthHandler(auth_config.consumer_key, auth_config.consumer_secret)
    auth.set_access_token(auth_config.access_token, auth_config.access_secret)
    api = tweepy.API(auth)

    try:
        bad = load_list('../data/negative-words.txt')
        good = load_list('../data/positive-words.txt')
    except Exception as e:
        print e

    bad_tags = dict()
    bad_tags['#Xbox'] = 0
    bad_tags['#Playstation'] = 0
    bad_tags['#Switch'] = 0

    good_tags = dict()
    good_tags['#Xbox'] = 0
    good_tags['#Playstation'] = 0
    good_tags['#Switch'] = 0

    twitter_stream = Stream(auth, MyListener())
    twitter_stream.filter(track=['#Xbox', '#Playstation', '#Switch'])

