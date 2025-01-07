import os

from lib import logger, db, sqlconnection

from bluesky import bluesky_author, bluesky_posts
from twit import twit_post, twitUi_open, twitUi_login, twitUi_post, twitUi_close


def main():
    logger.debug("Starting")

    # call blue sky
    author = bluesky_author()
    feed = bluesky_posts(author)

    logger.debug("Bluesky Done")

    # the feed is newest to oldest, but we need oldest to newest to maintain threads
    feed.reverse()
    # TEMP CUT FOR DEBUG
    # feed = feed[-3:]

    # for preventing getting rate limited on an existing account, gets the 10 most recent
    feed = feed[-10:]

    if os.environ['TWITTER_HANDLE']:
        # open browser and page
        logger.debug("Twitter UI is being used")
        twitter, browser, p = twitUi_open()
        loggedIn = False
    else:
        logger.debug("Twitter API is being used")

    for post in feed:
        db.execute('SELECT EXISTS(SELECT 1 FROM ids WHERE blskyid = ?)', (post['post']['cid'],))
        exists = db.fetchone()[0]
        if exists:
            logger.debug("Post already exists")
            continue

        text = post['post']['record']['text']
        # check for a link logic for links
        if 'embed' in post['post']['record'] and post['post']['record']['embed']['$type'] == "app.bsky.embed.external" \
                and 'uri' in post['post']['record']['embed']['external']:
            logger.debug("Link found - Embeded")
            link = post['post']['record']['embed']['external']['uri']
        elif 'facets' in post['post']['record'] and 'features' in post['post']['record']['facets'][0] \
                and 'uri' in post['post']['record']['facets'][0]['features'][0]:
            logger.debug("Link found - Faceted")
            link = post['post']['record']['facets'][0]['features'][0]['uri']
        else:
            logger.debug("No Link")
            link = None

        if len(text) > 280:
            logger.debug("Text too long:" + str(len(text)))
            text = text[:277] + "..."

        # see if it has a reply to a tweet
        if 'reply' in post:
            logger.debug("Reply")
            reply = post['reply']
            if reply['root']['author']['did'] != author or reply['parent']['author']['did'] != author:
                logger.debug("Not reply to post from Author")
                continue

            db.execute('SELECT twitid FROM ids WHERE blskyid = ?', (reply['parent']['cid'],))
            result = db.fetchone()

            if os.environ['TWITTER_HANDLE']:
                if not loggedIn:
                    twitUi_login(twitter)
                    loggedIn = True
                resp = twitUi_post(twitter, text, result[0])
            else:
                resp = twit_post(text, result[0])
        else:
            logger.debug('No Reply')
            if os.environ['TWITTER_HANDLE']:
                if not loggedIn:
                    twitUi_login(twitter)
                    loggedIn = True
                resp = twitUi_post(twitter, text)
            else:
                resp = twit_post(text)

        if os.environ['TWITTER_HANDLE']:
            logger.debug("Posted tweet " + str(resp) + " " + str(text)[:20])
        else:
            logger.debug("Posted tweet " + str(resp['id'] + " " + str(resp['text'])[:20]))
            resp = resp['id']

        db.execute('INSERT INTO ids (blskyid, twitid) VALUES (?, ?)', (post['post']['cid'], resp))
        sqlconnection.commit()

        if link is not None:
            logger.info("Link posting is presently disabled")
            # logger.debug("Link Posting")
            # if os.environ['TWITTER_HANDLE']:
            #     if not loggedIn:
            #         twitUi_login(twitter)
            #         loggedIn = True
            #     resp = twitUi_post(twitter, link, resp)
            # else:
            #     resp = twit_post(link, resp)
            # logger.debug("Link Posted")

        logger.debug("Done")

    if os.environ['TWITTER_HANDLE']:
        twitUi_close(browser, p)
    logger.debug("Finished and exiting\n\n")
    print("Finished and exiting")


if __name__ == "__main__":
    main()
