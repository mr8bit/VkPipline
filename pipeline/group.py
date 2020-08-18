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


class GetUsersFromGroupPipeline(TransformerMixin):
    """
        Пользователи из группы
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
        if isinstance(X, str):
            cleaned_post = []
            screen_name = X.split('/')[-1]
            resp = self.vk.utils.resolveScreenName(screen_name=screen_name)
            owner_id = resp['object_id']
            resp = self.vk.groups.getMembers(group_id=owner_id, offset=0, count=1)
            repeat_offset = int(math.ceil(resp['count'] / 1000))
            offset = 0
            for post_100 in range(repeat_offset):
                time.sleep(0.5)
                resp = self.vk.groups.getMembers(group_id=owner_id, offset=offset, count=1000)
                cleaned_post.extend(resp['items'])
                offset += 1000
                if post_100 == self.max_repeat_count:
                    break
            return [{owner_id:cleaned_post}]

        if isinstance(X, list):
            group_list_members = []
            for group in X:
                group_members = []
                resp = self.vk.groups.getMembers(group_id=group, offset=0, count=1)
                repeat_offset = int(math.ceil(resp['count'] / 1000))
                offset = 0
                for post_100 in range(repeat_offset):
                    time.sleep(0.45)
                    resp = self.vk.groups.getMembers(group_id=group, offset=offset, count=1000)
                    group_members.extend(resp['items'])
                    offset += 1000
                    if post_100 == self.max_repeat_count:
                        break
                group_list_members.append({group: group_members})
            return group_list_members
        else:
            return self
