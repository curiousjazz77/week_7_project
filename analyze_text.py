from collections import Counter
from heapq import *
import re
import unicodedata
import urllib.request


class GutenbergAnalyzer:
    def __init__(self, url):
        self.viable_word_line = False
        self.url = url
        self.total_words = []
        self.unique_words = set()

    def remove_control_characters(self, s):
        return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")


    def get_words_per_line(self, line):
        words_only = re.sub(r'\W+', ' ', line)
        control_characters_removed = self.remove_control_characters(words_only)
        sanitized_line = control_characters_removed.strip().split()
        return sanitized_line


    def getTotalUniqueWords(self):
        if len(self.total_words) == 0:
            self.parse_file_for_all_words()
        return len(set(self.total_words))


    def parse_file(self):
        data_file = urllib.request.urlopen(self.url)
        for line in data_file:
            decoded_line = line.decode("utf-8")
            yield decoded_line


    def check_if_viable_line(self, line):
        if "THE PREFACE" in line:
            self.viable_word_line = True
        if "End of Project" in line:
            self.viable_word_line = False
        return


    def parse_file_for_all_words(self):
        viable_word_line = False
        for line in self.parse_file():
            self.check_if_viable_line(line)
            if self.viable_word_line:
                self.total_words.extend(self.get_words_per_line(line))
            else:
                continue

    def getTotalNumberOfWords(self):
        self.parse_file_for_all_words()
        return len(self.total_words)

    def get20MostFrequentWords(self):
        k = 20
        if len(self.total_words) == 0:
            self.parse_file_for_all_words()
        c = Counter(self.total_words)

        heap = []
        for word, frequency in c.items():
            heappush(h, [-frequency, word])
        res = []
        while k > 0:
            f, w = heappop(h)
            res.append([w, f])
        return res




def main():
    url = "https://raw.githubusercontent.com/GITenberg/The-Picture-of-Dorian-Gray_174/master/174.txt"
    g = GutenbergAnalyzer(url)
    total_words = g.getTotalNumberOfWords()
    print('Total words in novel', total_words)
    unique_words = g.getTotalUniqueWords()
    print('Number of unique words in novel', unique_words)



if __name__ == "__main__":
    main()
