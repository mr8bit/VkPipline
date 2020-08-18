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
        if isinstance(X, list):
            cleaned_post = []
            for group in X:
                resp = self.vk.wall.get(owner_id=group * -1, offset=0, count=1)  # получаем общее количетво постов
                repeat_offset = int(math.ceil(resp['count'] / 100))
                offset = 0
                post_group = []
                for post_100 in range(repeat_offset):  # проходимся по 100 все посты группы
                    time.sleep(0.5)
                    resp = self.vk.wall.get(owner_id=group * -1, offset=offset, count=100)
                    for post in resp['items']:
                        text = post['text']
                        try:
                            text += post['copy_history'][0]['text']  # Если у репоста был текст
                        except:
                            pass
                        if len(text)>5:
                            post_group.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
                cleaned_post.append({group: post_group})
            return cleaned_post

        if isinstance(X, str):
            cleaned_post = []
            screen_name = X.split('/')[-1]
            resp = self.vk.utils.resolveScreenName(screen_name=screen_name)
            if resp['type'] == 'group':
                owner_id = resp['object_id']
                resp = self.vk.wall.get(owner_id=owner_id * -1, offset=0, count=1)
                repeat_offset = int(math.ceil(resp['count'] / 100))
                offset = 0
                for post_100 in range(repeat_offset):
                    time.sleep(0.5)
                    resp = self.vk.wall.get(owner_id=owner_id * -1, offset=offset, count=100)
                    for post in resp['items']:
                        text = post['text']
                        try:
                            text += post['copy_history'][0]['text']
                        except:
                            pass
                        if len(text)>5:
                            cleaned_post.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
                return [{owner_id:cleaned_post}]


class GetAllTextPostsFromUserPipeline(TransformerMixin):
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
        if isinstance(X, list):
            cleaned_post = []
            for user in X:
                resp = self.vk.wall.get(owner_id=user, offset=0, count=1)  # получаем общее количетво постов
                repeat_offset = int(math.ceil(resp['count'] / 100))
                offset = 0
                post_group = []
                for post_100 in range(repeat_offset):  # проходимся по 100 все посты группы
                    time.sleep(0.5)
                    resp = self.vk.wall.get(owner_id=user, offset=offset, count=100)
                    for post in resp['items']:
                        text = post['text']
                        try:
                            text += post['copy_history'][0]['text']  # Если у репоста был текст
                        except:
                            pass
                        if len(text)>5:
                            post_group.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
                cleaned_post.append({user: post_group})
            return cleaned_post

        if isinstance(X, str):
            cleaned_post = []
            screen_name = X.split('/')[-1]
            resp = self.vk.utils.resolveScreenName(screen_name=screen_name)
            if resp['type'] == 'user':
                owner_id = resp['object_id']
                resp = self.vk.wall.get(owner_id=owner_id, offset=0, count=1)
                repeat_offset = int(math.ceil(resp['count'] / 100))
                offset = 0
                print(resp)
                for post_100 in range(repeat_offset):
                    time.sleep(0.5)
                    resp = self.vk.wall.get(owner_id=owner_id, offset=offset, count=100)
                    for post in resp['items']:
                        text = post['text']
                        try:
                            text += post['copy_history'][0]['text']
                        except:
                            pass
                        if len(text)>5:
                            cleaned_post.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
                return [{owner_id: cleaned_post}]
