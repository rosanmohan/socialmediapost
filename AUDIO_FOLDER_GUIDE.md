# Audio Folder Guide

## How to Use Your Own Audio Files

The system now works exactly like background videos - you can put your audio files in a folder and it will randomly pick one each time!

## Setup Steps

### 1. Create Audio Folder
The folder is automatically created at:
```
assets/audio/
```

### 2. Add Your Audio Files
Put 20-25 royalty-free audio files in the `assets/audio/` folder.

**Supported formats:**
- `.mp3` (recommended)
- `.wav`
- `.m4a`
- `.aac`
- `.ogg`
- `.flac`

**Example:**
```
assets/
  ├── audio/
  │   ├── music1.mp3
  │   ├── music2.mp3
  │   ├── music3.mp3
  │   └── ... (20-25 files)
  ├── backgrounds/
  └── fonts/
```

### 3. How It Works

1. **Random Selection**: System randomly picks one audio file from the folder
2. **No Immediate Repeats**: Tracks last used file to avoid using the same audio twice in a row
3. **Auto-Looping**: If audio is shorter than 20 seconds, it automatically loops
4. **Auto-Trimming**: If audio is longer than 20 seconds, it trims to exactly 20 seconds
5. **Fallback**: If no audio files found, generates music programmatically

## Important Notes

⚠️ **Copyright Safety**: Only use royalty-free music files that you have the right to use!

✅ **Recommended Sources for Royalty-Free Music:**
- YouTube Audio Library (free, no copyright)
- Pixabay Music (free, no attribution needed)
- Free Music Archive (free, check licenses)
- Incompetech (free, attribution required)
- Bensound (free with attribution)

## Example Workflow

1. Download 20-25 royalty-free music tracks
2. Save them in `assets/audio/` folder
3. Run `python main_1.py`
4. System randomly picks one audio file
5. Each video gets different audio!

## Troubleshooting

**No audio files found?**
- Check that files are in `assets/audio/` folder
- Check file extensions (.mp3, .wav, etc.)
- System will fall back to generated music

**Same audio repeating?**
- System tracks last used file
- If you have 20+ files, repeats are very unlikely
- System resets after all files are used

**Audio too short/long?**
- System automatically handles this
- Short audio = loops to 20 seconds
- Long audio = trims to 20 seconds


