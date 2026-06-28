import os, requests, random, textwrap, schedule, time
from dotenv import load_dotenv
from trendspyg import download_google_trends_rss
import google.generativeai as genai
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (VideoFileClip, AudioFileClip, TextClip,
                             CompositeVideoClip, concatenate_videoclips)
from instagrapi import Client
from datetime import datetime
import moviepy.video.fx.all as vfx

# ── Load your config ──────────────────────────────────────
load_dotenv()
GEMINI_KEY      = os.getenv("GEMINI_API_KEY")
PEXELS_KEY      = os.getenv("PEXELS_API_KEY")
IG_USER         = os.getenv("INSTAGRAM_USERNAME")
IG_PASS         = os.getenv("INSTAGRAM_PASSWORD")
NICHE           = os.getenv("YOUR_NICHE", "technology")
POST_TIME       = os.getenv("POST_TIME", "10:00")

# ── Setup Gemini AI ───────────────────────────────────────
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# ── Folders ───────────────────────────────────────────────
os.makedirs("videos", exist_ok=True)
os.makedirs("audio",  exist_ok=True)
os.makedirs("output", exist_ok=True)

# ═════════════════════════════════════════════════════════
# STEP A: FIND TODAY'S TRENDING TOPIC
# ═════════════════════════════════════════════════════════
from trendspyg import download_google_trends_rss

def get_trending_topic():
    print("\n📈 [1/6] Finding trending topics...")
    try:
        # Get trending searches using trendspyg (maintained & working)
        env = download_google_trends_rss(geo='US', normalize=True)
        trends = env.get('trends', [])
        
        # Extract topic keywords
        topics = [t['keyword'] for t in trends[:10]]
        
        if not topics:
            raise Exception("No trends found")
        
        # Ask Gemini to pick the best topic for your niche
        prompt = f"""
        These are today's trending Google topics: {topics}
        My Instagram niche is: {NICHE}
        
        Pick the SINGLE best topic from this list that relates to {NICHE}.
        If none relate directly, pick the most viral one and suggest 
        a creative angle connecting it to {NICHE}.
        
        Reply in this exact format:
        TOPIC: [topic name]
        ANGLE: [one sentence about the angle]
        """
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')
        topic = lines[0].replace("TOPIC:", "").strip()
        angle = lines[1].replace("ANGLE:", "").strip() if len(lines) > 1 else "Trending now"
        print(f"   ✅ Topic chosen: {topic}")
        print(f"   ✅ Angle: {angle}")
        return topic, angle

    except Exception as e:
        print(f"   ⚠️ Trends error: {e} — Using fallback topic")
        return f"Top {NICHE} tips 2026", f"Essential {NICHE} advice everyone needs"
# ═════════════════════════════════════════════════════════
# STEP B: WRITE ALL CONTENT WITH AI
# ═════════════════════════════════════════════════════════
def generate_content(topic, angle):
    print("\n✍️  [2/6] Writing content with AI...")
    prompt = f"""
    Create a complete Instagram Reel package about: "{topic}"
    Angle: {angle}
    Niche: {NICHE}
    
    Return EXACTLY in this format (keep the labels):
    
    SCRIPT:
    [Write a 60-second video script. Break it into 5 short punchy sentences.
     Each sentence on a new line. Max 15 words per sentence.
     Start with a shocking hook. End with a call to action.]
    
    CAPTION:
    [Write an engaging Instagram caption. Use emojis. Max 300 characters.
     End with: Follow for daily {NICHE} content!]
    
    HASHTAGS:
    [Write exactly 5 hashtags. Mix popular and niche ones. All on one line.]
    
    KEYWORDS:
    [Write 3 short keywords for finding background video footage. Comma separated.]
    """
    response = model.generate_content(prompt)
    text     = response.text.strip()

    def extract(label, next_label):
        try:
            start = text.index(label + "\n") + len(label) + 1
            end   = text.index(next_label) if next_label in text else len(text)
            return text[start:end].strip()
        except:
            return ""

    script   = extract("SCRIPT:",   "CAPTION:")
    caption  = extract("CAPTION:",  "HASHTAGS:")
    hashtags = extract("HASHTAGS:", "KEYWORDS:")
    keywords = extract("KEYWORDS:", "ZZZZ")      # last item

    print(f"   ✅ Script written ({len(script.split())} words)")
    print(f"   ✅ Caption & {len(hashtags.split())} hashtags ready")
    return script, caption, hashtags, keywords


