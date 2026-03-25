---
title: MoodBeats AI
emoji: 🎵
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---

# MoodBeats AI — Emotion-Powered Music

Your emotion. Your frequency. Your music. This application uses DeepFace for facial emotion analysis, TextBlob for vocal sentiment parsing, and Biometric simulation to provide personalized music recommendations from YouTube.

## Features
- **Optic Scan**: Real-time facial expression analysis.
- **Vocal Sentiment**: NLP-based sentiment analysis of spoken words.
- **Biometrics**: Heart rate mapping to music energy (Pulse simulation).
- **Global Music**: Supports Sinhala, Hindi, and English songs.

## Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Set `YOUTUBE_API_KEY` environment variable.
3. Run the app: `python app.py`   Hosted link is available - https://mrcharcoal-moodbeats.hf.space

## Hugging Face Deployment
This space is configured to run via Docker. Ensure you set the `YOUTUBE_API_KEY` in the **Settings -> Secrets** tab of your Space for it to function correctly.
