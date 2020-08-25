from nltk import tokenize
import re
import nltk
import pyphen
import numpy as np
import pymorphy2

morph = pymorphy2.MorphAnalyzer()


class AutoaggressionAnalysis():
    """
        Построено на базе статьи
        ДИАГНОСТИРОВАНИЕ СКЛОННОСТИ АВТОРА ПИСЬМЕННОГО ТЕКСТА К АУТОАГРЕССИВНОМУ ПОВЕДЕНИЮ
        За авторством О. В. Загоровская, Т. А. Литвинова, О. А. Литвинова, П. В. Середин, М. Е. Сердюк
        Журнал ВЕСТНИК ВГУ. СЕРИЯ: ЛИНГВИСТИКА И МЕЖКУЛЬТУРНАЯ КОММУНИКАЦИЯ. 2015
        https://cyberleninka.ru/article/n/diagnostirovanie-sklonnosti-avtora-pismennogo-teksta-k-autoagressivnomu-povedeniyu

        Example:
            txt = "В этом мае я утону в цветах"
            analysis = AutoaggressionAnalysis(text)

            analysis.spontaneous_aggression()
            analysis.depression()
            analysis.balance()
            analysis.emotional_lability()
    """

    def __init__(self, text):
        self.text = text
        self.words = self.get_words(text)
        self.sentences = self.get_sentences()
        self.number_words = len(self.words)  # Количество слов
        self.number_sentences = 1 if len(self.sentences) == 0 else len(self.sentences)  # Количество предложений
        # number_syllables - количство слогов
        # number_polysyllable_words - количество сложных слов
        self.number_syllables, self.number_polysyllable_words = self.get_number_syllables()
        self.average_length_sentence = self.number_words / self.number_sentences  # Средняя длина предложений (по количеству слов)
        self.average_word_in_sentence = self.get_average_word_in_sentence()  # Среднее количество слов в предложении
        self.ttr = self.get_token_type_ration()  # Индекс лексического разнообразия текста (TTR token type ration)
        # self.percentage_unions_in_text - Доля союзов в тексте
        # self.percentage_particles_in_text - Доля частиц в тексте
        # self.percentage_prepositions_in_text - Доля предлогов в тексте
        # self.ratio_of_logical_consistency - Коэффициент логической связанности
        self.percentage_unions_in_text, self.percentage_particles_in_text, self.percentage_prepositions_in_text, self.ratio_of_logical_consistency, self.number_personal_pronouns = self.get_percentage_of_part_of_speech_in_the_text()  # Доля прелогов (PREP) в тексте

    def spontaneous_aggression(self):
        """
            Баллы по шкале «Спонтанная агрессивность»
            Значение 0-20.

            Позволяет выявить и оценить психопатизацию интротенсивного типа.
            Высокие оценки свидетельствуют о повышенном уровне психопатизации, создающем предпосылки для
            импульсивного поведения.
        """
        return 22.996 + (0.169 * self.average_word_in_sentence) - (21.910 * self.ttr) - (
                39.948 * self.percentage_particles_in_text)

    def depression(self):
        """
            Баллы по школе «Депрессивность»
            Значение 0-20

            Дает возможность диагностировать признаки, характерные для психопатологического депрессивного синдрома.
            Высокие оценки по шкале соответствуют наличию этих признаков в эмоциональном состоянии, в поведении, в
            отношениях к себе и к социальной среде.

        """
        return 15.607 + (0.204 * self.average_word_in_sentence) - (17.548 * self.ttr)

    def balance(self):
        """
            Баллы по школе «Уравновешенность»
            Значение 0-20

            Отражает устойчивость к стрессу. Высокие оценки свидетельствуют о хорошей защищенности к воздействию
            стресс-факторов обычных жизненных ситуаций, базирующейся на уверенности в себе, оптимистичности
            и активности
        """
        return -14.740 + (22.367 * self.ttr) + (33.559 * self.percentage_prepositions_in_text) + (
                2.642 * self.number_personal_pronouns)

    def emotional_lability(self):
        """
            Баллы по школе «Эмоциональная лабильность»
            Значение 0-20

            Высокие оценки указывают на неустойчивость эмоционального состояния, проявляющуюся в частых колебаниях
            настроения, повышенной возбудимости, раздражительности, недостаточной саморегуляции.
            Низкие оценки могут характеризовать не только высокую стабильность эмоционального состояния как такового,
            но и хорошее умение владеть собой.
        """
        return 14.842 + (0.0928 * self.average_word_in_sentence) - (17.577 * self.ttr) + (
                23.873 * self.percentage_prepositions_in_text)

    def get_percentage_of_part_of_speech_in_the_text(self):
        # Доля прелогов различных частей речи в тексте и коэфициент логической связаности
        document = re.sub(r'[^\w]', ' ', self.text)
        tokens = nltk.word_tokenize(document)
        count_POS = {'NOUN': 0,
                     'ADJF': 0,
                     'ADJS': 0,
                     'COMP': 0,
                     'VERB': 0,
                     'INFN': 0,
                     'PRTF': 0,
                     'PRTS': 0,
                     'GRND': 0,
                     'NUMR': 0,
                     'ADVB': 0,
                     'NPRO': 0,
                     'PRED': 0,
                     'PREP': 0,
                     'CONJ': 0,
                     'PRCL': 0,
                     'INTJ': 0,
                     None: 0
                     }
        for word in tokens:
            p = morph.parse(word)[0]
            count_POS[p.tag.POS] += 1
        ratio_of_logical_consistency = (count_POS['CONJ'] + count_POS['PRCL'] + count_POS[
            'PREP']) * 3 * self.number_sentences
        CONJ = count_POS['CONJ'] / len(tokens)
        PRCL = count_POS['PRCL'] / len(tokens)
        PREP = count_POS['PREP'] / len(tokens)
        return CONJ, PRCL, PREP, ratio_of_logical_consistency, count_POS['NPRO']

    def get_token_type_ration(self):
        # Индекс лексического разнообразия текста (TTR token type ration)
        document = re.sub(r'[^\w]', ' ', self.text)
        document = document.lower()
        tokens = nltk.word_tokenize(document)
        types = nltk.Counter(tokens)
        return (len(types) / len(tokens))

    def get_average_word_in_sentence(self):
        length = [len(self.get_words(sentence)) for sentence in self.sentences]
        return np.average(length)

    @staticmethod
    def get_words(text):
        """
            Returns a list of all words found in the text.
        """
        word_tokenizer = tokenize.TreebankWordTokenizer()
        words = [w.strip().lower() for w in word_tokenizer.tokenize(text) if w.strip()]
        # Ex.:  <<This is the final.>>  becomes
        # ['<','<', 'This', 'is', 'the', 'final', '.', '>', '>'] -> ['This', 'is', 'the', 'final']
        words = [re.sub("\W", '', word) for word in words]
        words = [word for word in words if word]
        return words

    def get_sentences(self):
        """
             Returns a list of all sentences found in the text.
        """
        sentences = tokenize.sent_tokenize(self.text)
        sentences_only_chars = []
        # Remove sentences containing only punctuation:
        for sentence in sentences:
            if re.sub("\W", "", sentence):
                sentences_only_chars.append(sentence)
        return sentences_only_chars

    def get_number_syllables(self):
        dic = pyphen.Pyphen(lang='ru')

        syllables = 0
        words_3_syllables_more = 0

        for word in self.words:
            syl = len(dic.inserted(word).split("-"))
            syllables += syl
            if syl >= 3:
                words_3_syllables_more += 1
        return syllables, words_3_syllables_more

    def get_flesch_reading_ease(self):
        # http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
        """
            90.0 - 100.0 - слабо понимается средним 11-летним студентом
            60.0 - 70.0 - легко понимается студентами в возрасте от 13 до 15 лет
            0.00 - 30.0 - лучше всего понимают выпускники университетов
        """
        if self.number_sentences == 0:
            return 100.0
        return 206.835 - 1.3 * (self.number_words / self.number_sentences) - 60.1 * (
                self.number_syllables / self.number_words)

    def get_gunning_fog_index(self):
        # http://en.wikipedia.org/wiki/Gunning_fog_index
        """
            Индекс оценивает годы формального образования, необходимые для понимания текста в первом чтении
        """
        if self.number_sentences == 0:
            return 0.0
        return 0.4 * (0.78 * ((self.number_words / self.number_sentences)) + 100 * (
                self.number_polysyllable_words / self.number_words))
