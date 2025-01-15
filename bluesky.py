import os, requests
from dotenv import load_dotenv

from lib import logger, close


def bluesky_author():
    load_dotenv()

    url = os.getenv("BLUESKY_URL")
    author = os.getenv("BLUESKY_AUTHOR")

    query = {
        'actor': author
    }

    try:
        resp = requests.get(url+'/xrpc/app.bsky.actor.getProfile', params=query)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}\nURL: {resp.url}\nStatus Code: {resp.status_code}\nResponse: {resp.text}")
        close(True)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}\nURL: {url+'/xrpc/app.bsky.actor.getProfile'}")
        close(True)
    else:
        return resp.json()['did']


def bluesky_posts(did):
    load_dotenv()

    url = os.getenv("BLUESKY_URL")

    query = {
        'actor': did,
        'filter': 'posts_and_author_threads'
    }

    try:
        resp = requests.get(url+'/xrpc/app.bsky.feed.getAuthorFeed', params=query)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}\nURL: {resp.url}\nStatus Code: {resp.status_code}\nResponse: {resp.text}")
        close(True)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}\nURL: {url+'/xrpc/app.bsky.feed.getAuthorFeed'}")
        close(True)
    else:
        return resp.json()['feed']