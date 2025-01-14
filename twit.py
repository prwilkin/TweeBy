import tweepy, os, time, random
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from lib import logger, twit, close


def twit_post(text: str, twitRepId=None):
    try:
        # if os.environ['TWITTER_API_VERSION']:
            # version 2
            resp = twit.apiV2.create_tweet(text=text, in_reply_to_tweet_id=twitRepId)
            resp = resp.data
        # else:
        #     # version 1
        #     resp = twit.apiV1.update_status(text, in_reply_to_tweet_id=twitRepId)
    except tweepy.errors.TweepyException as e:
        logger.error(
            f"Tweepy Exception: {e}\n"
            f"Request Payload: {{'text': {text}, 'in_reply_to_tweet_id': {twitRepId}}}\n"
            f"API Endpoint: apiV2.create_tweet"
        )
        close(e)
    except Exception as e:
        logger.error(
            f"Unexpected Error: {e}\n"
            f"Request Payload: {{'text': {text}, 'in_reply_to_tweet_id': {twitRepId}}}\n"
            f"API Endpoint: apiV2.create_tweet"
        )
        close(e)
    else:
        return resp


def twitUi_open():
    logger.debug("Opening Playwright")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    # browser = p.chromium.launch(headless=False)   # for debugging
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
        time.sleep(random.uniform(3, 6))
        page.get_by_test_id("loginButton").click()
        time.sleep(random.uniform(2, 3))
        page.get_by_label("Phone, email, or username").fill(os.environ['TWITTER_HANDLE'])
        time.sleep(random.uniform(1, 2))
        page.get_by_role("button", name="Next").click()
        time.sleep(random.uniform(3, 6))
        page.get_by_label("Password", exact=True).fill(os.environ['TWITTER_PASSWORD'])
        time.sleep(random.uniform(1, 2))
        page.get_by_test_id("LoginForm_Login_Button").click()

    except PlaywrightError as e:
        logger.error(e)
        logger.error('Url: ' + page.url)
        close(e)

    except PlaywrightTimeoutError:
        logger.error('Timeout on login')
        close('Error')

    else:
        logger.debug('Logged in OK')


def checkLoggedIn(page, link):
    x = 0
    try:
        while (page.get_by_label("Phone, email, or username").is_visible() or page.get_by_test_id("login").is_visible()) and x < 10:
            logger.debug('Needs to login')
            page.goto("https://x.com/login", timeout=10000)
            time.sleep(random.uniform(3, 6))
            page.get_by_label("Phone, email, or username").fill(os.environ['TWITTER_HANDLE'])
            time.sleep(random.uniform(1, 2))
            page.get_by_role("button", name="Next").click()
            time.sleep(random.uniform(3, 6))
            page.get_by_label("Password", exact=True).fill(os.environ['TWITTER_PASSWORD'])
            time.sleep(random.uniform(1, 2))
            page.get_by_test_id("LoginForm_Login_Button").click()
            time.sleep(random.uniform(3, 5))
            page.goto(link, timeout=10000)
            time.sleep(random.uniform(4, 8))
            x += 1
        if x == 10:
            raise Exception('Re-login failed when trying to tweet')

    except Exception as e:
        logger.error(e)

    except PlaywrightError as e:
        logger.error(e)
        logger.error('Url: ' + page.url)
        close(e)

    except PlaywrightTimeoutError:
        logger.error('Timeout on login')
        close('Error')
    else:
        logger.debug("Re-logged in")


def twitUi_post(page, text: str, twitRepId=None):
    try:
        if twitRepId is None:
            logger.debug('Tweeting')
            # no reply
            # note this link does not matter, we just need to trigger the view tweet window
            # this is a nod to the tweet that inspire the project
            page.goto("https://x.com/SCOTUSblog/status/1866852700433813805", timeout=10000)

            time.sleep(random.uniform(4, 8))
            # page.get_by_test_id("SideNav_NewTweet_Button").click()
            # page.get_by_test_id("tweetTextarea_0").fill(text)

            page.goto("https://x.com/compose/post", timeout=10000)
            time.sleep(random.uniform(6, 8))

            checkLoggedIn(page, "https://x.com/compose/post")

            page.get_by_role("textbox", name="Post text").fill(text)

            time.sleep(random.uniform(4, 10))

            # getting stuck on odd popups sometimes
            # if page.locator("#layers > div:nth-child(2) > div > div > div").is_visible():
            #     page.locator("#layers > div:nth-child(2) > div > div > div").first.click()
            #     logger.debug('Clicked background')
            # if not page.get_by_test_id("tweetButton").is_visible():
            #     page.mouse.click(1, 1)
            #     logger.debug('Clicked at 1, 1 for pop up')
            page.mouse.click(1, 1)
            if page.get_by_test_id("confirmationSheetDialog").is_visible():
                page.mouse.click(1, 1)

            page.get_by_test_id("tweetButton").click(force=True, timeout=10000)
            # time.sleep(random.uniform(3, 6))
            logger.debug('Tweeted out')
        else:
            logger.debug(f'Replying to Tweet {twitRepId}')
            # reply to tweet
            page.goto(f'https://x.com/{os.environ['TWITTER_HANDLE']}/status/{twitRepId}', timeout=10000)  # 10-second timeout
            time.sleep(random.uniform(6, 8))

            checkLoggedIn(page, f'https://x.com/{os.environ['TWITTER_HANDLE']}/status/{twitRepId}')

            page.get_by_test_id("tweetTextarea_0").fill(text)
            time.sleep(random.uniform(4, 10))
            # if page.locator("#layers > div:nth-child(2) > div > div > div").is_visible():
            #     page.locator("#layers > div:nth-child(2) > div > div > div").first.click()
            #     logger.debug('Clicked background')
            # if not page.get_by_test_id("tweetButtonInline").is_visible():
            #     page.mouse.click(1, 1)
            #     logger.debug('Clicked at 1, 1 for pop up')
            page.mouse.click(1, 1)
            page.get_by_test_id("tweetButtonInline").click(force=True, timeout=10000)
            # time.sleep(random.uniform(5, 8))
            logger.debug('Tweeted out')

        page.get_by_test_id("toast").locator("a").click()
        tweetId = page.url.split("/")[-1]
        logger.debug(f'Tweet ID Found: {tweetId}')

    except PlaywrightError as e:
        logger.error(e)
        logger.error('Url: ' + page.url)
        close(e)

    except PlaywrightTimeoutError:
        logger.error('Timeout on Post')
        close('Error')

    else:
        return tweetId
