import json
import nltk
import pandas as pd
from flask import Flask, jsonify, request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# from keybert import KeyBERT
# kw_model = KeyBERT(model='all-mpnet-base-v2')

nltk.download('vader_lexicon')
# Load the VADER model
sid = SentimentIntensityAnalyzer()
app = Flask(__name__)

# df = pd.read_json('Video_Games.json', lines=True)
df = pd.read_json('Appliances_5.json', lines=True)


def get_sentiment(text):
    temp = sid.polarity_scores(text)
    if temp['compound'] >= 0.05:
        return 'Positive'
    elif temp['compound'] <= - 0.05:
        return 'Negative'
    else:
        return 'Neutral'


def get_summary(text):
    # keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', highlight=False, top_n=5)
    # keywords_list = list(dict(keywords).keys())
    # return keywords_list
    return []


def get_reviews_by_product_id(product_id):
    reviews = []
    filtered_df = df[df['asin'] == product_id]
    for index, row in filtered_df.iterrows():
        review = {'review_id': index, 'reviewer_name': row['reviewerName'], 'review_text': row['reviewText'],
                  'sentiment': get_sentiment(row['reviewText'])}
        reviews.append(review)

    product_df = pd.read_json('products.json', lines=True)
    for index, product in product_df.iterrows():
        if product['asin'] == product_id:
            summary = product['review_summary']  # Add your own summary

    return {
        'product_id': product_id,
        'summary': summary,
        'reviews': reviews
    }


def generate_review_summary():
    # Group the dataframe by 'asin'
    grouped = df.groupby('asin')
    print(grouped.head())
    output_data = []

    for asin, group in grouped:
        review_text = '  '.join(group['reviewText'].tolist())

        review_summary = get_summary(review_text)

        output = {}
        output['asin'] = asin
        output['review_summary'] = review_summary
        output_data.append(output)

    # Open a new output file for writing
    with open('products.json', 'w') as f:
        for entry in output_data:
            f.write(json.dumps(entry))
            f.write('\n')


@app.route('/products/<string:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    product_reviews = get_reviews_by_product_id(product_id)

    return jsonify(product_reviews)


@app.route('/products', methods=['GET'])
def get_products():
    product_df = pd.read_json('products.json', lines=True)
    output = []
    products = []
    for index, row in product_df.iterrows():
        product = {'product_id': row['asin'], 'summary': row['review_summary']}
        products.append(product)

    output.append({'category': 'Video Games', 'products': products})
    return jsonify(output)


@app.route('/add_review', methods=['POST'])
def add_review():
    # Get review data from POST request
    print(request.json)
    review_data = request.json

    review = {'reviewText': review_data['review_text'], 'asin': review_data['product_id'], 'reviewerName': review_data['reviewer_name']}
    product = {'asin': review_data['product_id'], 'review_summary': get_summary(review_data['review_text'])}

    review_df = pd.read_json('Appliances_5.json', lines=True)
    product_df = pd.read_json('products.json', lines=True)

    review_df_ = pd.DataFrame([review])
    review_df = pd.concat([review_df, review_df_], ignore_index=True)

    product_df_ = pd.DataFrame([product])
    product_df = pd.concat([product_df, product_df_], ignore_index=True)

    print("DOne")
    review_df.to_json('Appliances_5.json', orient='records', lines=True)
    product_df.to_json('products.json',  orient='records', lines=True)

    return jsonify({'message': 'Review added successfully'})


if __name__ == '__main__':
    generate_review_summary()
    app.run(debug=True)
