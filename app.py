"""
app.py
EmotiSense Pro — Text-Based Emotion Detection System

A Flask web application that uses a pre-trained transformer model to
detect emotion in user-entered text, journals every analysis to a local
SQLite database, and visualizes emotional trends over time.

Routes:
    /              -> Analyze page (type text, get instant emotion prediction)
    /history       -> Journal history of everything analyzed
    /stats         -> Statistics dashboard (charts, word frequency, streaks)
    /predict       -> POST endpoint that runs the model and saves the entry
    /api/history   -> JSON: recent journal entries
    /api/stats     -> JSON: aggregated statistics for the dashboard charts
    /api/export    -> Download all journal entries as CSV
    /api/entry/<id> (DELETE) -> remove a single journal entry
    /api/clear     -> wipe the whole journal
"""

import json
import csv
import io

from flask import Flask, render_template, request, jsonify, Response
from transformers import pipeline

import config
import database as db

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Model loading (runs once at startup)
# ---------------------------------------------------------------------------
print(f"Loading emotion model '{config.MODEL_NAME}'... (first run downloads it)")
emotion_classifier = pipeline(
    "text-classification",
    model=config.MODEL_NAME,
    top_k=None,
)
print("Model loaded. EmotiSense Pro is ready.")

db.init_db()


def classify_text(text):
    """Run the model on text and return a clean, sorted result list."""
    raw_results = emotion_classifier(text)[0]
    raw_results = sorted(raw_results, key=lambda x: x["score"], reverse=True)

    formatted = []
    for r in raw_results:
        label = r["label"].lower()
        meta = config.EMOTION_META.get(label, {"emoji": "❓", "color": "#607D8B"})
        formatted.append({
            "label": label,
            "score": round(r["score"] * 100, 2),
            "emoji": meta["emoji"],
            "color": meta["color"],
        })
    return formatted


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html", active_page="analyze")


@app.route("/history")
def history_page():
    return render_template("history.html", active_page="history")


@app.route("/stats")
def stats_page():
    return render_template("stats.html", active_page="stats")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please enter some text."}), 400
    if len(text) > 800:
        return jsonify({"error": "Please keep text under 800 characters."}), 400

    results = classify_text(text)
    top_emotion = results[0]

    db.save_entry(
        text=text,
        top_emotion=top_emotion["label"],
        top_score=top_emotion["score"],
        all_scores_json=json.dumps(results),
    )

    return jsonify({
        "input_text": text,
        "top_emotion": top_emotion,
        "all_emotions": results,
    })


@app.route("/api/history")
def api_history():
    limit = request.args.get("limit", config.HISTORY_PAGE_LIMIT, type=int)
    entries = db.get_recent_entries(limit=limit)
    for e in entries:
        e["all_scores"] = json.loads(e["all_scores"])
        meta = config.EMOTION_META.get(e["top_emotion"], {})
        e["emoji"] = meta.get("emoji", "❓")
        e["color"] = meta.get("color", "#607D8B")
    return jsonify(entries)


@app.route("/api/entry/<int:entry_id>", methods=["DELETE"])
def api_delete_entry(entry_id):
    db.delete_entry(entry_id)
    return jsonify({"success": True})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    db.clear_all()
    return jsonify({"success": True})


@app.route("/api/stats")
def api_stats():
    distribution = db.get_emotion_distribution()
    trend = db.get_daily_trend(days=7)
    summary = db.get_summary_stats()

    top_words_overall = db.get_top_words(limit=12)
    words_by_emotion = {}
    for emotion in config.EMOTION_META.keys():
        words = db.get_top_words(emotion=emotion, limit=6)
        if words:
            words_by_emotion[emotion] = words

    return jsonify({
        "distribution": distribution,
        "trend": trend,
        "summary": summary,
        "top_words": top_words_overall,
        "words_by_emotion": words_by_emotion,
        "emotion_meta": config.EMOTION_META,
    })


@app.route("/api/export")
def api_export():
    entries = db.get_all_entries()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "text", "top_emotion", "top_score", "created_at"])
    for e in entries:
        writer.writerow([e["id"], e["text"], e["top_emotion"], e["top_score"], e["created_at"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=emotisense_journal.csv"},
    )


if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
