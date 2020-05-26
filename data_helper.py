"""
dataset helper to preprocess csv format text dataset
"""
import pandas as pd
import numpy as np
import random
import re
from konlpy.tag import Okt
from collections import Counter
import gensim

tw = Okt()

def tokenizer(sentence):
    tokens = re.findall(r"[\w]+|[^\s\w]", sentence)
    return tokens

def pos_extractor(sentence):
    """
    extract Noun, Adjective, Verb only
    """
    tokens = []
    pos = tw.pos(sentence, norm=True, stem=True)
    for token, p in pos:
        if p == 'Noun' or p == 'Adjective' or p == 'Verb':
            tokens.append(token)
    return tokens


def morphs_extractor(sentence):
    """
    extract morphs
    """
    tokens = tw.morphs(sentence, norm=True, stem=True)
    return tokens


def morphs_process(lines):
    tokens = []
    for line in lines:
        token = morphs_extractor(line)
        tokens.append(token)
    return tokens


##################### use tokenizer #####################

def build_vocab(lines, max_vocab=None):
    word_counter = Counter()
    vocab = dict()
    reverse_vocab = dict()

    for line in lines:
        tokens = tokenizer(line)
        word_counter.update(tokens)

    vocab['<PAD>'] = 0
    vocab['<UNK>'] = 1
    vocab_idx = 2

    if max_vocab == None or max_vocab > len(word_counter):
        max_vocab = len(word_counter)

    for key, value in word_counter.most_common(max_vocab):
        vocab[key] = vocab_idx
        vocab_idx += 1

    for key, value in vocab.items():
        reverse_vocab[value] = key

    vocab_size = len(vocab.keys())

    return vocab, reverse_vocab, vocab_size


def sentence_to_onehot(lines, vocab):
    indexes = []
    vocab_size = len(vocab)

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    one_hots = []
    for line in lines:
        tokens = tokenizer(line)
        tokens = set(tokens)
        one_hot = np.zeros(vocab_size, dtype=int)
        for token in tokens:
            if token in vocab.keys():
                one_hot[vocab[token]] = 1
        one_hots.append(one_hot)
    one_hots = np.asarray(one_hots)

    return one_hots


def cal_idf(lines, vocab):
    vocab_size = len(vocab)
    doc_size = len(lines)
    DF = np.zeros(vocab_size)
    for line in lines:
        tokens = tokenizer(line)
        tokens = set(tokens)
        for token in tokens:
            if token in vocab.keys():
                DF[vocab[token]] += 1
    IDF = np.log(doc_size / (1 + DF))

    return IDF


def sentence_to_tfidf(lines, vocab, IDF):
    vocab_size = len(vocab)
    doc_size = len(lines)

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    tf_idfs = []
    for line in lines:
        tokens = tokenizer(line)
        freq = dict()
        TF = np.zeros(vocab_size, dtype=float)
        for token in tokens:
            if token in vocab.keys():
                if token in freq.keys():
                    freq[token] += 1
                else:
                    freq[token] = 1
        if len(freq) == 0:
            max_tf = 0
        else:
            max_tf = max(freq.values())
        tokens = set(tokens)
        for token in tokens:
            if token in vocab.keys():
                TF[vocab[token]] = 0.5 + 0.5 * freq[token] / max_tf
        tf_idf = np.multiply(TF, IDF)
        tf_idfs.append(tf_idf)
    tf_idfs = np.asarray(tf_idfs)

    return tf_idfs


def sentence_to_index(lines, vocab, max_length=0):
    tokens = []
    indexes = []
    max_len = max_length

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    if max_len == 0:
        for line in lines:
            token = tokenizer(line)
            tokens.append(token)
            length = len(token)
            if max_len < length:
                max_len = length
    else:
        for line in lines:
            token = tokenizer(line)
            tokens.append(token)

    for token in tokens:
        if len(token) < max_len:
            temp = token
            for _ in range(len(temp), max_len):
                temp.append('<PAD>')
        else:
            temp = token[:max_len]
        index = []
        for char in temp:
            if char in vocab.keys():
                index.append(vocab[char])
            else:
                index.append(vocab['<UNK>'])
        indexes.append(index)

    return indexes


##################### use tokenizer #####################


################### use pos_extractor ###################

def build_vocab_pos(lines, max_vocab=None):
    word_counter = Counter()
    vocab = dict()
    reverse_vocab = dict()

    for line in lines:
        tokens = pos_extractor(line)
        word_counter.update(tokens)

    vocab['<PAD>'] = 0
    vocab['<UNK>'] = 1
    vocab_idx = 2

    if max_vocab == None or max_vocab > len(word_counter):
        max_vocab = len(word_counter)

    for key, value in word_counter.most_common(max_vocab):
        vocab[key] = vocab_idx
        vocab_idx += 1

    for key, value in vocab.items():
        reverse_vocab[value] = key

    vocab_size = len(vocab.keys())

    return vocab, reverse_vocab, vocab_size


