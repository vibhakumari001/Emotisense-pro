# 🧠 EmotiSense Pro — Text-Based Emotion Detection & Journaling System

EmotiSense Pro is a full-stack web application that detects the emotion
behind any piece of text using a pre-trained transformer model — and turns
every analysis into a personal, private mood journal with its own
statistics dashboard. It goes beyond a plain "type text, get a label" demo
by adding persistence, history, trends, and word-level insight, making it a
more complete and defensible final-year project.

## ✨ What Makes It Different

Most emotion-detection demos stop at a single prediction. EmotiSense Pro
adds a full data layer around that prediction:

- **Persistent Emotion Journal** — every analyzed entry is saved to a local
  SQLite database, not just shown and discarded.
- **Statistics Dashboard** — emotion distribution donut chart, a 7-day
  emotion trend line chart, average confidence, and journaling streak,
  all built from your own real usage data.
- **Signature Word Insight** — a lightweight frequency analysis surfaces
  the words most associated with each emotion you've logged (no extra
  model needed — pure Python text processing).
- **CSV Export** — download your entire journal for further analysis in
  Excel/Sheets or for a report appendix.
- **Light/Dark Theme Toggle** with an animated gradient background.
- **Zero external services** — everything (model, database, charts) runs
  locally; no API keys, no cloud dependency.

## 🧰 Tech Stack

| Layer        | Technology |
|--------------|------------|
| Backend      | Python, Flask |
| ML Model     | Hugging Face Transformers (`j-hartmann/emotion-english-distilroberta-base`) |
| Database     | SQLite (via Python's built-in `sqlite3`) |
| Frontend     | HTML5, CSS3 (custom, no framework), Vanilla JavaScript |
| Charts       | Chart.js (loaded via CDN) |

## 📁 Project Structure

```
emotisense-pro/
├── app.py                    # Flask app: routes, model inference, API endpoints
├── database.py                # SQLite persistence layer + analytics queries
├── config.py                  # Central configuration (model name, emotion metadata)
├── requirements.txt           # Python dependencies
├── .env.example                # Documented environment variables
├── .gitignore
├── README.md
├── data/
│   └── .gitkeep                # Placeholder; emotisense.db is created here at runtime
├── templates/
│   ├── base.html                # Shared layout, navbar, theme toggle
│   ├── index.html               # Analyze page
│   ├── history.html             # Journal history page
│   └── stats.html               # Statistics dashboard page
└── static/
    ├── css/
    │   └── style.css            # All styling, theming, animations
    ├── js/
    │   ├── main.js               # Theme toggle (shared)
    │   ├── analyze.js            # Analyze page logic
    │   ├── history.js            # Journal page logic
    │   └── stats.js              # Dashboard charts logic
    └── img/
        └── favicon.svg
```

## 🚀 Getting Started (VS Code / Local)

### 1. Open the project folder in VS Code

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> The first run downloads the pre-trained model (~300MB) from Hugging Face.
> This needs an internet connection once — after that it's cached locally
> and the app works fully offline.

### 4. (Optional) Configure environment variables

```bash
cp .env.example .env
```

### 5. Run the app

```bash
python app.py
```

### 6. Open in your browser

Go to **http://127.0.0.1:5000**

## 🖥️ How It Works

1. You type text into the Analyze page.
2. JavaScript sends it to the Flask `/predict` endpoint.
3. Flask runs the text through a pre-trained DistilRoBERTa model fine-tuned
   for 7-way emotion classification (joy, sadness, anger, fear, surprise,
   disgust, neutral).
4. The prediction is saved to `data/emotisense.db` along with a timestamp.
5. The **Journal** page reads that history back via `/api/history`.
6. The **Statistics** page aggregates all saved entries via `/api/stats` —
   computing emotion distribution, a 7-day trend, and word frequency —
   and renders it with Chart.js.

## 🔌 API Reference

| Method | Endpoint            | Description                              |
|--------|----------------------|-------------------------------------------|
| POST   | `/predict`            | Analyze text, save entry, return scores    |
| GET    | `/api/history`         | Recent journal entries (JSON)              |
| DELETE | `/api/entry/<id>`      | Delete a single journal entry              |
| POST   | `/api/clear`           | Wipe the entire journal                    |
| GET    | `/api/stats`           | Aggregated statistics for the dashboard    |
| GET    | `/api/export`          | Download journal as CSV                   |

## 📦 Pushing to GitHub

```bash
git init
git add .
git commit -m "Initial commit: EmotiSense Pro emotion detection & journaling system"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

Your personal journal database (`data/emotisense.db`) is excluded via
`.gitignore`, so cloning the repo always starts with a clean, empty journal.

## 🔮 Possible Extensions

- Add user accounts so multiple people can keep separate journals
- Add speech-to-text for voice journaling
- Add multi-language emotion detection
- Deploy to Render/Railway/Hugging Face Spaces for a public live demo
- Add a calendar heatmap view of mood over the month

## 📄 License

This project is open-source and free to use for academic purposes.
