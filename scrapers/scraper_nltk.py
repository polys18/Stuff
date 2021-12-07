import nltk
import pandas as pd


def get_trigrams(text):
    words = nltk.word_tokenize(text)
    finder = nltk.collocations.TrigramCollocationFinder.from_words(words)
    # trigrams = finder.ngram_fd.items()
    trigrams = sorted(finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
    print(trigrams[:21])


def main():
    df = pd.read_csv('comments_blitz_3.csv')
    comments = df['comment'].to_string(index=False)
    get_trigrams(comments)


if __name__ == '__main__':
    main()
