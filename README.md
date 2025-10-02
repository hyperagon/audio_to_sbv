## Simple Transcriber in Python
### Version 5

Just use `pip install -r requirements.txt` then run with `python mp3_to_sbv.py audio.mp3`, replacing `audio.mp3` by the path to an `mp3` file and it will generate an `audio.sbv` next to the input file.

Why `mp3` to `sbv`? Because that's what [youtube.com](https://www.youtube.com/) exports when you download subtitles.

What transcriber is used? Google Speech Recognition, learn more [here](https://github.com/Uberi/speech_recognition/blob/master/examples/audio_transcribe.py).

Initially vibe-coded with **Qwen**.

Thanks for the tips, [freecodecamp](https://www.freecodecamp.org/news/python-requirementstxt-explained/).

Modified to allow a multitude of files as input ([PyDub](https://github.com/jiaaro/pydub)):
- .mp3
- .wav
- .ogg
- .flac
- .aac
- .m4a
- .wma
- .aiff
- .au
- .raw
- .3gp
- .webm
