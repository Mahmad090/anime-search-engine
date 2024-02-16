from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import nltk
nltk.download('stopwords')
import re
from nltk.corpus import stopwords
from flask_cors import CORS
data=pd.read_csv("refined_data.csv")
# description_data=pd.read_csv("refined_data.csv")
# image_data=pd.read_csv("Anime_image1_50.csv")
def slugify(text):
  text = text.lower().replace(" ", "-")

  text = re.sub(r"[^\w\-]+", "", text)

  text = text.strip("-")

  return text
def clean_string(input_string, custom_stopwords=None):
    # Download NLTK stopwords
    # nltk.download('stopwords')

    # Define a default set of stopwords using NLTK
    default_stopwords = set(stopwords.words('english'))

    # If custom stopwords are provided, add them to the set
    if custom_stopwords is not None:
        default_stopwords.update(custom_stopwords)

    # Remove special characters and convert to lowercase
    cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string).lower()

    # Split the string into words
    words = cleaned_string.split()

    # Remove stopwords
    filtered_words = [word for word in words if word not in default_stopwords]

    # Join the filtered words back into a string
    result_string = ' '.join(filtered_words)

    return result_string
custom_stopwords = ["anime", "looking", "it","main character","fall"]
import spacy

# Load the pre-trained word embeddings model
nlp = spacy.load('en_core_web_md')
def calculate_similarity(row,prompt):
    word1 = nlp(prompt)
    word2=nlp(row)
    common_keywords = set(token.text.lower() for token in word1 if token.text.lower() in word2.text.lower())
    custom_similarity = len(common_keywords) / max(len(word1), len(word2))

    return custom_similarity
# def get_image_address(anime_name):
   
#     # Search for the anime name in the dataset and fetch the image address
#     anime_info =image_data[image_data['Name'] == anime_name]
#     if not anime_info.empty:
#         image_address = anime_info.iloc[0]['ImageUrl']
#         return image_address
#     else:
#         return "Image address not found for " + anime_name
# def get_description(anime_name):
#     # Search for the anime name in the dataset and fetch the description
#     anime_info = description_data[description_data['Name'] == anime_name]
#     if not anime_info.empty:
#         description = anime_info.iloc[0]['Description']
#         return description
#     else:
#         return ""
def clean_filename(name):
    # Remove invalid characters from the file name
    invalid_chars = {'/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.'}
    return ''.join(char if char not in invalid_chars else '_' for char in name)
def get_similarity(prompt, page_number=1, items_per_page=10):
    cleaned_prompt = clean_string(prompt, custom_stopwords)
    data['similarities'] = data.apply(lambda row: calculate_similarity(row['string_tags'], cleaned_prompt), axis=1)
    sorted_data = data.sort_values(by='similarities', ascending=False)

    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page

    sliced_data = sorted_data.iloc[start_index:end_index]

    anime_list = []
    for _, row in sliced_data.iterrows():
        anime_info = {
            'Name': row['Name'],
            'Link': 'https://www.anime-planet.com/anime/'+slugify(row['Name'])
        }
        anime_list.append(anime_info)

    return json.dumps(anime_list)

app = Flask(__name__)

CORS(app)
@app.route('/')
def index():
    return render_template("index.html")
current_page = 1
@app.route('/process', methods=['POST'])
def process():
    global current_page
    data = request.json
    text = data['text']
    # with open('./UserPrompts.txt', 'a') as file:
    # # Write the text to the file
    #     file.write(text)
    jsonData = get_similarity(text, current_page)  # Pass the current page number to the function
    current_page += 1  # Increment the page number for the next request
    return jsonData

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
