## Simple Transcriber in Python
### Version 7

It now works with the [Vosk](https://alphacephei.com/vosk/) speech to text library, working fully offline.

I used [UV](https://docs.astral.sh/uv/) to make it portable.

You need to download a *model* from the [Vosk Models website](https://alphacephei.com/vosk/models) and extract it,
I used the `vosk-model-en-us-0.22-lgraph` but you can change the **VOSK_MODEL_PATH** variable in the script.

Now set it up in your terminal:
```
curl -LsSf https://astral.sh/uv/install.sh | sh # Install UV, you could also use pip install uv
uv init -p 3.12 # Initialize in current directory, in this case I specify Python 3.12 but it's optional
uv add pydub tqdm vosk # Install dependencies
```

And run it with:
`uv run audio_to_sbv2.py audio.mp3`

Thank [Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx).

### Version 6

Just use `pip install -r requirements.txt` then run with `python mp3_to_sbv.py audio.mp3`, replacing `audio.mp3` by the path to an `mp3` file and it will generate an `audio.sbv` next to the input file.

Why `mp3` to `sbv`? Because that's what [youtube.com](https://www.youtube.com/) exports when you download subtitles.

What transcriber is used? Google Speech Recognition, learn more [here](https://github.com/Uberi/speech_recognition/blob/master/examples/audio_transcribe.py).

Thanks for the tips, [freecodecamp](https://www.freecodecamp.org/news/python-requirementstxt-explained/).

### Modified to allow a multitude of files as input (it uses [PyDub](https://github.com/jiaaro/pydub))
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
