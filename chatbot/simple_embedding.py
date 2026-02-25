import re
import math
from collections import Counter

class SimpleEmbedder:
    def __init__(self, all_texts):
        self.vocab = self.build_vocab(all_texts)

    def preprocess(self, text):
        return re.findall(r"\w+", text.lower())

    def build_vocab(self, texts):
        vocab = set()
        for text in texts:
            words = self.preprocess(text)
            vocab.update(words)
        return sorted(vocab)

    def encode(self, text):
        words = self.preprocess(text)
        word_count = Counter(words)
        return [word_count.get(word, 0) for word in self.vocab]

    def cosine_similarity(self, v1, v2):
        dot = sum(a*b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a*a for a in v1))
        norm2 = math.sqrt(sum(b*b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)
