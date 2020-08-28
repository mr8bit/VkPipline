from sklearn.base import BaseEstimator, TransformerMixin
import os
import time
import vk_api
import re
import pymorphy2
from stop_words import get_stop_words
import numpy as np
from tqdm import tqdm
import math
from demoji import replace as emoji_remove

stop_words = get_stop_words('ru')


class ClearTextPipeline(TransformerMixin):
    def __init__(self, *featurizers):
        self.featurizers = featurizers

    @staticmethod
    def deEmojify(text):
        regrex_pattern = re.compile("["
                                    u"\U0001F600-\U0001F64F"  # emoticons
                                    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                    u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                    u"\U0001F1F2-\U0001F1F4"  # Macau flag
                                    u"\U0001F1E6-\U0001F1FF"  # flags
                                    u"\U0001F600-\U0001F64F"
                                    u"\U00002702-\U000027B0"
                                    u"\U000024C2-\U0001F251"
                                    u"\U0001f926-\U0001f937"
                                    u"\U0001F1F2"
                                    u"\U0001F1F4"
                                    u"\U0001f964"
                                    u"\U0001F620"
                                    u"\u001f90d"
                                    u"\u200d"
                                    u"\u2640-\u2642"
                                    u"\U0001F90d"
                                    "]+", flags=re.UNICODE)

        return regrex_pattern.sub(r'', text)

    def mister_cleaner(self, text):
        text = emoji_remove(str(text))
        bad_chars = [';', ':', '!', "*", '^', '_', ']', '[', '(', ')']

        text = re.sub(r"http\S+", "", text)
        text = re.sub("#(\w+)", " ", text)
        text = re.sub("([\(\[]).*?([\)\]])", "", text)
        text = text.split('\n')
        data = [re.sub('\S*@\S*\s?', '', sent) for sent in text]

        # Remove new line characters
        data = [re.sub('\s+', ' ', sent) for sent in data]
        text = [re.sub("\'", "", sent) for sent in data]
        text = ' '.join(text)
        for i in bad_chars:
            text = text.replace(i, "")
        return text

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        for user in X:
            clear_user_wall = []
            for post in user['content']['wall']:
                cleaned_post = self.mister_cleaner(post)
                if len(cleaned_post)>1:
                    clear_user_wall.append(self.mister_cleaner(post))
            user['content']['wall'] = clear_user_wall
        return X
