# Elevenlabs + WhisperX autosplicing via pydub

main.py contains a function that, given two strings (one being the actual "spoken" text and one being the text used to give it emotion), does the following:
- Generates audio.mp3 containing the full text via elevenlabslib.
- Uses whisperX to obtain word-level timestamps.
- Identifies the start and end of the spoken text.
- Uses pydub to create cut_audio.mp3, containing only the audio for the spoken text.

To try it out (I recommend doing this in a venv):
1. Do `pip install -r pinnedrequirements.txt --no-deps`
2. Edit api_key in main.py to contain your API key
3. Run it


There is a dependency conflict going on due to `pyannote-audio` requiring an older version of soundfile than the minimum for mp3 support (which `elevenlabslib` requires) but it works fine if you just force it, hence the requirements file with pinned versions.