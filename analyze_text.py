from collections import Counter, defaultdict
from heapq import *
import random
import re
import unicodedata
import urllib.request


class GutenbergAnalyzer:
    def __init__(self, url):
        self.viable_word_line = False
        self.url = url
        self.total_words = []
        self.unique_words = set()
        self.common_words_url = "https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt"
        self.common_words = []
        self.interesting_word_mode = False
        self.chapter_progression_words = defaultdict(lambda: defaultdict(int))

    def remove_control_characters(self, s):
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    def get_words_per_line(self, line):
        # words_only = re.sub(r'\W+', ' ', line)
        # words_only = re.sub(r"(\w+'\w+)", " ", line)
        words_only = re.sub(r"(^|\W)\d+", " ", line)
        control_characters_removed = self.remove_control_characters(words_only)
        sanitized_line = (
            control_characters_removed.strip()
            .replace(".", "")
            .replace('"', "")
            .replace("'", "")
            .replace(",", "")
            .replace("-", "")
            .replace("_", "")
            .replace("!", "")
            .replace("?", "")
            .split()
        )
        sanitized_line = [x.lower() for x in sanitized_line]
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
            self.chapter_progression_words["PREFACE"]  # add first
        if "End of Project" in line:
            self.viable_word_line = False
        return

    def parse_file_for_all_words(self):
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
            heappush(heap, [-frequency, word])
        res = []
        while k > 0:
            f, wd = heappop(heap)
            if self.interesting_word_mode:
                if wd not in self.common_words:
                    res.append([wd, -f])
                    k -= 1
                else:
                    continue
            else:
                res.append([wd, -f])
                k -= 1
        return res

    def get20LeastFrequentWords(self):
        k = 20
        if len(self.total_words) == 0:
            self.parse_file_for_all_words()
        c = Counter(self.total_words)

        heap = []
        for word, frequency in c.items():
            heappush(heap, [frequency, word])
        res = []
        while k > 0:
            f, wd = heappop(heap)
            if self.interesting_word_mode:
                if wd not in self.common_words:
                    res.append([wd, f])
                    k -= 1
                else:
                    continue
            else:
                res.append([wd, f])
                k -= 1
        return res

    def parse_most_common_words(self):
        data_file = urllib.request.urlopen(self.common_words_url)
        for line in data_file:
            decoded_line = line.decode("utf-8")
            sanitized_line = self.get_words_per_line(decoded_line)
            sanitized_line = [x.lower() for x in sanitized_line]
            self.common_words.extend(sanitized_line)
        self.common_words = set(self.common_words)

    def get20MostInterestingFrequentWords(self):
        self.parse_most_common_words()
        self.interesting_word_mode = True
        return self.get20MostFrequentWords()

    def getFrequencyOfWord(self, word):  # per chapter
        current_key = "PREFACE"
        for line in self.parse_file():
            self.check_if_viable_line(line)
            if self.viable_word_line:
                if "CHAPTER" in line:
                    line = self.remove_control_characters(line)
                    current_key = line
                words = self.get_words_per_line(line)
                for w in words:
                    self.chapter_progression_words[current_key][w] += 1

            else:
                continue
        res = []
        for k, v in self.chapter_progression_words.items():
            if w in v:
                res.append(self.chapter_progression_words[k][w])

        total_chapters = int(current_key.split()[1])
        assert len(res) == total_chapters
        return res

    def getChapterQuoteAppears(self, quote):
        current_chapter = "PREFACE"
        quote_arr = quote.split()

        so_far = ""
        multi_yield = self.parse_file()
        while True:
            try:
                line = next(multi_yield)
                self.check_if_viable_line(line)
                if self.viable_word_line:
                    line = self.remove_control_characters(line)
                    if "CHAPTER" in line:
                        current_chapter = line
                    if quote_arr[0] in line:
                        so_far += line
                        next_line = next(multi_yield)
                        so_far += " "
                        so_far += next_line
                        if quote in so_far:
                            return current_chapter.split()[1]
                        else:
                            so_far = ""
            except StopIteration:
                break
        return -1

    def find_next_word(self, start_word):
        multi_yield = self.parse_file()
        next_word_list = []
        while True:
            try:
                line = next(multi_yield)
                self.check_if_viable_line(line)
                if self.viable_word_line:
                    line = self.remove_control_characters(line)
                    line = [x.lower() for x in line.split()]
                    if not line:
                        continue
                    if start_word.lower() in line:
                        for idx, word in enumerate(line):
                            if word == start_word.lower() and idx + 1 < len(line):
                                next_word_list.append(line[idx + 1])
                    else:
                        continue
                else:
                    continue

            except StopIteration:
                break
        # PICK RANDOM ITEM
        if len(next_word_list) > 0:
            random_next_word = random.choice(next_word_list)
            return random_next_word
        else:
            return ""

    def generate_sentence(self, start_word):
        res = [start_word]
        next_word_list = []

        k = 20
        while k > 0:
            next_word = self.find_next_word(res[-1])
            if next_word == "":
                continue
            res.append(next_word)
            k -= 1

        res.append(".")
        return " ".join(res)


def main():
    url = "https://raw.githubusercontent.com/GITenberg/The-Picture-of-Dorian-Gray_174/master/174.txt"
    g = GutenbergAnalyzer(url)
    total_words = g.getTotalNumberOfWords()
    print("Total words in novel", total_words)
    unique_words = g.getTotalUniqueWords()
    print("Number of unique words in novel", unique_words)

    top_20 = g.get20MostFrequentWords()
    print("Top 20 words")
    print(*top_20, sep="\n")
    print("\n")

    top_20_interesting = g.get20MostInterestingFrequentWords()
    print("Top 20 interesting words")
    print(*top_20_interesting, sep="\n")
    print("\n")

    bottom_20 = g.get20LeastFrequentWords()
    print("Top 20 words")
    print(*bottom_20, sep="\n")
    print("\n")

    word = "dorian"
    frequency_by_chapter = g.getFrequencyOfWord(word)
    print("Frequency of word: [", word, "] per chapter", frequency_by_chapter)
    print("\n")

    word = "the"
    frequency_by_chapter = g.getFrequencyOfWord(word)
    print("Frequency of word:[", word, "] per chapter", frequency_by_chapter)
    print("\n")

    quote = "Yes, Dorian, you will always be fond of me"
    print("Quote: ", quote, "appears in chapter", g.getChapterQuoteAppears(quote))
    print("\n")

    """This takes quite some time; A trie built once would be faster"""
    start_word = "The"
    generated_sentence = g.generate_sentence(start_word)
    print(generated_sentence)


if __name__ == "__main__":
    main()
