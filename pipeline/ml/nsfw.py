from sklearn.base import BaseEstimator, TransformerMixin
import os
import time
import vk_api
from tqdm import tqdm
import math
from os.path import isfile, join, exists, isdir, abspath
import tensorflow as tf
import time
from .utils import get_image_from_url_and_convert_for_model, get_batches
from tqdm import tqdm


class ClassificationNSFWContentPipeline(TransformerMixin):
    """
        Получить список групп пользователя
    """

    def __init__(self, model_path, threshold_prediction=0.7):
        if model_path is None or not exists(model_path):
            raise ValueError("saved_model_path must be the valid directory of a saved model to load.")
        self.model = tf.keras.models.load_model(model_path)
        self.threshold_prediction = threshold_prediction

    def probs_set(self, model_prediction):
        categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']
        probs = []
        for i, single_preds in enumerate(model_prediction):
            single_probs = {}
            for j, pred in enumerate(single_preds):
                single_probs[categories[j]] = float(pred)
            probs.append(single_probs)
        return probs

    def fit(self):
        return self

    def transform(self, X):
        result = []
        if isinstance(X, list):
            photo_list = []
            for photo in X:
                for user in photo.keys():
                    for image in tqdm(photo[user]):
                        time.sleep(0.45)
                        img = get_image_from_url_and_convert_for_model(image['image'][0])
                        if img.shape == (299, 299, 3):
                            photo_list.append(img)
                    # Вот тут обрабатываем пользователя
                    nsfw_clas = {
                        'hentai': 0,
                        'drawings': 0,
                        'neutral': 0,
                        'porn': 0,
                        'sexy': 0
                    }
                    predict = self.model.predict([photo_list])
                    probs = self.probs_set(predict)
                    for prob in probs:
                        if prob['hentai'] > self.threshold_prediction:
                            nsfw_clas['hentai'] += 1
                        if prob['drawings'] > self.threshold_prediction:
                            nsfw_clas['drawings'] += 1
                        if prob['neutral'] > self.threshold_prediction:
                            nsfw_clas['neutral'] += 1
                        if prob['porn'] > self.threshold_prediction:
                            nsfw_clas['porn'] += 1
                        if prob['sexy'] > self.threshold_prediction:
                            nsfw_clas['sexy'] += 1
                    result.append({user: nsfw_clas})
            return result
        return result