# ═════════════════════════════════════════════════════════
# STEP C: DOWNLOAD FREE STOCK VIDEOS (Pexels)
# ═════════════════════════════════════════════════════════
def download_stock_videos(keywords, num_clips=4):
    print("\n🎬 [3/6] Downloading free stock videos from Pexels...")
    keyword_list = [k.strip() for k in keywords.split(",")]
    clip_paths   = []
    headers      = {"Authorization": PEXELS_KEY}

    for keyword in keyword_list[:2]:   # Use first 2 keywords
        url    = f"https://api.pexels.com/videos/search?query={keyword}&per_page=5&orientation=portrait"
        resp   = requests.get(url, headers=headers).json()
        videos = resp.get("videos", [])

        for video in videos[:2]:       # Download 2 clips per keyword
            files = video.get("video_files", [])
            # Get the smallest HD file to save time
            hd_files = [f for f in files if f.get("quality") in ["hd", "sd"]]
            if not hd_files:
                continue
            chosen   = sorted(hd_files, key=lambda x: x.get("width", 0))[0]
            vid_url  = chosen["link"]
            filename = f"videos/clip_{len(clip_paths)}.mp4"

            with requests.get(vid_url, stream=True) as r:
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            clip_paths.append(filename)
            print(f"   ✅ Downloaded: {filename}")

            if len(clip_paths) >= num_clips:
                break
        if len(clip_paths) >= num_clips:
            break

    return clip_paths


# ═════════════════════════════════════════════════════════
# STEP D: CREATE VOICEOVER (Free Google TTS)
# ═════════════════════════════════════════════════════════
def create_voiceover(script):
    print("\n🎙️  [4/6] Generating AI voiceover...")
    audio_path = "audio/voiceover.mp3"
    tts        = gTTS(text=script, lang='hi', slow=False)
    tts.save(audio_path)
    print(f"   ✅ Voiceover saved!")
    return audio_path


# ═════════════════════════════════════════════════════════
# STEP E: BUILD THE ANIMATED VIDEO
# ═════════════════════════════════════════════════════════
def build_video(clip_paths, audio_path, script, topic):
    print("\n🎞️  [5/6] Building the animated video...")

    # Instagram Reels dimensions (vertical 9:16)
    W, H         = 1080, 1920
    output_path  = f"output/reel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    # Load voiceover to get total duration
    audio_clip   = AudioFileClip(audio_path)
    total_dur    = audio_clip.duration
    clip_dur     = total_dur / max(len(clip_paths), 1)

    # Process each background video clip
    processed = []
    for path in clip_paths:
        try:
            vc = VideoFileClip(path)
            # Crop to vertical (9:16) — center crop
            vc_w, vc_h = vc.size
            target_w   = int(vc_h * (9/16))
            x_center   = (vc_w - target_w) // 2
            vc         = vc.crop(x1=x_center, y1=0,
                                  x2=x_center + target_w, y2=vc_h)
            vc         = vc.resize((W, H))
            vc         = vc.subclip(0, min(clip_dur, vc.duration))
            # Dim the background slightly
            vc         = vc.fl_image(lambda f: (f * 0.55).astype('uint8'))
            processed.append(vc)
        except Exception as e:
            print(f"   ⚠️ Skipping clip {path}: {e}")

    if not processed:
        # Fallback: solid color background
        from moviepy.editor import ColorClip
        processed = [ColorClip(size=(W, H), color=[10, 10, 40],
                                duration=total_dur)]

    # Concatenate background clips
    bg_video = concatenate_videoclips(processed).subclip(0, total_dur)

    # Create animated text overlays from script sentences
    sentences   = [s.strip() for s in script.split('\n') if s.strip()]
    text_clips  = []
    time_per    = total_dur / max(len(sentences), 1)

    for i, sentence in enumerate(sentences):
        start_t = i * time_per
        wrapped = textwrap.fill(sentence, width=25)

        # Main text
        txt = TextClip(
            wrapped,
            fontsize=65,
            color='white',
            font='Arial-Bold',
            method='caption',
            size=(W - 80, None),
            stroke_color='black',
            stroke_width=3
        ).set_position(('center', H * 0.35)) \
         .set_start(start_t) \
         .set_duration(time_per) \
         .crossfadein(0.3) \
         .crossfadeout(0.3)
        text_clips.append(txt)

    # Title bar at the top
    title_clip = TextClip(
        f"#{topic[:30]}",
        fontsize=45,
        color='yellow',
        font='Arial-Bold',
        method='label'
    ).set_position(('center', 80)) \
     .set_duration(total_dur)

    # Watermark at bottom
    watermark = TextClip(
        f"Follow @{IG_USER}",
        fontsize=38,
        color='white',
        font='Arial',
        method='label'
    ).set_position(('center', H - 120)) \
     .set_duration(total_dur)

    # Compose final video
    final = CompositeVideoClip(
        [bg_video] + text_clips + [title_clip, watermark]
    ).set_audio(audio_clip)

    # Export
    final.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        verbose=False,
        logger=None
    )
    print(f"   ✅ Video created: {output_path}")

    # Cleanup temp clips
    for p in clip_paths:
        try:
            os.remove(p)
        except:
            pass

    return output_path


