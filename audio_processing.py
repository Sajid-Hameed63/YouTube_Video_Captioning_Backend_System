import os
import torch
import torchaudio
from pyannote.audio import Pipeline
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from dotenv import load_dotenv


class AudioProcessor:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Get Hugging Face token from environment variable
        hugging_face_token = os.getenv("HUGGINGFACE_AUTH_TOKEN")
        if hugging_face_token is None:
            raise ValueError("Hugging Face token is not set in the .env file.")

        # Check if GPU is available and set the device accordingly
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Instantiate the pyannote pipeline for speaker diarization
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hugging_face_token  # Use the token from the environment
        )
        self.pipeline.to(self.device)

        # Create directories for RTTM and temporary segments
        os.makedirs("RTTM_Files", exist_ok=True)
        os.makedirs("temp_segments", exist_ok=True)



    def extract_audio(self, input_path):
        """Extract audio from video or convert audio file to WAV format."""
        if input_path.endswith(('.mp4', '.mkv', '.avi')):  # Check if the file is a video
            video_clip = VideoFileClip(input_path)
            audio_path = "temp_audio.wav"  # Save audio in WAV format
            audio_clip = video_clip.audio
            
            # Write the audio to a separate WAV file
            audio_clip.write_audiofile(audio_path, codec='pcm_s16le')
            
            # Close the video and audio clips
            audio_clip.close()
            video_clip.close()

            print("Audio extraction successful!")
            return audio_path
        
        elif not input_path.endswith('.wav'):  # Convert to WAV if not already
            audio_path = "temp_audio.wav"
            audio = AudioSegment.from_file(input_path)
            audio.export(audio_path, format="wav")
            return audio_path
        
        return input_path  # If it's already a .wav file


    def generate_rttm(self, audio_path, save_rttm=True):
        # Load the audio file into memory
        waveform, sample_rate = torchaudio.load(audio_path)
        waveform = waveform.to(self.device)

        # Run the pipeline on the pre-loaded waveform
        diarization = self.pipeline({"waveform": waveform, "sample_rate": sample_rate}, min_speakers=2, max_speakers=7)

        audio_name_without_ext = os.path.splitext(os.path.basename(audio_path))[0]

        if save_rttm:
            # Dump the diarization output to disk using RTTM format in the "RTTM_Files" directory
            rttm_file = os.path.join("RTTM_Files", f"{audio_name_without_ext}.rttm")
            with open(rttm_file, "w") as rttm:
                diarization.write_rttm(rttm)
            print(f"Diarization completed and saved to '{rttm_file}'.")
            return rttm_file
        else:
            print("Diarization completed but not saved to a file.")
            return diarization  # Return the diarization object directly