def sentence_to_onehot_pos(lines, vocab):
    indexes = []
    vocab_size = len(vocab)

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    one_hots = []
    for line in lines:
        tokens = pos_extractor(line)
        tokens = set(tokens)
        one_hot = np.zeros(vocab_size, dtype=int)
        for token in tokens:
            if token in vocab.keys():
                one_hot[vocab[token]] = 1
        one_hots.append(one_hot)
    one_hots = np.asarray(one_hots)

    return one_hots


def cal_idf_pos(lines, vocab):
    vocab_size = len(vocab)
    doc_size = len(lines)
    DF = np.zeros(vocab_size)
    for line in lines:
        tokens = pos_extractor(line)
        tokens = set(tokens)
        for token in tokens:
            if token in vocab.keys():
                DF[vocab[token]] += 1
    IDF = np.log(doc_size / (1 + DF))

    return IDF


def sentence_to_tfidf_pos(lines, vocab, IDF):
    vocab_size = len(vocab)
    doc_size = len(lines)

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    tf_idfs = []
    for line in lines:
        tokens = pos_extractor(line)
        freq = dict()
        TF = np.zeros(vocab_size, dtype=float)
        for token in tokens:
            if token in vocab.keys():
                if token in freq.keys():
                    freq[token] += 1
                else:
                    freq[token] = 1
        if len(freq) == 0:
            max_tf = 0
        else:
            max_tf = max(freq.values())
        tokens = set(tokens)
        for token in tokens:
            if token in vocab.keys():
                TF[vocab[token]] = 0.5 + 0.5 * freq[token] / max_tf
        tf_idf = np.multiply(TF, IDF)
        tf_idfs.append(tf_idf)
    tf_idfs = np.asarray(tf_idfs)

    return tf_idfs


def sentence_to_index_pos(lines, vocab, max_length=0):
    tokens = []
    indexes = []
    max_len = max_length

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    if max_len == 0:
        for line in lines:
            token = pos_extractor(line)
            tokens.append(token)
            length = len(token)
            if max_len < length:
                max_len = length
    else:
        for line in lines:
            token = pos_extractor(line)
            tokens.append(token)

    for token in tokens:
        if len(token) < max_len:
            temp = token
            for _ in range(len(temp), max_len):
                temp.append('<PAD>')
        else:
            temp = token[:max_len]
        index = []
        for char in temp:
            if char in vocab.keys():
                index.append(vocab[char])
            else:
                index.append(vocab['<UNK>'])
        indexes.append(index)

    return indexes


################### use pos_extractor ###################


################## use morphs_extractor ##################

def build_vocab_morphs(lines, max_vocab=None):
    word_counter = Counter()
    vocab = dict()
    reverse_vocab = dict()

    for line in lines:
        tokens = morphs_extractor(line)
        word_counter.update(tokens)

    vocab['<PAD>'] = 0
    vocab['<UNK>'] = 1
    vocab_idx = 2

    if max_vocab == None or max_vocab > len(word_counter):
        max_vocab = len(word_counter)

    for key, value in word_counter.most_common(max_vocab):
        vocab[key] = vocab_idx
        vocab_idx += 1

    for key, value in vocab.items():
        reverse_vocab[value] = key

    vocab_size = len(vocab.keys())

    return vocab, reverse_vocab, vocab_size


def sentence_to_onehot_morphs(lines, vocab):
    indexes = []
    vocab_size = len(vocab)

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    one_hots = []
    for line in lines:
        tokens = morphs_extractor(line)
        tokens = set(tokens)
        one_hot = np.zeros(vocab_size, dtype=int)
        for token in tokens:
            if token in vocab.keys():
                one_hot[vocab[token]] = 1
        one_hots.append(one_hot)
    one_hots = np.asarray(one_hots)

    return one_hots


def cal_idf_morphs(lines, vocab):
    vocab_size = len(vocab)
    doc_size = len(lines)
    DF = np.zeros(vocab_size)
    for line in lines:
        tokens = morphs_extractor(line)
        tokens = set(tokens)
        for token in tokens:
            if token in vocab.keys():
                DF[vocab[token]] += 1
    IDF = np.log(doc_size / (1 + DF))

    return IDF


