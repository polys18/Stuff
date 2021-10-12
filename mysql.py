import sqlite3
import pandas as pd


def add_to_db():
    conn = sqlite3.connect('scraperdb.db')
    conn.execute('''CREATE TABLE COMMENTS
            (GAME_ID TEXT,
            COMMENTER_ID TEXT,
            DATE TEXT,
            COMMENT TEXT,
            NUM_FOUND_HELPFUL TEXT,
            SENTIMENT REAL,
            SUGGESTION TEXT);''')

    df = pd.read_csv("comments_db.csv")
    for i in range(len(df)):
        commenter_name = df["commenter_name"][i]
        sentiment = df["sentiment"][i]
        comment = df["comment"][i]
        game_id = df["game_name"][i]
        date = df["date"][i]
        num_found_helpful = df["num_found_helpful"][i]
        suggestion = df["suggestion"][i]

        conn.execute("INSERT INTO COMMENTS VALUES (?,?,?,?,?,?,?)",
                     (game_id, commenter_name, date, comment, num_found_helpful, sentiment, suggestion))
        conn.commit()

    conn.close()


def main():
    add_to_db()


if __name__ == '__main__':
    main()
