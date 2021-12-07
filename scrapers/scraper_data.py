import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
import plotly.express as px


def generate_basic_wordcloud(data, title, mask=None):
    cloud = WordCloud(scale=3,
                      max_words=150,
                      colormap='RdYlGn',
                      mask=mask,
                      # stopwords=stopwords,
                      background_color='white',
                      contour_color='#5d0f24',
                      contour_width=3,
                      collocations=True).generate_from_text(data)
    plt.figure(figsize=(10, 8))
    plt.imshow(cloud)
    plt.axis('off')
    plt.title(title, fontsize=13)
    plt.show()


# 6460
# 3708
def main():
    df = pd.read_csv('comments_blitz_3.csv')
    locations = df['location'].astype('str')
    for location in locations:
        if 'Russia' in location:
            locations[location] = 'Russian Federation'
    count = locations.value_counts(dropna=True)
    print(count['United States'])
    num_comments = len(df)
    numnan = 3708
    num_comments -= numnan
    ten_most_popular_locations = count[:11]
    ten_most_popular_locations = ten_most_popular_locations.astype('float')
    df['comment'] = df['comment'].astype('string')
    for i in range(len(ten_most_popular_locations)):
        ten_most_popular_locations[i] = (ten_most_popular_locations[i] / num_comments) * 100
    print(ten_most_popular_locations)
    comments = df['comment'].to_string()
    total = 0
    for sentiment in df['sentiment']:
        total += sentiment
    total /= len(df['sentiment'])
    blob_comments = TextBlob(comments)
    sentiment = blob_comments.sentiment.polarity
    print(" ")
    print("Sentiment:", total)
    #generate_basic_wordcloud(comments, "Most Common Words in Comments")
    countsent = df['sentiment'].value_counts(dropna=True)
    print(countsent)
    fig = px.histogram(df, 'sentiment', marginal="violin", title='Sentiment Distribution')
    fig.show()


if __name__ == '__main__':
    main()
