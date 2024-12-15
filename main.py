from lib import logger, db, sqlconnection

from bluesky import bluesky_author, bluesky_posts
from twit import twit_post


def main():
    logger.debug("Starting")

    # call blue sky
    author = bluesky_author()
    feed = bluesky_posts(author)

    logger.debug("Bluesky Done")

    # the feed is newest to oldest, but we need oldest to newest to maintain threads
    feed.reverse()

    for post in feed:
        db.execute('SELECT EXISTS(SELECT 1 FROM ids WHERE blskyid = ?)', (post['post']['cid'],))
        exists = db.fetchone()[0]
        if exists:
            logger.debug("Post already exists")
            continue

        text = post['post']['record']['text']
        # check for a link logic for links
        if 'embed' in post['post']['record'] and post['post']['record']['embed']['$type'] == "app.bsky.embed.external" \
                and 'uri' in post['post']['record']['embed']['external']['uri']:
            logger.debug("Link found - Embeded")
            link = post['post']['record']['embed']['external']['uri']
        elif 'facets' in post['post']['record'] and 'features' in post['post']['record']['facets'] \
                and 'uri' in post['post']['record']['facets']['features']:
            logger.debug("Link found - Faceted")
            link = post['post']['record']['facets']['features']['uri']
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
            resp = twit_post(text, result[0])
        else:
            logger.debug('No Reply')
            resp = twit_post(text)

        logger.debug("Posted tweet " + str(resp['id'] + " " + str(resp['text'])[:20]))

        db.execute('INSERT INTO ids (blskyid, twitid) VALUES (?, ?)', (post['post']['cid'], resp['id']))
        sqlconnection.commit()

        if link is not None:
            logger.debug("Link Posting")
            resp = twit_post(link, resp['id'])
            logger.debug("Link Posted")

        logger.debug("Done")


if __name__ == "__main__":
    main()