def sentence_to_tfidf_morphs(lines, vocab, IDF):
    vocab_size = len(vocab)
    doc_size = len(lines)

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    tf_idfs = []
    for line in lines:
        tokens = morphs_extractor(line)
        freq = dict()
        TF = np.zeros(vocab_size, dtype=float)
        for token in tokens:
            if token in vocab.keys():
                if token in freq.keys():
                    freq[token] += 1
                else:
                    freq[token] = 1
        if len(freq) == 0:
            max_tf = 0
        else:
            max_tf = max(freq.values())
        tokens = set(tokens)
        for token in tokens:
            if token in vocab.keys():
                TF[vocab[token]] = 0.5 + 0.5 * freq[token] / max_tf
        tf_idf = np.multiply(TF, IDF)
        tf_idfs.append(tf_idf)
    tf_idfs = np.asarray(tf_idfs)

    return tf_idfs


def sentence_to_index_morphs(lines, vocab, max_length=0):
    tokens = []
    indexes = []
    max_len = max_length

    assert (type(lines) is list or tuple), "Input type must be list or tuple."

    if max_len == 0:
        for line in lines:
            token = morphs_extractor(line)
            tokens.append(token)
            length = len(token)
            if max_len < length:
                max_len = length
    else:
        for line in lines:
            token = morphs_extractor(line)
            tokens.append(token)

    for token in tokens:
        if len(token) < max_len:
            temp = token
            for _ in range(len(temp), max_len):
                temp.append('<PAD>')
        else:
            temp = token[:max_len]
        index = []
        for char in temp:
            if char in vocab.keys():
                index.append(vocab[char])
            else:
                index.append(vocab['<UNK>'])
        indexes.append(index)
    return indexes

def make_embedding_vectors(data, embedding_size=300):
    tokens = morphs_process(data)
    wv_model = gensim.models.Word2Vec(min_count=1, window=5, size=embedding_size)
    wv_model.build_vocab(tokens)
    wv_model.train(tokens, total_examples=wv_model.corpus_count, epochs=wv_model.epochs)
    word_vectors = wv_model.wv

    vocab = dict()
    vocab['<PAD>'] = 0
    vocab['<UNK>'] = 1
    idx = 2
    for word in word_vectors.vocab:
        vocab[word] = idx
        idx += 1

    embedding = [np.random.normal(size=300), np.random.normal(size=300)]
    for word in word_vectors.vocab:
        embedding.append(word_vectors[word])
    embedding = np.asarray(embedding)
    vocab_size = len(embedding)

    return embedding, vocab, vocab_size

class data_helper():
    def __init__(self, sequence_max_length=1024):
        # self.alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:’"/|_#$%ˆ&*˜‘+=<>()[]{} ' # 영어

        # self.char_dict = {}
        self.sequence_max_length = sequence_max_length
        # for i,c in enumerate(self.alphabet):
        # 	self.char_dict[c] = i+1

    # def char2vec(self, text):
    # 	data = np.zeros(self.sequence_max_length)
    # 	for i in range(0, len(text)):
    # 		if i > self.sequence_max_length:
    # 			return data
    # 		elif text[i] in self.char_dict:
    # 			data[i] = self.char_dict[text[i]]
    # 		else:
    # 			# unknown character set to be 68
    # 			data[i] = 68
    # 	return data

    def load_csv_file(self, filename, num_classes):
        """
        Load CSV file, generate one-hot labels and process text dataset as Paper did.
        """
        all_data = []
        labels = []
        with open(filename) as f:
            # reader = csv.DictReader(f, fieldnames=['class'], restkey='fields')
            reader = pd.read_csv(f)
            for row in reader:
                # One-hot
                one_hot = np.zeros(num_classes)
                one_hot[int(row['category']) - 1] = 1
                labels.append(one_hot)
                # Char2vec
                data = np.ones(self.sequence_max_length)*68
                text = row['data'] # [-1].lower()
                texts, _, _ = make_embedding_vectors(text)
                all_data.append(texts) ### kor2vec

        f.close()

        return np.array(all_data), np.array(labels)

    def load_dataset(self, dataset_path):
        # Read Classes Info
        with open(dataset_path+"classes.txt") as f:
            classes = []
            for line in f:
                classes.append(line.strip())
        f.close()
        num_classes = len(classes)
        # Read CSV Info
        train_data, train_label = self.load_csv_file(dataset_path+'train.csv', num_classes)
        test_data, test_label = self.load_csv_file(dataset_path+'test.csv', num_classes)

        return train_data, train_label, test_data, test_label

    def batch_iter(self, data, batch_size, num_epochs, shuffle=True):
        """
        Generates a batch iterator for a dataset.
        """
        data = np.array(data)
        data_size = len(data)
        num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
        for epoch in range(num_epochs):
            # Shuffle the dataset at each epoch
            if shuffle:
                shuffle_indices = np.random.permutation(np.arange(data_size))
                shuffled_data = data[shuffle_indices]
            else:
                shuffled_data = data
            for batch_num in range(num_batches_per_epoch):
                start_index = batch_num * batch_size
                end_index = min((batch_num + 1) * batch_size, data_size)
                yield shuffled_data[start_index:end_index]