# ═════════════════════════════════════════════════════════
# STEP F: AUTO-UPLOAD TO INSTAGRAM
# ═════════════════════════════════════════════════════════
def upload_to_instagram(video_path, caption, hashtags):
    print("\n📤 [6/6] Uploading to Instagram...")
    full_caption = f"{caption}\n\n.\n.\n.\n{hashtags}"

    cl = Client()
    cl.delay_range = [2, 5]   # Human-like delays

    try:
        cl.login(IG_USER, IG_PASS)
        print("   ✅ Logged in to Instagram!")
    except Exception as e:
        print(f"   ❌ Login failed: {e}")
        return False

    try:
        media = cl.clip_upload(
            path=video_path,
            caption=full_caption
        )
        print(f"   ✅ REEL POSTED SUCCESSFULLY! 🎉")
        print(f"   📊 Media ID: {media.pk}")
        cl.logout()
        return True
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        cl.logout()
        return False


# ═════════════════════════════════════════════════════════
# 🚀 MASTER FUNCTION — DOES EVERYTHING IN ONE SHOT
# ═════════════════════════════════════════════════════════
def run_full_automation():
    print("\n" + "═"*55)
    print(f"  🤖 INSTAGRAM AI BOT STARTED — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═"*55)

    try:
        # A. Find trending topic
        topic, angle = get_trending_topic()

        # B. Generate all content with AI
        script, caption, hashtags, keywords = generate_content(topic, angle)

        # C. Download stock videos
        clip_paths = download_stock_videos(keywords)

        # D. Create voiceover
        audio_path = create_voiceover(script)

        # E. Build animated video
        video_path = build_video(clip_paths, audio_path, script, topic)

        # F. Upload to Instagram
        success = upload_to_instagram(video_path, caption, hashtags)

        if success:
            print("\n🎉 SUCCESS! Your Instagram Reel was posted automatically!")
        else:
            print("\n⚠️ Video was created but upload failed. Check credentials.")

    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        import traceback; traceback.print_exc()

    print("\n⏰ Next post scheduled at:", POST_TIME, "tomorrow")
    print("═"*55)


# ═════════════════════════════════════════════════════════
# ⏰ SCHEDULER — Runs daily automatically
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════╗
║   🤖 INSTAGRAM AI BOT — ONE-CLICK MODE  ║
║   Niche   : {NICHE:<30}║
║   Posts at: {POST_TIME} daily                      ║
╚══════════════════════════════════════════╝
    """)

    # Run immediately right now
    run_full_automation()

    # Then schedule daily
    schedule.every().day.at(POST_TIME).do(run_full_automation)
    print(f"\n✅ Bot is now running in the background...")
    print(f"📅 Will post every day at {POST_TIME} automatically.")
    print("🔴 Keep this terminal open (or host it — see below)\n")

    while True:
        schedule.run_pending()
        time.sleep(60)
