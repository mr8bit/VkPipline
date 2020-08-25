from .autoaression import AutoaggressionAnalysis

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


class AutoreggressionPipeline(TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        for user in X:
            for id in user.keys():
                for group in user[id]:
                    for post in group:
                        print(post)
        return self
