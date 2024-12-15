import tweepy
from lib import logger, twit, close


def twit_post(text: str, twitRepId=None):
    try:
        resp = twit.create_tweet(text=text, in_reply_to_tweet_id=twitRepId)
    except tweepy.errors.TweepyException as e:
        logger.error(e)
        close(e)
    else:
        return resp.data


