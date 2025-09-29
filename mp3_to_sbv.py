# pip install SpeechRecognition pydub tqdm
# Version 6

import sys
import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import speech_recognition as sr
from datetime import timedelta
from tqdm import tqdm

def transcribe_audio(audio_segment):
    """Transcribe audio segment to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_segment) as source:
        audio = recognizer.record(source)  # Read the entire audio file
    return recognizer.recognize_google(audio)

def ms_to_sbv_time(ms):
    """Convert milliseconds to SBV time format (HH:MM:SS.SSS)."""
    seconds = ms / 1000.0
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)

    return f"{hours}:{minutes:02}:{int(seconds):02}.{milliseconds:03}"

def audio_to_sbv(audio_path, silence_thresh=-50, min_silence_len=1000):
    """
    Convert an audio file (WAV or MP3) to SBV format, breaking the audio into segments based on non-silent portions.

    Parameters:
    - audio_path: Path to the input audio file (WAV or MP3).
    - silence_thresh: Silence threshold in dB. Default is -50 dB.
    - min_silence_len: Minimum length of silence in milliseconds to be considered silence. Default is 1000 ms.
    """
    # Load the audio file
    try:
        # https://github.com/jiaaro/pydub
        # Determine file format and load accordingly
        file_ext = os.path.splitext(audio_path)[1].lower()
        format_handlers = {
            '.mp3': lambda path: AudioSegment.from_mp3(path),
            '.wav': lambda path: AudioSegment.from_wav(path),
            '.ogg': lambda path: AudioSegment.from_ogg(path),
            '.flac': lambda path: AudioSegment.from_file(path, format='flac'),
            '.aac': lambda path: AudioSegment.from_file(path, format='aac'),
            '.m4a': lambda path: AudioSegment.from_file(path, format='m4a'),
            '.wma': lambda path: AudioSegment.from_file(path, format='wma'),
            '.aiff': lambda path: AudioSegment.from_file(path, format='aiff'),
            '.au': lambda path: AudioSegment.from_file(path, format='au'),
            '.raw': lambda path: AudioSegment.from_file(path, format='raw'),
            '.3gp': lambda path: AudioSegment.from_file(path, format='3gp'),
            '.webm': lambda path: AudioSegment.from_file(path, format='webm'),
        }

        if file_ext in format_handlers:
            audio = format_handlers[file_ext](audio_path)
        else:
            raise ValueError(f"Unsupported audio format: {file_ext}")
    except Exception as e:
        print(f"Error loading audio file {audio_path}: {e}")
        sys.exit(1)

    # Determine the SBV file path (same location as audio but with SBV extension)
    sbv_path = os.path.splitext(audio_path)[0] + '.sbv'

    print('Detect non-silent segments...')
    # Detect non-silent segments
    nonsilent_ranges = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    # Debugging: Print the number of segments detected
    print(f"Detected {len(nonsilent_ranges)} non-silent segments.")

    # If no non-silent segments are detected, treat the entire audio as a single segment
    if not nonsilent_ranges:
        nonsilent_ranges = [(0, len(audio))]
        
    with open(sbv_path, 'w') as sbv_file:
        for start,end in tqdm(nonsilent_ranges, desc="Processing segments", unit="segment", file=sys.stdout):
            # Convert milliseconds to SBV time format
            start_time_formatted = ms_to_sbv_time(start)
            end_time_formatted = ms_to_sbv_time(end)

            # Write the segment timing to the SBV file
            sbv_file.write(f"{start_time_formatted},{end_time_formatted}\n")

            # Transcribe the audio segment
            wav_segment = 'temp_segment.wav'
            audio_segment = audio[start:end]
            audio_segment.export(wav_segment, format='wav')
            try:
                transcription = transcribe_audio(wav_segment)
                sbv_file.write(transcription + "\n\n")  # Write the transcription text
            except Exception as e:
                sbv_file.write("Transcription error: " + str(e) + "\n\n")
            finally:
                os.remove(wav_segment)  # Clean up temporary WAV segment

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audio_to_sbv.py <input_audio.(mp3|wav)>")
        sys.exit(1)

    audio_file_path = sys.argv[1]
    print(f'Input: {audio_file_path}')
    audio_to_sbv(audio_file_path)
    print(f"Output: {os.path.splitext(audio_file_path)[0] + '.sbv'}")
