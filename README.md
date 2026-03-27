# 🎯 YouTube Sentiment Analysis System

A 3-agent system that analyzes emotions in YouTube video comments using AI.

## 🤖 How It Works

- **Agent 1 (Fetcher):** Fetches videos and comments from YouTube
- **Agent 2 (Brain):** Analyzes comment sentiments using GPT
- **Agent 3 (Visualizer):** Displays results on a dashboard

## ⚙️ Setup

### Requirements
- Python 3.10+
- Node.js 18+
- YouTube Data API v3 key
- OpenAI API key

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd youtube-sentiment-analysis
```

### 2. Setup Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Open .env and add your API keys
```

### 3. Setup Frontend
```bash
cd frontend
npm install
```

## 🚀 Usage

### Fetch Data
```bash
cd backend
python agents/fetcher.py
```

### Run Analysis
```bash
python agents/brain.py
```

### Open Dashboard
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` in your browser.

## 🔑 Getting API Keys

- **YouTube:** [console.cloud.google.com](https://console.cloud.google.com)
- **OpenAI:** [platform.openai.com](https://platform.openai.com)

## 📊 Analyzed Emotions

Anger, Joy, Trust, Fear, Surprise, Sadness, Disgust, Anticipation

---

# 🎯 YouTube Duygu Analizi Sistemi

YouTube'daki popüler videoların yorumlarını yapay zeka ile analiz eden 3 ajanlı sistem.

## 🤖 Nasıl Çalışır?

- **Ajan 1 (Fetcher):** YouTube'dan video ve yorumları çeker
- **Ajan 2 (Brain):** GPT ile yorumların duygu analizini yapar
- **Ajan 3 (Visualizer):** Sonuçları dashboard'da gösterir

## ⚙️ Kurulum

### Gereksinimler
- Python 3.10+
- Node.js 18+
- YouTube Data API v3 key
- OpenAI API key

### 1. Repoyu İndir
```bash
git clone https://github.com/KULLANICI_ADIN/REPO_ADIN.git
cd youtube-sentiment-analysis
```

### 2. Backend Kur
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını aç, kendi API key'lerini yaz
```

### 3. Frontend Kur
```bash
cd frontend
npm install
```

## 🚀 Kullanım

### Veri Çek
```bash
cd backend
python agents/fetcher.py
```

### Analiz Yap
```bash
python agents/brain.py
```

### Dashboard'u Aç
```bash
cd frontend
npm run dev
```
Tarayıcıda `http://localhost:3000` aç.

## 🔑 API Key Alma

- **YouTube:** [console.cloud.google.com](https://console.cloud.google.com)
- **OpenAI:** [platform.openai.com](https://platform.openai.com)

## 📊 Analiz Edilen Duygular

Öfke, Sevinç, Güven, Korku, Sürpriz, Üzüntü, İğrenme, Beklenti