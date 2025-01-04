import tweepy, os, time, random
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from lib import logger, twit, close


def twit_post(text: str, twitRepId=None):
    try:
        resp = twit.create_tweet(text=text, in_reply_to_tweet_id=twitRepId)
    except tweepy.errors.TweepyException as e:
        logger.error(e)
        close(e)
    else:
        return resp.data


def twitUi_open():
    logger.debug("Opening Playwright")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    return page, browser, p


def twitUi_close(browser, p):
    logger.debug('Closing Playwright')
    browser.close()
    p.stop()


def twitUi_login(page):
    try:
        logger.debug('Logging in')
        page.goto("https://x.com/", timeout=10000)  # 10-second timeout

        # LOGIN
        page.get_by_test_id("loginButton").click()
        page.get_by_label("Phone, email, or username").fill(os.environ['TWITTER_HANDLE'])
        page.get_by_role("button", name="Next").click()
        time.sleep(random.uniform(3, 6))
        page.get_by_label("Password", exact=True).fill(os.environ['TWITTER_PASSWORD'])
        page.get_by_test_id("LoginForm_Login_Button").click()

    except PlaywrightError as e:
        logger.error(e)
        close(e)

    except PlaywrightTimeoutError:
        logger.error('Timeout on login')
        close('Error')

    else:
        logger.debug('Logged in OK')


def twitUi_post(page, text: str, twitRepId=None):
    try:
        if twitRepId is None:
            logger.debug('Tweeting')
            # no reply
            # note this link does not matter, we just need to trigger the view tweet window
            # this is a nod to the tweet that inspire the project
            page.goto("https://x.com/SCOTUSblog/status/1866852700433813805", timeout=10000)

            time.sleep(random.uniform(4, 8))
            page.get_by_test_id("SideNav_NewTweet_Button").click()
            page.get_by_test_id("tweetTextarea_0").fill(text)
            time.sleep(random.uniform(4, 10))
            page.get_by_test_id("tweetButton").click(timeout=10000)
            time.sleep(random.uniform(3, 6))
            logger.debug('Tweeted out')
        else:
            logger.debug('Replying to Tweet')
            # reply to tweet
            page.goto(f'https://x.com/{os.environ['TWITTER_HANDLE']}/status/{twitRepId}', timeout=10000)  # 10-second timeout

            time.sleep(random.uniform(4, 8))
            page.get_by_test_id("reply").click()
            page.get_by_role("textbox", name="Post text").fill(text)
            time.sleep(random.uniform(4, 10))
            page.get_by_test_id("tweetButton").click(timeout=10000)
            time.sleep(random.uniform(5, 8))
            logger.debug('Tweeted out')

        page.get_by_test_id("toast").locator("a").click()
        tweetId = page.url.split("/")[-1]
        logger.debug(f'Tweet ID Found: {tweetId}')

    except PlaywrightError as e:
        logger.error(e)
        close(e)

    except PlaywrightTimeoutError:
        logger.error('Timeout on login')
        close('Error')

    else:
        return tweetId
