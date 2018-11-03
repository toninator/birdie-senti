#!/usr/bin/env python
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import auth_config
import json
import sys


def load_list(fname):
    try:
        with open(fname, "r") as f:
            word_list = f.read().split()
            word_list = map(lambda x: unicode(x, "utf-8"), word_list)
        return word_list
    except Exception as e:
        print e
        sys.exit(-1)


def count_sentiment(tweet, word_list):
    total = 0
    for word in tweet.split():
        # check if words are in positive or negative lists, also check words in tags
        if word.replace("#", "") in word_list:
            total += 1
    return total


def emit_totals():
    # print running totals
    negative_tags = [key for key in negative_totals if negative_totals[key] == max(negative_totals.values())]
    positive_tags = [key for key in positive_totals if positive_totals[key] == max(positive_totals.values())]

    positive = "Most Positive: %s (%d)" % (positive_tags, max(positive_totals.values()))
    negative = "Most Negative: %s (%d)" % (negative_tags, max(negative_totals.values()))
    print positive + ' ' + negative


def eval_sentiment_count(platform_tag, tweet, positive_word_list, negative_word_list):
    # Compare if positive is great or negative is greater only if there's increment from previous state
    if count_sentiment(tweet, negative_word_list) == count_sentiment(tweet, positive_word_list):
        pass
    elif count_sentiment(tweet, negative_word_list) > count_sentiment(tweet, positive_word_list):
        negative_totals[platform_tag] += 1
        emit_totals()
    else:
        positive_totals[platform_tag] += 1
        emit_totals()


class MyListener(StreamListener):
    def on_data(self, data):
        try:
            payload = json.loads(data)
            tweet = payload['text']
            # print tweet # for debug

            # checks tweet if there's only 1 platform mentioned
            if xbox.lower() in tweet.lower() \
                    and (playstation.lower() not in tweet.lower() or switch.lower() not in tweet.lower()):
                eval_sentiment_count(xbox, tweet, positive_words, negative_words)
                return True

            if playstation.lower() in tweet.lower() \
                    and (xbox.lower() not in tweet.lower() or switch.lower() not in tweet.lower()):
                eval_sentiment_count(playstation, tweet, positive_words, negative_words)
                return True

            if switch.lower() in tweet.lower() \
                    and (xbox.lower() not in tweet.lower() or playstation.lower() not in tweet.lower()):
                eval_sentiment_count(switch, tweet, positive_words, negative_words)
                return True

        except BaseException as e:
            print("Error on_data: %s" % str(e))
            time.sleep(5)
        return True

    def on_error(self, status):
        print(status)
        return True


if __name__ == '__main__':
    # platform vars
    xbox = '#Xbox'
    playstation = '#Playstation'
    switch = '#Switch'

    # Using keys from auth_config.py to authenticate with Twitter API
    auth = OAuthHandler(auth_config.consumer_key, auth_config.consumer_secret)
    auth.set_access_token(auth_config.access_token, auth_config.access_secret)
    api = tweepy.API(auth)

    # read file for positive and negative lists
    negative_words = load_list('../data/negative-words.txt')
    positive_words = load_list('../data/positive-words.txt')

    # initialize running total dictionary
    negative_totals = dict()
    negative_totals[xbox] = 0
    negative_totals[playstation] = 0
    negative_totals[switch] = 0

    positive_totals = dict()
    positive_totals[xbox] = 0
    positive_totals[playstation] = 0
    positive_totals[switch] = 0

    # use tweepy.StreamListener
    twitter_stream = Stream(auth, MyListener())
    twitter_stream.filter(track=[xbox, playstation, switch])

