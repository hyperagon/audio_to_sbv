# pip install pydub tqdm vosk
# Requires a model from https://alphacephei.com/vosk/models
# Version 7

import sys
import os
import json
import wave
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from tqdm import tqdm
import vosk

# CONFIGURATION
# Ensure you have downloaded a model and extracted it here
# Download from: https://alphacephei.com/vosk/models
VOSK_MODEL_PATH = "vosk-model-en-us-0.22-lgraph"

def transcribe_audio_vosk(audio_segment_path, vosk_model):
    """
    Transcribe audio segment to text using Vosk.
    """
    if not vosk_model:
        raise ValueError("Vosk model is not loaded.")

    wf = wave.open(audio_segment_path, "rb")
    
    # Check if audio format is compatible with Vosk (PCM 16-bit mono)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise ValueError("Audio must be WAV format mono PCM.")

    rec = vosk.KaldiRecognizer(vosk_model, wf.getframerate())
    result_text = ""
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "
    
    # Process the final buffer
    res = json.loads(rec.FinalResult())
    result_text += res.get("text", "")
    
    wf.close()
    
    return result_text.strip()

def ms_to_sbv_time(ms):
    """Convert milliseconds to SBV time format (H:MM:SS.SSS)."""
    seconds = ms / 1000.0
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)

    # SBV format requires H:MM:SS.SSS (single digit hour is allowed/standard)
    return f"{hours}:{minutes:02}:{int(seconds):02}.{milliseconds:03}"

def audio_to_sbv(audio_path):
    """
    Convert an audio file (WAV or MP3) to SBV format.
    """
    # 1. Load Audio
    try:
        print(f"Loading audio: {audio_path}")
        file_ext = os.path.splitext(audio_path)[1].lower()
        # Handle format string for pydub (remove dot)
        audio = AudioSegment.from_file(audio_path, format=file_ext[1:])
    except Exception as e:
        print(f"Error loading audio file {audio_path}: {e}")
        sys.exit(1)

    # 2. Load Vosk Model
    if not os.path.exists(VOSK_MODEL_PATH):
        print(f"Error: Vosk model directory '{VOSK_MODEL_PATH}' not found.")
        print(f"Please download a model and extract it to the current directory.")
        sys.exit(1)

    try:
        print(f"Loading Vosk model from '{VOSK_MODEL_PATH}'...")
        vosk_model = vosk.Model(VOSK_MODEL_PATH)
    except Exception as e:
        print(f"Failed to load Vosk model: {e}")
        sys.exit(1)

    sbv_path = os.path.splitext(audio_path)[0] + '.sbv'

    # 3. Smart Silence Detection
    # Calculate dynamic threshold based on the file's actual average loudness
    # If the file is quiet, we lower the threshold.
    avg_loudness = audio.dBFS
    # Set silence threshold to be 10dB below average loudness, or -50, whichever is lower (more permissive)
    dynamic_thresh = min(-50, avg_loudness - 10)
    
    print(f"Audio Average Loudness: {avg_loudness:.2f} dBFS")
    print(f"Using Silence Threshold: {dynamic_thresh:.2f} dBFS")

    print('Detecting non-silent segments...')
    nonsilent_ranges = detect_nonsilent(
        audio, 
        min_silence_len=1000,  # 1 second of silence to split
        silence_thresh=dynamic_thresh
    )
    
    print(f"Detected {len(nonsilent_ranges)} non-silent segments.")

    # FIX: If no segments found, process the whole file as one segment
    if not nonsilent_ranges:
        print("Warning: No distinct speech segments detected. Processing entire file as one segment.")
        nonsilent_ranges = [(0, len(audio))]
        
    # 4. Transcribe Segments
    print(f"Writing to {sbv_path}...")
    
    # We open the file here so it is created even if the loop has issues later
    with open(sbv_path, 'w', encoding='utf-8') as sbv_file:
        for start, end in tqdm(nonsilent_ranges, desc="Processing segments", unit="segment"):
            # Format time
            start_time_formatted = ms_to_sbv_time(start)
            end_time_formatted = ms_to_sbv_time(end)

            sbv_file.write(f"{start_time_formatted},{end_time_formatted}\n")

            wav_segment = 'temp_segment.wav'
            audio_segment = audio[start:end]
            
            # Vosk requires specific audio settings: 16kHz Sample Rate, Mono, PCM 16-bit
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
            audio_segment.export(wav_segment, format='wav')
            
            try:
                transcription = transcribe_audio_vosk(wav_segment, vosk_model)
                if not transcription:
                    transcription = "[No Speech Detected]"
                sbv_file.write(transcription + "\n\n")
            except Exception as e:
                sbv_file.write(f"Transcription error: {str(e)}\n\n")
            finally:
                if os.path.exists(wav_segment):
                    os.remove(wav_segment)

    print(f"\nDone. Output saved to: {sbv_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audio_to_sbv_fixed.py <input_audio.(mp3|wav)>")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    audio_to_sbv(audio_file_path)
