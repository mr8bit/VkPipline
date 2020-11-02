from sklearn.base import TransformerMixin
import os
import vk_api
import math
import time
import traceback
from vk_api.exceptions import ApiError
from tqdm import tqdm

class GetUserIdPipelineV2(TransformerMixin):
    """
        Получаем id пользователей
    """

    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        if isinstance(X, list):
            result = []
            for user_link in tqdm(X):
                screen_name = user_link.split('/')[
                    -1]  # получаем коротное имя пользователя (вроде как работает и с форматом id321321)
                res = self.vk.utils.resolveScreenName(screen_name=screen_name)
                if res:
                    user_id = res['object_id']
                    result.append({"user_id": user_id, 'content': {} })
            return result
        else:
            return self


class GetUserSubscriptionPipelineV2(TransformerMixin):
    """
        Получить подписки пользователя страницы пабликов
    """

    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        result = []
        if isinstance(X, list):
            for user in tqdm(X):
                user_id = user["user_id"]
                time.sleep(0.4)
                try:
                    response = self.vk.users.getSubscriptions(user_id=user_id, extended=0, count=200)
                    user["content"]["subscriptions"] = response['groups']['items']
                except ApiError:
                    user["content"]["subscriptions"] = []
                    traceback.print_exc()
                    continue
            return X

        if isinstance(X, str):
            screen_name = X.split('/')[-1]
            res = self.vk.utils.resolveScreenName(screen_name=screen_name)
            user_id = res['object_id']
            response = self.vk.users.getSubscriptions(user_id=user_id, extended=0, count=200)
            result.append({user_id: response['groups']['items']})

        return result


class GetUserFriendPipelineV2(TransformerMixin):
    """
        Получить список друзей пользователя
    """

    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        result = []
        if isinstance(X, list):
            for user in X:
                user_id = user["user_id"]
                time.sleep(0.4)
                try:
                    response = self.vk.friends.get(user_id=user_id, extended=0, count=5000)
                    user["content"]["friends"] = response['items']
                except ApiError:
                    user["content"]["friends"] = []
                    traceback.print_exc()
                    continue
            return X

        elif isinstance(X, str):
            screen_name = X.split('/')[-1]
            res = self.vk.utils.resolveScreenName(screen_name=screen_name)
            user_id = res['object_id']
            response = self.vk.friends.get(user_id=user_id, extended=0, count=5000)
            result.append({user_id: response['items']})
            return result
        else:
            return self


class GetUserGroupsPipelineV2(TransformerMixin):
    """
        Получить список групп пользователя
    """

    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        if isinstance(X, list):
            result = []
            for user in tqdm(X):
                user_id = user["user_id"]
                time.sleep(0.4)
                try:
                    response = self.vk.groups.get(user_id=user_id, extended=0, count=1000)
                    user["content"]["groups"] = response['items']
                except ApiError:
                    traceback.print_exc()
                    user["content"]["groups"] = []
                    continue
            return X
        else:
            return self


class GetUserMentionsPipeline(TransformerMixin):
    """
        Получить список упоминаний пользователя
    """

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
                try:
                    response = self.vk.newsfeed.getMentions(user_id=user_id, count=1)
                except ApiError:
                    traceback.print_exc()
                    result.append({user_id: False})
                    continue
                repeat_offset = int(math.ceil(response['count'] / 50))
                offset = 0
                for _ in range(repeat_offset):
                    try:
                        time.sleep(0.4)
                        response = self.vk.newsfeed.getMentions(user_id=user_id, offset=offset, count=50)
                        for mention in response['items']:
                            result.append({user_id: mention})
                    except ApiError:
                        traceback.print_exc()
                        result.append({user_id: False})

                    offset += 50
            return result

        elif isinstance(X, str):
            screen_name = X.split('/')[-1]
            res = self.vk.utils.resolveScreenName(screen_name=screen_name)
            user_id = res['object_id']
            response = self.vk.newsfeed.getMentions(owner_id=user_id, count=1)
            repeat_offset = int(math.ceil(response['count'] / 50))
            offset = 0
            mentions_user = []
            for _ in range(repeat_offset):
                time.sleep(0.4)
                response = self.vk.newsfeed.getMentions(owner_id=user_id, offset=offset, count=50)
                print(response)
                for mention in response['items']:
                    mentions_user.append(mention)
                offset += 50

            result.append({user_id: mentions_user})
            return result
        else:
            return self


class GetUserGroupsPipeline(TransformerMixin):
    """
        Получить список групп пользователя
    """

    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

    def fit(self):
        return self

    def transform(self, X):
        if isinstance(X, list):
            result = []
            for user_id in X:
                time.sleep(0.4)
                try:
                    response = self.vk.groups.get(user_id=user_id, extended=0, count=1000)
                    result.append({user_id: response['items']})
                except ApiError:
                    traceback.print_exc()
                    return [{user_id: False}]
            return result
        else:
            screen_name = X.split('/')[-1]
            res = self.vk.utils.resolveScreenName(screen_name=screen_name)
            user_id = res['object_id']
            try:
                response = self.vk.groups.get(user_id=user_id, extended=0, count=1000)
                return [{user_id: response['items']}]
            except ApiError:
                traceback.print_exc()
                return [{user_id: False}]


class GetUserSubscriptionPipeline(TransformerMixin):
    """
        Получить подписки пользователя страницы пабликов
    """

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
                time.sleep(0.4)
                response = self.vk.users.getSubscriptions(user_id=user_id, extended=0, count=1000)
                result.append({user_id: response['groups']['items']})
        if isinstance(X, str):
            screen_name = X.split('/')[-1]
            res = self.vk.utils.resolveScreenName(screen_name=screen_name)
            user_id = res['object_id']
            response = self.vk.users.getSubscriptions(user_id=user_id, extended=0, count=200)
            result.append({user_id: response['groups']['items']})

        return result


class GetUserFriendPipeline(TransformerMixin):
    """
        Получить список друзей пользователя
    """

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
                time.sleep(0.4)
                response = self.vk.friends.get(user_id=user_id, extended=0, count=5000)
                result.append({user_id: response['items']})
            return result
        elif isinstance(X, str):
            screen_name = X.split('/')[-1]
            res = self.vk.utils.resolveScreenName(screen_name=screen_name)
            user_id = res['object_id']
            response = self.vk.friends.get(user_id=user_id, extended=0, count=5000)
            result.append({user_id: response['items']})
            return result
        else:
            return self
