from sklearn.base import BaseEstimator, TransformerMixin
import os
import time
import vk_api
from tqdm import tqdm
import math


class GetUserPhotoPipeline(TransformerMixin):
    """
        Получить фотографии пользователя
    """

    def __init__(self, max_repeat_count, sizes=['m', 'o', 'p', 'q', 'r', 's', 'w', 'x', 'y', 'z'], photo_type='wall'):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.photo_type = photo_type

        if photo_type not in ['wall', 'profile', 'saved']:
            raise ValueError

        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count
        self.selected_size = sizes

    def get_wall_photos_group(self, user_id, repeat_offset):
        offset = 0
        group_photos = []
        for _ in range(repeat_offset):
            response = self.vk.photos.get(owner_id=user_id, album_id=self.photo_type, rev=1, count=100, offset=offset)
            offset += 100
            for item in response['items']:
                image = [
                    size['url']
                    for size in item['sizes']
                    if size['type'] in self.selected_size
                ]
                group_photos.append({
                    "date": item['date'],
                    "image": image
                })
            if _ == self.max_repeat_count:
                break
            time.sleep(0.4)
        return group_photos

    def get_wall_photo_on_group(self, X):
        result = []
        screen_name = X.split('/')[-1]
        res = self.vk.utils.resolveScreenName(screen_name=screen_name)
        group_id = res['object_id']
        try:
            response = self.vk.photos.get(owner_id=group_id, album_id=self.photo_type, count=1)
        except:
            return []
        time.sleep(0.3)
        repeat_offset = int(math.ceil(response['count'] / 100))
        photos_group = self.get_wall_photos_group(group_id, repeat_offset)
        result.append({group_id: photos_group})
        return result

    def get_wall_photo_on_list_group(self, X):
        """
            Получаем все фотки с стены если был передан массив с id пользоватлеями
        """
        result = []
        for group_id in tqdm(X):
            time.sleep(0.4)
            response = self.vk.photos.get(owner_id=group_id, album_id=self.photo_type, count=1)
            repeat_offset = int(math.ceil(response['count'] / 100))
            photos_group = self.get_wall_photos_group(group_id, repeat_offset)
            result.append({group_id: photos_group})
        return result

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if isinstance(X, list):
            return self.get_wall_photo_on_list_group(X)
        elif isinstance(X, str):
            return self.get_wall_photo_on_group(X)
        else:
            return self


class GetGroupPhotosPipeline(TransformerMixin):
    """
        Получаем список фотографий со стены группы
        О размерах изображений https://vk.com/dev/photo_sizes
        Самый популярный x рекомендую его
    """

    def __init__(self, max_repeat_count, sizes=['m', 'o', 'p', 'q', 'r', 's', 'w', 'x', 'y', 'z'], photo_type ='wall'):
        self.vk_session = vk_api.VkApi(os.getenv('LOGIN'), os.getenv('PASSWORD'))
        self.photo_type = photo_type

        if photo_type not in ['wall', 'profile']:
            raise ValueError

        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        self.max_repeat_count = max_repeat_count
        self.selected_size = sizes

    def fit(self, X, y=None):
        return self

    def get_wall_photos_group(self, user_id, repeat_offset):
        offset = 0
        group_photos = []
        for _ in range(repeat_offset):
            response = self.vk.photos.get(owner_id=user_id, album_id=self.photo_type, count=100, rev=1, offset=offset)
            offset += 100
            for item in response['items']:
                image = [
                    size['url']
                    for size in item['sizes']
                    if size['type'] in self.selected_size
                ]
                group_photos.append({
                    "date": item['date'],
                    "image": image
                })
            if _ == self.max_repeat_count:
                break
            time.sleep(0.4)
        return group_photos

    def get_wall_photo_on_list_group(self, X):
        """
            Получаем все фотки с стены если был передан массив с id групп
        """
        result = []
        for group_id in tqdm(X):
            time.sleep(0.4)
            response = self.vk.photos.get(owner_id=group_id * -1, album_id=self.photo_type, count=1)
            repeat_offset = int(math.ceil(response['count'] / 100))
            photos_group = self.get_wall_photos_group(group_id * -1, repeat_offset)
            result.append({group_id: photos_group})
        return result

    def get_wall_photo_on_group(self, X):
        result = []
        screen_name = X.split('/')[-1]
        res = self.vk.utils.resolveScreenName(screen_name=screen_name)
        group_id = res['object_id']
        response = self.vk.photos.get(owner_id=group_id * -1, album_id=self.photo_type, count=1)
        time.sleep(0.3)
        repeat_offset = int(math.ceil(response['count'] / 100))
        photos_group = self.get_wall_photos_group(group_id * -1, repeat_offset)
        result.append({group_id: photos_group})
        return result

    def transform(self, X):
        if isinstance(X, list):
            return self.get_wall_photo_on_list_group(X)
        elif isinstance(X, str):
            return self.get_wall_photo_on_group(X)
        else:
            return self
