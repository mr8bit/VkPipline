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
import traceback
from vk_api.exceptions import ApiError

user_template = {
    "user_id": '',
    "content": {
        "wall": [],
        "photos": [],
        "friends": [],
        "groups": []
    }
}


class GetPostsFromGroupPipelineV2(TransformerMixin):
    def __init__(self, max_repeat_count, only_user_text):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count
        self.only_user_text = only_user_text

    def fit(self):
        return self

    def transform(self, X):
        if isinstance(X, list):
            for group in X:
                try:
                    print(int(group["group_id"]) * -1)
                    resp = self.vk.wall.get(owner_id=group["group_id"], offset=0, count=1)
                    repeat_offset = int(math.ceil(resp['count'] / 100))
                    offset = 0
                    group["content"]["wall"] = []
                    print("Group")
                    print(group)
                    for repeat in range(repeat_offset):
                        time.sleep(0.45)
                        resp = self.vk.wall.get(owner_id=group['group_id'], offset=offset, count=100)
                        for post in resp['items']:
                            print(post)
                            text = post['text']
                            if not self.only_user_text:
                                try:
                                    text += post['copy_history'][0]['text']
                                except Exception as e:
                                    print(e)
                                    print("Error")
                                    print(group)
                                    pass
                            group["content"]["wall"].append(text)
                        offset += 100
                        if repeat == self.max_repeat_count:
                            break
                except ApiError:
                    group["content"]["wall"] = []
                    continue
            return X

        else:
            return self


class GetPostsFromUserPipelineV2(TransformerMixin):
    def __init__(self, max_repeat_count, only_user_text):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count
        self.only_user_text = only_user_text

    def fit(self):
        return self

    def transform(self, X):
        if isinstance(X, list):
            for user in X:
                try:
                    resp = self.vk.wall.get(owner_id=user['user_id'], offset=0, count=1)
                    repeat_offset = int(math.ceil(resp['count'] / 100))
                    offset = 0
                    user["content"]["wall"] = []
                    for repeat in range(repeat_offset):
                        time.sleep(0.45)
                        resp = self.vk.wall.get(owner_id=user['user_id'], offset=offset, count=100)
                        for post in resp['items']:
                            text = post['text']
                            if not self.only_user_text:
                                try:
                                    text += post['copy_history'][0]['text']
                                except:
                                    pass
                            user["content"]["wall"].append(text)
                        offset += 100
                        if repeat == self.max_repeat_count:
                            break
                except ApiError:
                    user["content"]["wall"] = []
                    traceback.print_exc()
                    continue
            return X

        else:
            return self


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

    def get_post_from_group(self, repeat_offset, groupid):
        offset = 0
        post_group = []
        for repeater in range(repeat_offset):  # проходимся по 100 все посты группы
            time.sleep(0.5)  # Что бы не блокировали ждем пол секунды
            resp = self.vk.wall.get(owner_id=groupid, offset=offset, count=100)
            for post in resp['items']:
                text = post['text']
                try:
                    text += post['copy_history'][0]['text']  # Если у репоста был текст
                except Exception as e:
                    pass
                if len(text) > 5:
                    post_group.append(text)
            offset += 100
            if repeater == self.max_repeat_count:  # останавливаем цикл
                break
        return post_group

    def transform(self, X):
        if isinstance(X, list):
            user_group_post = []
            for user in X:
                for id in user.keys():
                    cleaned_post = []
                    for group in tqdm(user[id]):
                        try:
                            resp = self.vk.wall.get(owner_id=group * -1, offset=0,
                                                    count=1)  # получаем общее количетво постов
                        except ApiError:  # Если группа закрытая
                            traceback.print_exc()
                            cleaned_post.append({group: False})
                            continue
                        repeat_offset = int(math.ceil(resp['count'] / 100))  # считаем сколько раз надо пройтись
                        post_group = self.get_post_from_group(repeat_offset, group * -1)  # получаем посты с группы
                        cleaned_post.append({group: post_group})
                    user_group_post.append({id: cleaned_post})
            return user_group_post

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
                        if len(text) > 5:
                            cleaned_post.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
                return [{owner_id: cleaned_post}]


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

    def get_post_from_group(self, repeat_offset, groupid):
        offset = 0
        post_group = []
        for repeater in range(repeat_offset):  # проходимся по 100 все посты группы
            time.sleep(0.5)  # Что бы не блокировали ждем пол секунды
            resp = self.vk.wall.get(owner_id=groupid, offset=offset, count=100)
            for post in resp['items']:
                text = post['text']
                if len(text) > 5:
                    post_group.append(text)
            offset += 100
            if repeater == self.max_repeat_count:  # останавливаем цикл
                break
        return post_group

    def transform(self, X):
        if isinstance(X, list):
            user_group_post = []
            for user in X:
                for id in user.keys():
                    cleaned_post = []
                    for group in tqdm(user[id]):
                        try:
                            resp = self.vk.wall.get(owner_id=group, offset=0,
                                                    count=1)  # получаем общее количетво постов
                        except ApiError:  # Если группа закрытая
                            traceback.print_exc()
                            cleaned_post.append({group: False})
                            continue
                        repeat_offset = int(math.ceil(resp['count'] / 100))  # считаем сколько раз надо пройтись
                        post_group = self.get_post_from_group(repeat_offset, group)  # получаем посты с группы
                        cleaned_post.append({group: post_group})
                    user_group_post.append({id: cleaned_post})
            return user_group_post

        if isinstance(X, str):
            cleaned_post = []
            screen_name = X.split('/')[-1]
            resp = self.vk.utils.resolveScreenName(screen_name=screen_name)
            if resp['type'] == 'group':
                owner_id = resp['object_id']
                resp = self.vk.wall.get(owner_id=owner_id, offset=0, count=1)
                repeat_offset = int(math.ceil(resp['count'] / 100))
                offset = 0
                for post_100 in range(repeat_offset):
                    time.sleep(0.5)
                    resp = self.vk.wall.get(owner_id=owner_id, offset=offset, count=100)
                    for post in resp['items']:
                        text = post['text']
                        try:
                            text += post['copy_history'][0]['text']
                        except:
                            pass
                        if len(text) > 5:
                            cleaned_post.append(text)
                    offset += 100
                    if post_100 == self.max_repeat_count:
                        break
                return [{owner_id: cleaned_post}]
