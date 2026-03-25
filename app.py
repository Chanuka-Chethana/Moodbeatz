from flask import Flask, render_template, request, jsonify
import random
import os
import cv2
import numpy as np
import base64
from deepface import DeepFace
from googleapiclient.discovery import build
from deep_translator import GoogleTranslator
from textblob import TextBlob

app = Flask(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyDPPhwfgvqw9xL-hctWTExpwl1XnaK6pHE")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# --- PORTFOLIO FAIL-SAFE (Ensures app works even if API is down) ---
FALLBACK_SONGS = {
    'happy': [
        {'id': '09R8_2nJtjg', 'title': 'Sugar - Maroon 5 (Global Hit)'},
        {'id': 'S0fGqR7zLqI', 'title': 'Hanthana Sihine - Sinhala Classic'},
        {'id': '79DIFeS7atI', 'title': 'Pharrell Williams - Happy'}
    ],
    'sad': [
        {'id': 'hLQl3WQQoQ0', 'title': 'Adele - Someone Like You'},
        {'id': '_c78Vz6l7X8', 'title': 'Manike Mage Hithe (Cover)'}
    ],
    'energetic': [
        {'id': 'fJ9rUzIMcZQ', 'title': 'Queen - Don\'t Stop Me Now'},
        {'id': 'kJQP7kiw5Fk', 'title': 'Luis Fonsi - Despacito'}
    ],
    'calm': [
        {'id': 'fHI8X4OXskQ', 'title': 'Marconi Union - Weightless (Scientific Calm)'},
        {'id': 'L0MA7gzf_zU', 'title': 'Lofi Hip Hop - Study Beats'}
    ]
}

def find_youtube_song(mood, language):
    try:
        query = f"{language} {mood} mood hit songs"
        
        request_api = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=15,
            type='video',
            videoCategoryId='10', # Music category
            videoEmbeddable='true' # MUST BE EMBEDDABLE FOR IFRAME
        )
        response = request_api.execute()
        search_results = response.get('items', [])
        
        if not search_results:
            # Fallback search if category filtering was too strict
            request_api = youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=10,
                type='video',
                videoEmbeddable='true'
            )
            response = request_api.execute()
            search_results = response.get('items', [])

        if not search_results:
            raise Exception("No results found — entering Fail-Safe Mode.")
            
        selected_song = random.choice(search_results)
        video_id = selected_song.get('id', {}).get('videoId')
        title = selected_song.get('snippet', {}).get('title')
        
        if not video_id:
            raise Exception("Invalid video ID.")

        return jsonify({
            'title': title,
            'language': language,
            'detected_mood': mood,
            'video_id': video_id,
            'thumbnail': selected_song.get('snippet', {}).get('thumbnails', {}).get('high', {}).get('url'),
            'status': 'live'
        })
    except Exception as e:
        print(f"YouTube Search Error: {e}")
        # RESILIENCE: Play from curated Fail-safe list
        import random as rnd
        fallback = rnd.choice(FALLBACK_SONGS.get(mood, FALLBACK_SONGS['calm']))
        return jsonify({
            'title': fallback['title'],
            'language': f"{language} (Optimized Mode)",
            'detected_mood': mood,
            'video_id': fallback['id'],
            'status': 'fail-safe'
        })
    except Exception as e:
        print(f"YouTube Search Error: {e}")
        return jsonify({'error': 'Failed to fetch song from YouTube.'})


@app.route('/')
def index():
    return render_template('index.html')


# --- MOOD FETCH (From Heartbeat or General) ---
@app.route('/get_music_by_mood', methods=['POST'])
def get_music_by_mood():
    data = request.json
    mood = data.get('mood', 'calm')
    language = data.get('language', 'english')
    return find_youtube_song(mood, language)


# --- WEBCAM AI SCAN ---
@app.route('/scan_emotion', methods=['POST'])
def scan_emotion():
    try:
        data = request.json
        image_data = data['image']
        language = data.get('language', 'english')

        # 1. Decode the image
        encoded_data = image_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 2. Use DeepFace to analyze
        predictions = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        
        emotion = predictions[0]['dominant_emotion']
        print(f"AI Detected Face Emotion: {emotion}")

        # 3. Map AI emotions to Music Categories
        mapped_mood = "calm" # Default

        if emotion in ['happy', 'surprise']:
            mapped_mood = 'happy'
        elif emotion in ['sad', 'fear']:
            mapped_mood = 'sad'
        elif emotion in ['angry', 'disgust']:
            mapped_mood = 'energetic'
        elif emotion == 'neutral':
            mapped_mood = 'calm'

        return find_youtube_song(mapped_mood, language)

    except Exception as e:
        print(f"Face AI Error: {e}")
        return jsonify({'error': 'Could not analyze face. Please try again.'})


# --- VOICE AI SCAN (Text Sentiment) ---
@app.route('/scan_voice_text', methods=['POST'])
def scan_voice_text():
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'english')
        
        print(f"Voice recognized text ({language}): {text}")

        if language.lower() != 'english':
            text = GoogleTranslator(source='auto', target='en').translate(text)
            print(f"Translated to English: {text}")

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.4:
            mood = 'happy'
        elif polarity < -0.1:
            mood = 'sad'
        elif 0 <= polarity <= 0.4:
            mood = 'calm'
        else:
            mood = 'energetic'

        print(f"Voice Detected Mood: {mood}")

        return find_youtube_song(mood, language)

    except Exception as e:
        print(f"Voice AI Error: {e}")
        return jsonify({'error': 'Could not analyze voice sentiment. Please try again.'})


if __name__ == '__main__':
    app.run(debug=True)