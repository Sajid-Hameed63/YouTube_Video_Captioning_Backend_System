import os
import yt_dlp
import datetime
from audio_processing import AudioProcessor
from transcription import Transcriber
import utils
import json
import csv

class YouTubeCaptioningSystem:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.transcriber = Transcriber()

    def download_audio(self, youtube_url):
        # Create a directory for YouTube downloads if it doesn't exist
        download_dir = "YouTube_Downloads"
        os.makedirs(download_dir, exist_ok=True)

        # Generate a unique timestamp for the filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join(download_dir, f"{timestamp}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': False,
            'noplaylist': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"[{datetime.datetime.now()}] Downloading video from {youtube_url}...")
                ydl.download([youtube_url])
            print(f"[{datetime.datetime.now()}] Audio downloaded successfully to {audio_path}")
            return audio_path + ".wav"
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error downloading video: {str(e)}")
            raise

    def generate_subtitles(self, youtube_url, file_format):
        try:
            audio_path = self.download_audio(youtube_url)
            print("[INFO] Extracting audio from the video...")

            # Diarization and transcription
            print("[INFO] Performing speaker diarization...")
            rttm_output = self.audio_processor.generate_rttm(audio_path, save_rttm=True)

            print("[INFO] Performing speech recognition...")
            results = self.transcriber.perform_speech_recognition(audio_path, rttm_output)

            # Save in the requested format
            output_file = os.path.splitext(audio_path)[0]
            if file_format == "srt":
                return self.save_as_srt(results, f"{output_file}.srt")
            elif file_format == "json":
                return self.save_as_json(results, f"{output_file}.json")
            elif file_format == "vtt":
                return self.save_as_vtt(results, f"{output_file}.vtt")
            elif file_format == "csv":
                return self.save_as_csv(results, f"{output_file}.csv")
            elif file_format == "txt":
                return self.save_as_txt(results, f"{output_file}.txt")
            else:
                raise ValueError(f"[ERROR] Unsupported format: {file_format}")

        except Exception as e:
            print(f"[ERROR] Error processing video: {str(e)}")
            raise

    def save_as_srt(self, results, output_file):
        with open(output_file, 'w') as srt_file:
            for i, result in enumerate(results):
                srt_file.write(f"{i + 1}\n")
                srt_file.write(f"{result['starting_timestamp']} --> {result['ending_timestamp']}\n")
                srt_file.write(f"{result['speaker_id']}: {result['transcription']}\n\n")
        print(f"[INFO] Subtitles saved in SRT format to {output_file}")
        return output_file

    def save_as_json(self, results, output_file):
        with open(output_file, 'w') as json_file:
            json.dump(results, json_file, indent=4)
        print(f"[INFO] Subtitles saved in JSON format to {output_file}")
        return output_file

    def save_as_vtt(self, results, output_file):
        with open(output_file, 'w') as vtt_file:
            vtt_file.write("WEBVTT\n\n")
            for result in results:
                vtt_file.write(f"{result['starting_timestamp']} --> {result['ending_timestamp']}\n")
                vtt_file.write(f"{result['speaker_id']}: {result['transcription']}\n\n")
        print(f"[INFO] Subtitles saved in WebVTT format to {output_file}")
        return output_file

    def save_as_csv(self, results, output_file):
        with open(output_file, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["starting_timestamp", "ending_timestamp", "speaker_id", "transcription"])
            writer.writeheader()
            writer.writerows(results)
        print(f"[INFO] Subtitles saved in CSV format to {output_file}")
        return output_file

    def save_as_txt(self, results, output_file):
        with open(output_file, 'w') as txt_file:
            for result in results:
                txt_file.write(f"{result['starting_timestamp']} - {result['ending_timestamp']}: ")
                txt_file.write(f"{result['speaker_id']}: {result['transcription']}\n")
        print(f"[INFO] Subtitles saved in TXT format to {output_file}")
        return output_file
