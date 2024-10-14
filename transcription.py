from pydub import AudioSegment
import whisper
from utils import format_timestamp
import os

class Transcriber:
    def __init__(self):
        # Load Whisper ASR model
        self.model = whisper.load_model("base")  # You can choose a different model size, go to Whisper ASR github for more detail.

    def perform_speech_recognition(self, audio_path, rttm_file):
        audio = AudioSegment.from_wav(audio_path)
        results = []
        speaker_map = {}  # To map speaker IDs

        audio_name_without_ext = os.path.splitext(os.path.basename(audio_path))[0]

        with open(rttm_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts[0] == "SPEAKER":
                    speaker_id = parts[7]
                    
                    if speaker_id not in speaker_map:
                        # Map the speaker ID to a letter starting from A
                        speaker_index = len(speaker_map)
                        speaker_map[speaker_id] = f"Speaker_{chr(65 + speaker_index)}"  # 65 is ASCII for 'A'

                    mapped_speaker_id = speaker_map[speaker_id]
                    start_time = float(parts[3])
                    duration = float(parts[4])
                    end_time = start_time + duration
                    
                    # Extract the segment for this speaker
                    start_ms = int(start_time * 1000)
                    end_ms = int(end_time * 1000)
                    segment = audio[start_ms:end_ms]

                    # Save segment to temporary file for transcription in the "temp_segments" directory
                    segment_path = os.path.join("temp_segments", f"{audio_name_without_ext}_temp_segment.wav")
                    segment.export(segment_path, format="wav")

                    print("check")
                    # Perform speech recognition using Whisper
                    transcription = self.model.transcribe(segment_path)['text']
                    
                    # Store results
                    results.append({
                        "starting_timestamp": format_timestamp(start_time),
                        "ending_timestamp": format_timestamp(end_time),
                        "transcription": transcription,
                        "speaker_id": mapped_speaker_id  # Use the mapped speaker ID
                    })

        return results
