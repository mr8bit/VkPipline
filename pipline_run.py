from sklearn.pipeline import FeatureUnion, Pipeline
from pipline import GetAllTextPostsFromGroupPipline, ClearTextPipline, TokenNormalizationPipline
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import gensim
from gensim.models import CoherenceModel


clearing = Pipeline([
    ('vk_group_post', GetAllTextPostsFromGroupPipline(max_repeat_count=0)),
    ('clear_text', ClearTextPipline()),
    ('normalization', TokenNormalizationPipline()),
    ('vectorazing', CountVectorizer(max_features=10000))
])

full_pipeline = FeatureUnion(transformer_list=[
    ('clearing', clearing),
])

full_pipeline_m = Pipeline(steps=[('full_pipeline', full_pipeline), ])

tf = full_pipeline_m.fit_transform("https://vk.com/maiuniversity")


print(tf)