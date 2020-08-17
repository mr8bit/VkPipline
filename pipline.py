from sklearn.base import BaseEstimator, TransformerMixin
import os
import time
import vk_api
import re
import pymorphy2
from stop_words import get_stop_words
import numpy as np

stop_words = get_stop_words('ru')


class GetAllTextPostsFromGroupPipeline(TransformerMixin):
    """
        Получаем все посты с гурппы ВК
        max_repeat_count - количество внутренних итераций
    """

    def __init__(self, max_repeat_count):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        cleaned_post = []
        screen_name = X.split('/')[-1]
        resp = self.vk.utils.resolveScreenName(screen_name=screen_name)
        if resp['type'] == 'group':
            owner_id = resp['object_id']
            resp = self.vk.wall.get(owner_id=owner_id * -1, offset=0, count=1)
            if resp['count'] > 100:
                repeat_post = int(resp['count'] / 100)
                if repeat_post > 0 and repeat_post < 1:
                    repeat_post = 0
                offset = 0
                for post_100 in range(repeat_post):
                    time.sleep(0.5)
                    resp = self.vk.wall.get(owner_id=owner_id * -1, offset=offset, count=100)
                    for post in resp['items']:
                        text = post['text']
                        try:
                            text += post['copy_history'][0]['text']
                        except:
                            pass
                        cleaned_post.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
        return cleaned_post


class GetAllTextAndPhotosFromGroupListPipeline(TransformerMixin):
    """
        Получаем все посты с списка гурпп ВК
        max_repeat_count - количество внутренних итераций
    """

    def __init__(self, max_repeat_count, *featurizers):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count
        self.featurizers = featurizers

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, list):
            cleaned_post = []
            for owner_id in X:
                resp = self.vk.wall.get(owner_id=owner_id * -1, offset=0, count=1)
                if resp['count'] > 100:
                    repeat_post = int(resp['count'] / 100)
                    if repeat_post > 0 and repeat_post < 1:
                        repeat_post = 0
                    offset = 0
                    for post_100 in range(repeat_post):
                        time.sleep(0.5)
                        resp = self.vk.wall.get(owner_id=owner_id * -1, offset=offset, count=100)
                        for post in resp['items']:
                            text = post['text']
                            try:
                                text += post['copy_history'][0]['text']
                            except:
                                pass
                            cleaned_post.append(text)
                        offset += 100
                        if post_100 == self.max_repeat_count:
                            break
            return cleaned_post
        else:
            return self


class ClearTextPipeline(TransformerMixin):
    def __init__(self, *featurizers):
        self.featurizers = featurizers

    @staticmethod
    def mister_clean(text):
        text = re.sub(r"http\S+", "", text)
        text = text.lower()
        text = re.sub("([\(\[]).*?([\)\]])", "", text)
        text = text.split('\n')
        data = [re.sub('\S*@\S*\s?', '', sent) for sent in text]

        # Remove new line characters
        data = [re.sub('\s+', ' ', sent) for sent in data]

        # Remove distracting single quotes
        text = [re.sub("\'", "", sent) for sent in data]
        text = ' '.join(text)
        text = re.sub("[^0-9a-zA-Zа-яА-Я ]", "", text)
        return text

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self.mister_clean(sentence) for sentence in X]


class TokenNormalizationPipeline(TransformerMixin):
    def __init__(self, *featurizers):
        self.morph = pymorphy2.MorphAnalyzer()
        self.featurizers = featurizers

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        clear = []
        for x in X:
            normolize_sentence = [self.morph.parse(word)[0].normal_form for word in x.split(' ')]
            text = [w for w in normolize_sentence if not w in stop_words and len(w) > 5]
            clear.append(' '.join(text))
        return clear


class GetWallPhotosPipeline(TransformerMixin):
    def __init__(self, max_repeat_count, sizes=['m', 'o', 'p', 'q', 'r', 's', 'w', 'x', 'y', 'z']):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count
        self.selected_size = sizes

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        screen_name = X.split('/')[-1]
        res = self.vk.utils.resolveScreenName(screen_name=screen_name)
        user_id = res['object_id']
        user_type = res['type']

        if user_type == 'group':
            user_id *= -1

        result = []
        response = self.vk.photos.get(owner_id=user_id, album_id="wall", count=1)
        if response['count'] > 100:
            repeat_offset = int(response['count'] / 100)
            if 0 < repeat_offset < 1:
                repeat_offset = 0
            offset = 0
            for i in range(repeat_offset):
                response = self.vk.photos.get(owner_id=user_id, album_id="wall", count=100, offset=offset)
                offset += 100
                print(response['items'])
                for item in response['items']:
                    image = []
                    for size in item['sizes']:
                        if size['type'] in self.selected_size:
                            image.append(['url'])
                    result.append({
                        "date": item['date'],
                        "image": image
                    })
        else:
            response = self.vk.photos.get(owner_id=user_id, album_id="wall", count=100)
            for item in response['items']:
                image = []
                for size in item['sizes']:
                    if size['type'] in self.selected_size:
                        image.append(size['url'])
                result.append({
                    "date": item['date'],
                    "image": image
                })
        return result


class GetUserGroupsPipeline(TransformerMixin):
    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        result = []
        if isinstance(X, list):
            for user_id in X:
                response = self.vk.groups.get(owner_id=user_id, extended=0, count=1000)
                result.append({user_id: response['items']})

        return result


class  GetUserSubscriptionPipeline(TransformerMixin):
    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        result = []
        if isinstance(X, list):
            for user_id in X:
                response = self.vk.users.getSubscriptions(user_id=user_id, extended=0, count=1000)
                result.append({user_id: response['items']})
        else:
            print(X)
            try:
                if len(X.split('/')):
                    print(X)
                    screen_name = X.split('/')[-1]
                    res = self.vk.utils.resolveScreenName(screen_name=screen_name)
                    user_id = res['object_id']
                    print(user_id)
                    response = self.vk.users.getSubscriptions(user_id=user_id, extended=0, count=200)
                    print(response)
                    result.append({user_id: response['items']})

            except Exception as e:
                print(e)

        return result


class GetUserFriendPipeline(TransformerMixin):
    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        result = []
        if isinstance(X, list):
            for user_id in X:
                response = self.vk.friends.get(user_id=user_id, extended=0, count=5000)
                result.append({user_id: response['items']})

        return result
