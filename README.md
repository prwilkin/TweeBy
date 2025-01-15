# x.twitter-bluesky-repost-bot
This is a bot that tweets posts and threads from an account on bluesky. This bot is for the use sharing information.
Media is not supported nor is retweet/quote tweeting.

# Feature Flags
To enable Feature Flags simple put 'True' at the feature, otherwise leave it blank.
### LINK_POSTING
This feature takes links and posts them in the reply to your tweet with the link. This is helpful in preserving the rate
limit. Since the limit is so low it can very easily be burned through by using this feature. Usage of this feature will
not disrupt a thread as the link reply is not stored or referenced

### UI_POSTING
This feature voids the api and uses playwright to post from the UI. Please see the section of this on the readme. 

# Bugs reporting & Feature requests
Please make a github issue for any bugs or feature requests. Please be as specific as possible in the issue you've 
encountered to help me replicate and understand the bug or feature. Vague issues will be closed.

# Contributing
Please feel free to reach out if you would like to help with features or bugs.

# usage
This can be used for noncommercial usage in accordance with Twitter/X policy.

# playwright
This project includes functionality to use playwright instead of the Twitter/X api. Usage of this feature may 
violate policy on Twitter/X. Authors of this project are not responsible for the outcome of such usage and do not 
encourage or endorse such usage. Please refer to Twitter/X for their policy guidelines on such automations.