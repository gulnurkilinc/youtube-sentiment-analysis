<div align="center">

# 🎀 YouTube Sentiment Analysis System 🎀
# 🎀 YouTube Duygu Analizi 🎀

🎀 *Türkçe dil seçeneği alt kısımda mevcuttur.* 🎀



![Python](https://img.shields.io/badge/Python-3.10+-FF69B4?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-DA70D6?style=for-the-badge&logo=next.js&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-FFB6C1?style=for-the-badge&logo=openai&logoColor=white)
![YouTube](https://img.shields.io/badge/YouTube-Data_API_v3-C8A2C8?style=for-the-badge&logo=youtube&logoColor=white)

*✨ A 3-agent AI system that analyzes emotions in YouTube comments ✨*
*✨ YouTube yorumlarındaki duyguları yapay zeka ile analiz eden 3 ajanlı sistem ✨*


</div>

---

<div align="center">

## 🎀 How It Works 🎀

</div>

| 🎀 Agent | 📌 Task |
|---------|--------|
| 🔍 **Agent 1 — Fetcher** | Fetches trending videos & comments from YouTube |
| 🧠 **Agent 2 — Brain** | Analyzes sentiments using GPT-4o-mini |
| 📊 **Agent 3 — Visualizer** | Displays results on a beautiful dashboard |

---

<div align="center">

## 🎀 Setup 🎀

</div>

**Requirements**
- 🐍 Python 3.10+
- 💚 Node.js 18+
- 🔑 YouTube Data API v3 key
- 🔑 OpenAI API key

**1. Clone the Repo**
```bash
git clone https://github.com/gulnurkilinc/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
```

**2. Setup Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Open .env and add your API keys
```

**3. Setup Frontend**
```bash
cd frontend
npm install
```

---

<div align="center">

## 🎀 Usage 🎀

</div>

**Step 1 — Fetch Data**
```bash
cd backend
python agents/fetcher.py
```

**Step 2 — Run Analysis**
```bash
python agents/brain.py
```

**Step 3 — Open Dashboard**
```bash
cd frontend
npm run dev
```
> 🌸 Open `http://localhost:3000` in your browser

---

<div align="center">

## 🎀 Analyzed Emotions 🎀

| Emotion | Duygu |
|--------|-------|
| 😠 Anger | Öfke |
| 😊 Joy | Sevinç |
| 🤝 Trust | Güven |
| 😨 Fear | Korku |
| 😲 Surprise | Sürpriz |
| 😢 Sadness | Üzüntü |
| 🤢 Disgust | İğrenme |
| 🌟 Anticipation | Beklenti |

</div>

---

<div align="center">

## 🎀 API Keys 🎀

🔑 **YouTube API →** [console.cloud.google.com](https://console.cloud.google.com)

🔑 **OpenAI API →** [platform.openai.com](https://platform.openai.com)

</div>

---

<div align="center">

## 🎀 TÜRKÇE 🎀
## 🎀 Nasıl Çalışır? 🎀

</div>

| 🎀 Ajan | 📌 Görev |
|--------|---------|
| 🔍 **Ajan 1 — Fetcher** | YouTube'dan trend videolar ve yorumlar çeker |
| 🧠 **Ajan 2 — Brain** | GPT-4o-mini ile duygu analizi yapar |
| 📊 **Ajan 3 — Visualizer** | Sonuçları dashboard'da gösterir |

---

<div align="center">

## 🎀 Kurulum 🎀

</div>

**1. Repoyu İndir**
```bash
git clone https://github.com/gulnurkilinc/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
```

**2. Backend Kur**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env dosyasını aç ve API key'lerini yaz
```

**3. Frontend Kur**
```bash
cd frontend
npm install
```

---

<div align="center">

## 🎀 Kullanım 🎀

</div>

**Adım 1 — Veri Çek**
```bash
cd backend
python agents/fetcher.py
```

**Adım 2 — Analiz Yap**
```bash
python agents/brain.py
```

**Adım 3 — Dashboard'u Aç**
```bash
cd frontend
npm run dev
```
> 🌸 Tarayıcıda `http://localhost:3000` aç

---

<div align="center">



</div>