"""
config.py
Centralized configuration for EmotiSense Pro.
Keeping these in one place makes the model/behaviour easy to tune
without touching application logic.
"""

import os

# Hugging Face model used for inference (pre-trained, no training required)
MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"

# Flask settings
DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
PORT = int(os.environ.get("FLASK_PORT", 5000))

# How many recent journal entries to show on the History page
HISTORY_PAGE_LIMIT = 100

# Emoji + color mapping used across backend responses and charts
EMOTION_META = {
    "joy":      {"emoji": "😄", "color": "#FFC107"},
    "sadness":  {"emoji": "😢", "color": "#4C6FFF"},
    "anger":    {"emoji": "😠", "color": "#FF5C5C"},
    "fear":     {"emoji": "😨", "color": "#9B5DE5"},
    "surprise": {"emoji": "😲", "color": "#FF9F1C"},
    "disgust":  {"emoji": "🤢", "color": "#2EC4B6"},
    "neutral":  {"emoji": "😐", "color": "#8892A6"},
}
