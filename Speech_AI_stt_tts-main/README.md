# Speech_AI_stt_tts
A Python project with two features:

- **Text-to-Speech**: converts text to an MP3 using gTTS (English, Hindi, Telugu, Tamil)
- **Speech-to-Text**: transcribes microphone recordings or audio files using
  OpenAI Whisper (`openai/whisper-base`) through Hugging Face Transformers

## Project structure
```
speech_ai/
├── main.py           # menu-based app
├── tts.py            # text to speech
├── stt.py            # speech to text
├── requirements.txt
└── README.md
```

## Installation
```
pip install -r requirements.txt
```

## Usage
```
python main.py
```
Generated audio and transcripts are saved in the `output/` folder.

## Notes
- Text-to-Speech needs an internet connection (gTTS).
- Speech-to-Text runs locally; the Whisper model downloads on first use.
- Audio files should be WAV, FLAC or OGG.

## Tech Stack
Python, PyTorch, Hugging Face Transformers, gTTS, sounddevice, soundfile
