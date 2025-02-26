
# YouTube Video Captioning System

This project allows users to download a YouTube video’s audio, perform speaker diarization, and generate captions in multiple formats (SRT, JSON, VTT, CSV, TXT). It supports GPU acceleration if available, falling back to CPU if necessary. This system is containerized using Docker, so you can run it on any machine with Docker installed.

## Features

- Download YouTube audio
- Speaker diarization with Pyannote
- Speech recognition using Whisper
- Multiple caption formats (SRT, VTT, JSON, TXT, CSV)
- Model pool mechanism (Strategy 1) & Requests processing in a queue (Strategy 2)
- GPU and CPU support for machine learning models

---


## Prerequisites

### 1. Docker
Ensure Docker is installed on your system:

- **Linux**: Install Docker using your package manager. [Docker Installation Guide](https://docs.docker.com/engine/install/)
- **Windows**: Install Docker Desktop. Ensure you enable **WSL2** and install the necessary **NVIDIA drivers** if you want to use GPU. [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

### 2. NVIDIA Drivers (For GPU Support)
To utilize GPU acceleration:
- **Linux**: Install NVIDIA drivers and `nvidia-docker`. [Instructions](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- **Windows**: Install **NVIDIA WSL2 drivers** from [NVIDIA's website](https://developer.nvidia.com/cuda/wsl).

---

## Installation

### Step 1: Clone the Repository
First, clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/YouTube_Video_Captioning_Backend_System.git
cd YouTube_Video_Captioning_Backend_System
```

### Step 2: Set Up Environment Variables
This project uses **Pyannote** for speaker diarization, which requires an authentication token from Hugging Face. To get your token:
1. Sign up for a Hugging Face account.
2. Obtain your token from [this page](https://huggingface.co/settings/tokens). If you are using your own access token of Hugging Face, please ensure to get the necessary permissions of pyannote. Go to [link](https://huggingface.co/pyannote/speaker-diarization-3.1) for access to pyannote. 

Create a `.env` file in the root directory:

```bash
echo "HUGGINGFACE_AUTH_TOKEN=your_huggingface_token" > .env
```

---

## Use My Pre-build Docker Image

### Step 1: Pull the Docker Image
You need to pull the docker image from my account.

```bash
sudo docker pull sajidhameed63/youtube_captioning_system:lightweight
```

### Step 2: Run the Container in Interactive Mode and Daemon Mode

```bash
sudo docker run -it -d --gpus all --network host youtube_captioning_system:lightweight /bin/bash
sudo docker ps 
sudo docker attach <running-container-id>
```

### Step 3: Go inside the Docker Container, install requirements

```bash
pip3 install -r requirements.txt
```

### Step 4: Run the Flask App

```bash
python3 app.py
```

Now your Flask app is running, you can use it.

---

## Build Your Docker Image

### Step 1: Build the Docker Image
You need to build the Docker image from the provided Dockerfile.

```bash
sudo docker build -t youtube_video_captioning_system:lightweight .
```

### Step 2: Run the Docker Container
**Note:** Before running the flask app, make to install the python requirements.

#### With GPU (if available):
If your system supports GPU, you can run the Docker container with GPU acceleration:

```bash
sudo docker run -it --gpus all --network host youtube_video_captioning_system:lightweight

```


#### Without GPU (CPU only):
If you don't have a GPU or don't want to use one (it will take more time for processing on CPU):

```bash
sudo docker run -it --network host youtube_video_captioning_system:lightweight
```

**Note:** If you want to update your HuggingFace access token, you can run the container in interactive mode and write it manually:
```
sudo docker run -it --gpus all --network host youtube_video_captioning_system:lightweight /bin/bash
sudo docker ps
sudo docker attach <ID_OF_RUNNING_CONTAINER>

```

---

## Running Without Docker (Locally)

If you want to run the project without Docker, follow the steps below:

### Step 1: Set Up a Python Virtual Environment

Ensure you have **Python 3.8+** installed. Set up and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows, use `venv\Scripts\activate`
```

### Step 2: Install Dependencies
Install the required Python packages:

```bash
pip3 install -r requirements.txt
```

### Step 3: Run the Application
Once the dependencies are installed, you can run the Flask API:

```bash
python app.py
```

The application should now be running on `http://127.0.0.1:5000`.

---

## API Usage

To generate captions, send a POST request to `/generate_captions` with a YouTube URL and the desired format (optional):

### Request Format
```json
{
  "youtube_url": "https://youtube.com/shorts/X_CuPlfY1y0?si=SmLDdx7YV90QSU51",
  "format": "srt"  # Optional: 'srt', 'json', 'vtt', 'csv', 'txt' (default is 'srt')
}
```

### Sample cURL Command
```bash
curl -X POST http://127.0.0.1:5000/generate_captions -H "Content-Type: application/json" -d '{"youtube_url": "https://youtube.com/shorts/X_CuPlfY1y0?si=SmLDdx7YV90QSU51", "format": "srt"}'
```

### Response Format
```json
{
  "content": "1\n00:00:00 --> 00:00:15\nSpeaker_A:  Fix your English in 20 seconds. Hmm, I met him three years before. I met him three years ago. I born in 1999. I was born in 1999.\n\n2\n00:00:15 --> 00:00:19\nSpeaker_A:  Hoo! Today morning, I went jogging.\n\n3\n00:00:19 --> 00:00:24\nSpeaker_A:  This morning, I went jogging. Oh, I-\n\n4\n00:00:24 --> 00:00:32\nSpeaker_B:  Visit Thailand twice. I've visited Thailand twice. Which mistake do you make?\n\n5\n00:00:32 --> 00:00:33\nSpeaker_B:  Leave a comment below.\n\n",
  "format": "srt",
  "message": "Captions generated successfully"
}
```

---

## File Structure

Here’s an overview of the key files in this project:

```
YouTube_Video_Captioning_Backend_System/
│
├── app.py                 # Main Flask application
├── youtube_captioning_system.py  # Handles YouTube audio downloading and caption generation
├── audio_processing.py    # Audio extraction and diarization logic
├── transcription.py       # Speech-to-text functionality using Whisper
├── utils.py               # Utility functions like timestamp formatting
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker setup for the project
├── .env                   # Hugging Face token file
└── .gitignore             # The .gitignore file tells Git to ignore certain files or directories so they won’t be tracked or pushed to your repository.
└── README.md              # Project documentation
```

## Model Pooling Mechanism

To efficiently handle multiple requests simultaneously, this system implements a **model pooling mechanism**. Rather than loading a new instance of the model for every incoming request (which would be resource-intensive), the system pre-loads multiple instances of the model into a pool when the server starts.

This pool of models allows for concurrent processing of requests, where each request uses an available model from the pool. If all models are busy, incoming requests wait until a model becomes available, ensuring optimal resource usage and avoiding bottlenecks in performance.

### How It Works:
- The pool is initialized with a configurable number of model instances. In the current implementation, it creates **2 instances** of the model by default.
- Each instance in the pool is protected by an asynchronous lock, ensuring that only one request can use a specific model instance at a time.
- When a request for generating captions is received, the system fetches an available model from the pool. Once the captioning process is complete, the model is returned to the pool, and its lock is released for the next request.
- If no models are available, the request waits until a model becomes free, maintaining an orderly processing flow.

This pooling mechanism significantly reduces the overhead of repeatedly loading models and improves the overall scalability of the system.

### Configuration:
You can adjust the number of model instances in the pool based on your server's capacity by modifying the `MODEL_POOL_SIZE` variable in `app.py`:

```python
MODEL_POOL_SIZE = 2  # Adjust this value based on your system's resources
```

Increasing this value will allow more concurrent requests to be handled, but it will also require more memory and computational resources.


---

## Troubleshooting

### Common Issues

1. **Docker: No GPU Available**  
   If you receive an error about GPUs not being available, ensure that:
   - Your system has an NVIDIA GPU.
   - You have installed the appropriate drivers.
   - You’re using the correct Docker run command with `--gpus all`.

2. **Docker: Permission Denied Error**  
   If Docker gives a permission error, ensure that your user has access to the Docker daemon. If flask API is not reachable after running the docker container, try below command:
   ```bash
   sudo docker run --gpus all --network host youtube_video_captioning_system
   ```


3. **Pyannote Pipeline Errors**  
   If you encounter errors with the Pyannote pipeline, ensure that:
   - You have set up the `.env` file with a valid Hugging Face token.
   - The token has the necessary access to use the `pyannote/speaker-diarization-3.1` model. If you are using your own access token of Hugging Face, please make sure to get the necessary permissions of pyannote. Go to [link](https://huggingface.co/pyannote/speaker-diarization-3.1) for access of pyannote. 

4. **Whisper Model Issues**  
   If Whisper throws errors, make sure you have the necessary dependencies for `ffmpeg` installed, as it is required for audio processing.

---

## Contributing
Contributions are welcome! Feel free to open issues or pull requests for any improvements or bug fixes.
