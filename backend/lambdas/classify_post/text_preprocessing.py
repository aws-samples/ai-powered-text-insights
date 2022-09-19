import re

class TweetPreprocessor:

    @staticmethod
    def remove_links(tweet):
        """Takes a string and removes web links from it"""
        tweet = re.sub(r'http\S+', '', tweet)  # remove http links
        tweet = re.sub(r'bit.ly/\S+', '', tweet)  # remove bitly links
        tweet = re.sub(r'pic.twitter\S+', '', tweet)
        return tweet

    @staticmethod
    def remove_users(tweet):
        """Takes a string and removes retweet and @user information"""
        tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+):*', '', tweet)  # remove re-tweet
        tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+):*', '', tweet)  # remove tweeted at
        return tweet

    @staticmethod
    def remove_hashtags(tweet):
        """Takes a string and removes any hash tags"""
        tweet = re.sub('(#[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet)  # remove hash tags
        return tweet

    @staticmethod
    def remove_av(tweet):
        """Takes a string and removes AUDIO/VIDEO tags or labels"""
        tweet = re.sub('VIDEO:', '', tweet)  # remove 'VIDEO:' from start of tweet
        tweet = re.sub('AUDIO:', '', tweet)  # remove 'AUDIO:' from start of tweet
        return tweet

    @staticmethod
    def preprocess(tweet):
        #tweet = tweet.encode('latin1', 'ignore').decode('latin1')
        tweet = tweet.lower()
        #tweet = TweetPreprocessor.remove_users(tweet)
        tweet = TweetPreprocessor.remove_links(tweet)
        #tweet = TweetPreprocessor.remove_hashtags(tweet)
        tweet = TweetPreprocessor.remove_av(tweet)
        tweet = ' '.join(tweet.split())  # Remove extra spaces
        return tweet.strip()

    @staticmethod
    def get_hash_tags(tweet):
        return re.findall(r"#(\w+)", tweet)