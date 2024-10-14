################################################################################################################################
'''
# Below code support only one API request at a time. 

from flask import Flask, request, jsonify, Response
from youtube_captioning_system import YouTubeCaptioningSystem

app = Flask(__name__)

# Instantiate the captioning system
captioning_system = YouTubeCaptioningSystem()

@app.route('/generate_captions', methods=['POST'])
async def generate_captions():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    file_format = data.get('format', 'srt')  # Default to 'srt' if no format is provided
    
    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        # Generate the subtitles in the requested format
        output_file = captioning_system.generate_subtitles(youtube_url, file_format)

        # Read the content of the output file
        with open(output_file, 'r') as file:
            file_content = file.read()

        # Return the content in the response with a key
        return jsonify({
            "message": "Captions generated successfully",
            "content": file_content
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True) # https://youtube.com/shorts/X_CuPlfY1y0?si=SmLDdx7YV90QSU51

'''
################################################################################################################################



################################################################################################################################
# Below Code Loads more than 1 instances of model and uses for API requests.
import os
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_captioning_system import YouTubeCaptioningSystem
import torch
from asyncio import Lock

app = Flask(__name__)
CORS(app)

# Number of model instances in the pool
MODEL_POOL_SIZE = 2  # You can adjust this based on your server capacity
captioning_system_pool = []
model_locks = []  # Corresponding locks for each model instance

# Initialize the pool of models and their locks
for _ in range(MODEL_POOL_SIZE):
    system_instance = YouTubeCaptioningSystem()
    captioning_system_pool.append(system_instance)
    model_locks.append(Lock())  # Create a lock for each model instance


async def get_model_from_pool():
    """
    Waits until a model is available, then returns it along with its lock.
    """
    while True:
        for i in range(MODEL_POOL_SIZE):
            if model_locks[i].locked() is False:  # Check if the lock is free
                await model_locks[i].acquire()  # Acquire the lock
                return captioning_system_pool[i], model_locks[i]
        await asyncio.sleep(0.1)  # Sleep briefly to avoid a busy loop


@app.route('/generate_captions', methods=['POST'])
async def generate_captions():
    data = request.get_json()  # Get the JSON input from the request
    youtube_url = data.get('youtube_url')
    file_format = data.get('format', 'srt')  # Default to 'srt' if no format is provided

    if not youtube_url:
        return jsonify({"error": "YouTube URL is required"}), 400

    try:
        # Get a model and its lock from the pool
        system_instance, model_lock = await get_model_from_pool()

        try:
            # Generate the subtitles using the model from the pool
            output_content_file_path = await asyncio.to_thread(system_instance.generate_subtitles, youtube_url, file_format)

            # Read the content of the output file
            with open(output_content_file_path, 'r') as file:
                file_content = file.read()

            # Return the generated subtitle content in the response
            return jsonify({
                "message": "Captions generated successfully",
                "content": file_content,
                "format": file_format
            }), 200

        finally:
            # Release the lock so other requests can use the model
            model_lock.release()

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

# curl -X POST http://127.0.0.1:5000/generate_captions -H "Content-Type: application/json" -d '{"youtube_url": "https://youtube.com/shorts/X_CuPlfY1y0?si=SmLDdx7YV90QSU51", "format": "srt"}'

################################################################################################################################