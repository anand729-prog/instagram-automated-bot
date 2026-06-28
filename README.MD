# AI Instagram Reel Automation Bot

An end-to-end AI-powered Instagram automation bot that creates and publishes Instagram Reels automatically.

The bot performs the complete workflow:

* Finds trending Google topics
* Generates an engaging Reel script using Gemini AI
* Downloads royalty-free stock videos from Pexels
* Creates AI voiceovers
* Builds a vertical Instagram Reel with subtitles
* Uploads the Reel directly to Instagram
* Runs automatically every day at a scheduled time

---

# Features

* Automatic Google Trends analysis
* AI-generated scripts, captions, hashtags, and keywords
* Free stock video downloading via Pexels API
* AI voice generation using Google Text-to-Speech
* Automatic video editing with MoviePy
* Animated captions
* Instagram Reels auto-upload
* Daily scheduling
* Fully customizable niche

---

# Project Structure

```
project/
│
├── videos/              # Downloaded stock videos
├── audio/               # Generated voiceovers
├── output/              # Final Instagram Reels
│
├── .env                 # Environment variables
├── main.py              # Main application
└── README.md
```

---

## ⚙️ Technologies Used

* Python
* Google Gemini API
* Pexels API
* Google Trends RSS
* MoviePy
* gTTS
* Instagrapi
* Pillow
* python-dotenv
* Schedule

---

#Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/instagram-ai-bot.git

cd instagram-ai-bot
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_gemini_api_key

PEXELS_API_KEY=your_pexels_api_key

INSTAGRAM_USERNAME=your_username

INSTAGRAM_PASSWORD=your_password

YOUR_NICHE=technology

POST_TIME=10:00
```

Example niches:

* Technology
* Fitness
* AI
* Finance
* Motivation
* Education
* Gaming

---

# Usage

Run the bot:

```bash
python main.py
```

The bot will:

1. Find today's trending topic
2. Generate AI content
3. Download stock videos
4. Create a voiceover
5. Build a Reel
6. Upload it to Instagram
7. Schedule the next daily post

---

# Workflow

```
Google Trends
       │
       ▼
Gemini AI
(Script + Caption + Hashtags)
       │
       ▼
Pexels API
(Download Videos)
       │
       ▼
Google TTS
(Voiceover)
       │
       ▼
MoviePy
(Video Creation)
       │
       ▼
Instagram Upload
       │
       ▼
Daily Scheduler
```

---

# Dependencies

```
python-dotenv
requests
schedule
trendspyg
google-generativeai
gTTS
Pillow
moviepy
instagrapi
```

Install all at once:

```bash
pip install python-dotenv requests schedule trendspyg google-generativeai gTTS Pillow moviepy instagrapi
```

---

# Example Output

* AI-generated Instagram Reel
* AI-generated caption
* Relevant hashtags
* AI voice narration
* Auto-uploaded Reel on Instagram

---

# Customization

You can customize:

* Posting time
* Instagram niche
* Video duration
* Caption style
* Voice language
* Font size
* Subtitle animation
* Watermark
* Reel design

---

# Notes

* Use a valid Instagram account.
* Ensure your API keys are active.
* Keep your `.env` file private.
* Do not commit credentials to GitHub.

---

# License

This project is licensed under the MIT License.

---

##Author

Developed using Python, Gemini AI, MoviePy, Pexels API, and Instagram Automation tools.
