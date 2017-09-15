from textblob.classifiers import NaiveBayesClassifier
from plagiarism import bag_of_words, tokenizers


train = [
    ('sim', 'pos'),
    ('s', 'pos'),
    ('claro', 'pos'),
    ('vamos', 'pos'),
    ('vamos sim', 'pos'),
    ('agora', 'pos'),
    ('só se for agora', 'pos'),
    ('bora', 'pos'),
    ('nao', 'neg'),
    ('não', 'neg'),
    ('n', 'neg'),
    ('depois', 'neg'),
    ('agora não dá', 'neg'),
    ('podemos fazer amanhã', 'neg'),
    ('jamais', 'neg'),
    ('nunca', 'neg'),
    ('talvez', 'neg'),
]


def extract(text):
    tokens = tokenizers.stemmize(
        text,
        language='portuguese',
    )
    features = bag_of_words.bag_of_words(tokens, 'boolean')
    return dict(features)


def classify(text):
    classifier = NaiveBayesClassifier(train, feature_extractor=extract)
    prob_dist = classifier.prob_classify(text)
    label = prob_dist.max()
    if prob_dist.prob(label) > 0.5:
        return label
    else:
        return None
