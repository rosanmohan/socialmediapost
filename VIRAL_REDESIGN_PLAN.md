# 🚀 VIRAL REDESIGN IMPLEMENTATION PLAN

We are shifting from a "Top 5 Bulletin" to a **"Single Viral Story"** format to maximize views.

## 🛠️ Phase 1: The Core Framework
- [x] Create `pipeline_viral.py` (The new logic for single-story reels).
- [x] Implement `hook_generator()` using LLM to create scroll-stopping hooks.
- [x] Implement `script_summarizer()` to turn news articles into 30-40 word "stories".

## 🛠️ Phase 2: Audio & Voiceover
- [x] Integrate **Edge-TTS** (Free, high-quality AI voice) or ElevenLabs.
- [x] Sync captions with the voiceover timing.

## 🛠️ Phase 3: Visual Pacing
- [x] Implement "Pattern Breaks" (Automatic zoom-in/pan every 3 seconds).
- [x] Add "Story Captions" (One sentence at a time, progressive reveal).
- [x] Color Coding (Red for Breaking, Blue for Tech, etc.).

## 🛠️ Phase 4: Platform Intelligence
- [x] `platform_caption_mapper()`: Unique titles/captions for YT vs IG.

---

## 📈 Current Task: STEP 1 (The Single Story Logic)
We will create a new pipeline that picks **one** trending story and creates a deep-dive 15-second reel with a killer hook.
