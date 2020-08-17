import gensim.corpora as corpora

def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations





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


data_words = list(sent_to_words(tf))


data_lemmatized = data_words

id2word = corpora.Dictionary(data_lemmatized)
# Create Corpus
texts = data_lemmatized
# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]


lda_model = gensim.models.ldamodel.LdaModel(corpus=tf,
                                           num_topics=20,
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)

# Compute Perplexity
print('\nPerplexity: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.
# Compute Coherence Score
coherence_model_lda = CoherenceModel(model=lda_model, texts=tf, dictionary=id2word, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print('\nCoherence Score: ', coherence_lda)