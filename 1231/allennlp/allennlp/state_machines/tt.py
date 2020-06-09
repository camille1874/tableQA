import gensim
import numpy as np
from gevent import monkey
from scipy.linalg import norm

# model = gensim.models.KeyedVectors.load_word2vec_format('./Tencent_AILab_ChineseEmbedding/Tencent_AILab_ChineseEmbedding.txt', binary=False)
model = gensim.models.KeyedVectors.load_word2vec_format('/home/xuzh/GoogleNews-vectors-negative300.bin', binary=True)


def get_sentence_sim(sen1, sen2):
    def sentence_vector(s):
            words = s.split()
            v = np.zeros(300)
            for word in words:
                if word in model:
                    v += model[word]
            v /= len(words)
            return v
    v1, v2 = sentence_vector(sen1), sentence_vector(sen2)
    return np.dot(v1, v2) / (norm(v1) * norm(v2))


a = get_sentence_sim("what is the only song on this soundtrack that is less than 3 minutes long ?", "smaller than")
b = get_sentence_sim("what is the only song on this soundtrack that is less than 3 minutes long ?", "larger than")
print(a)
print(b)
