import os
import random
import openai
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
import webbrowser

openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)
api = Api(app)
CORS(app)

def generate_response(dialog):
    instruction = 'Instruction: given a dialog context, you need to respond empathetically.'
    dialog_text = ' '.join(dialog)
    prompt = f"{instruction}\n[CONTEXT]: {dialog_text}\n"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=50
    )
    generated_text = response.choices[0].message.get("content", "").strip()
    return generated_text

def sentiment_and_language_finder(user_dialog):
    prompt = (
        "Sentiment analysis: classify the emotion conveyed in the dialog. "
        "Please reply with only 'happy', 'sad', or 'neutral'.\n"
        "Language: specify the language for the song recommendation (e.g., English, Kannada, Hindi).\n"
        f"[CONTEXT]: {user_dialog}\n"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=50
    )
    response_text = response.choices[0].message.get("content", "").strip().lower()
    sentiment, language = 'neutral', 'english'  # Default values
    for token in response_text.split():
        if token in ['happy', 'sad', 'neutral']:
            sentiment = token
        elif token in ['english', 'kannada', 'hindi']:
            language = token
    return sentiment, language

def get_song_recommendations(mood, language):
    base_directory = os.path.join(os.getcwd(), language.lower() + "Songs", mood.lower() + "Song")
    print("Base directory:", base_directory)
    
    # Check if the directory exists
    if not os.path.exists(base_directory):
        print(f"Directory {base_directory} does not exist.")
        return []
    
    # List the contents of the directory
    songs = os.listdir(base_directory)
    print("Songs in directory:", songs)
    
    # Check if there are any songs in the directory
    if not songs:
        print(f"No songs found in directory {base_directory}.")
        return []
    
    # Shuffle the list of songs
    random.shuffle(songs)
    
    # Select three random songs from the shuffled list
    random_songs = songs[:3]
    
    song_paths = [os.path.join(base_directory, song) for song in random_songs]
    return song_paths

class ResponseResource(Resource):
    def post(self):
        data = request.get_json()
        dialog = data.get('dialog', [])
        generated_text = generate_response(dialog)
        user_dialog = dialog[-1]
        emotion, language = sentiment_and_language_finder(user_dialog)

        # Get three song recommendations based on mood and language
        song_paths = get_song_recommendations(emotion, language)

        response_data = {'generated_response': generated_text, 'emotion': emotion, 'song_paths': song_paths}
        return jsonify(response_data)

api.add_resource(ResponseResource, '/get_response')

if __name__ == '__main__':
    webbrowser.open('home.html')
    app.run()

