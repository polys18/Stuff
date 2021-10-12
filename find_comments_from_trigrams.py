import pandas as pd
from scraper_nltk import get_trigrams


def find_comments_from_trigrams(trigram):
    df = pd.read_csv('comments_blitz_3.csv')
    comments = df['comment'].tolist()
    selected_comments = ""
    for comment in comments:
        if trigram in str(comment):
            selected_comments += comment
    return selected_comments


def main():
    text = find_comments_from_trigrams("------")
    get_trigrams(text)


if __name__ == '__main__':
    main()
