# ---------------- Import Required Libraries  ---------------------

import json
from flask import Flask, request, send_file, url_for
from threading import Lock
import util
import chat_util
import os
import requests
import time
import sys
from flask import render_template

# import the package wav2lip_inference/wav2lip.py
library_path = util.ROOT_DIR + "/code/wav2lip_inference"
print(library_path)
sys.path.insert(1, library_path)
from Wav2Lip import Processor

# ---------------- Load API Keys From the .env File  ---------------------
from dotenv import load_dotenv

load_dotenv(util.ROOT_DIR + "/.env")

# ---------------- Initialize application  ---------------------

util.initialize()
util.start_log_task("Initializing Flask app...")
app = Flask(__name__)
util.end_log_task()

patient_agent = chat_util.generate_blank_patient()
# create mr al farsi/green as global variable

CHUNK_SIZE = 1024
BASE_URL = 'http://localhost:5000'

@app.route('/', methods=['POST'])
def index():
    return "Homepage!"


from subprocess import run, PIPE

from flask import logging, Flask, render_template, request

import wave, keyboard, faster_whisper, torch.cuda

model, answer, history = faster_whisper.WhisperModel(model_size_or_path="tiny.en",
                                                     device='cuda' if torch.cuda.is_available() else 'cpu'), "", []

# import base64
# import pyaudio

from threading import Thread


@app.route('/client_test', methods=['GET'])
def client_test():
    return render_template('client.html')


@app.route('/receive_audio', methods=['POST'])
def receive_audio():
    # dirname = "temp"
    # filename = "temp.webm" #request.files['audio_file'].filename
    save_path = "temp/temp.webm"
    wav_save_path = 'temp/temp.wav'
    request.files['audio_file'].save(save_path)

    Thread(target=transcribe_text).start()

    return "Received audio file"


@app.route('/transcribe_text', methods=['POST'])
def transcribe_text():

    save_path = "temp/temp.webm"
    wav_save_path = "temp/temp.wav"
    print("converting to wave audio")

    # convert wepm to wav
    run(['ffmpeg', '-y', save_path, wav_save_path], stdout=PIPE, stderr=PIPE)

    print('preparing for transcription')

    # audio, frames = pyaudio.PyAudio(), []

    # # Transcribe recording using whisper
    # with wave.open(wav_save_path, 'wb') as wf:
    #     wf.setparams((1, audio.get_sample_size(pyaudio.paInt16), 16000, 0, 'NONE', 'NONE'))
    #     wf.writeframes(b''.join(frames))

    print('transcribing')
    user_text = " ".join(seg.text for seg in model.transcribe(wav_save_path, language="en")[0])
    print(f'>>>{user_text}\n<<< ', end="", flush=True)
    return user_text

# ---------------- Generation endpoints  ---------------------

@app.route('/generate_patient', methods=['POST'])
def request_patient_generation():
    # to do: sessions / authorization to have multiple active agents
    global patient_agent

    patient_agent = chat_util.generate_patient(language_model_name='gpt-4-turbo-preview')
    return f"Generated patient agent ({patient_agent.name}) using {patient_agent.model.model_name} and the following system message: {patient_agent.system_message}"


@app.route('/generate_patient_text', methods=['POST'])
def generate_patient_text(message_from_user=None):
    # message_from_user = request.args.get('message_from_user', type=str)
    if not message_from_user:
        message_from_user = request.json['message_from_user']
    util.rprint(f"[bold]Conversation started [/bold] \n ─────────────────────────────────────────── ")
    util.rprint(f"  [blue][bold]▶ CLINICIAN [/bold] {message_from_user} [/blue]\n")
    patient_agent.receive(name="Clinician", message=message_from_user)
    message_from_patient = patient_agent.send()
    util.rprint(f"  [cyan3][bold]▶ PATIENT [/bold] {message_from_patient} [/cyan3]\n")
    return json.dumps({'message_from_patient': message_from_patient})


@app.route('/generate_patient_audio', methods=['POST'])
def generate_patient_audio(message_from_user=None):
    request_id = util.generate_hash()

    if not message_from_user:
        message_from_user = request.json['message_from_user']
    patient_text_response = json.loads(generate_patient_text(message_from_user))['message_from_patient']
    url = "https://api.elevenlabs.io/v1/text-to-speech/jwnLlmJUpWazVNZOyzKE"
    querystring = {"optimize_streaming_latency": "4", "output_format": "mp3_44100_32"}
    payload = {"text": patient_text_response}
    headers = {
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    }
    util.start_log_task("Sending audio_files request to Eleven Labs...")
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    util.end_log_task()

    local_filename = request_id + '.mp3'
    util.log_task(f"Received {local_filename} from Eleven Labs.")
    filename = util.ROOT_DIR + '/audio_files/' + local_filename

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    if response.status_code == 200:
        return json.dumps({'status': 'success',
                           'request_id': request_id,
                           'audio_url': BASE_URL + '/get_audio?filename=' + local_filename,
                           'audio_path': filename,
                           'message_from_patient': patient_text_response})


@app.route('/generate_remote_video', methods=['POST'])
def generate_remote_video(audio_path=None):
    if not audio_path:
        audio_path = request.json['audio_path']

    url = "https://api.synclabs.so/lipsync"
    querystring = {"optimize_streaming_latency": "4", "output_format": "mp3_44100_32"}
    payload = {
        "audioUrl": "https://cdn.syntheticpatients.org/audio/output_2024-04-30-T-01-47-46___72537b5cb2024fc3.mp3",
        "videoUrl": "https://cdn.syntheticpatients.org/video/alfarsi_speaking_shortly_5s_720p.mp4",
        "synergize": True,
        "maxCredits": None,
        "webhookUrl": None,
        "model": "wav2lip++"
    }
    headers = {
        "accept": "application/json",
        "x-api-key": os.environ["SYNCLABS_API_KEY"],
        "Content-Type": "application/json"
    }
    util.start_log_task("Sending video request to Sync Labs...")
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    util.end_log_task()

    print(response.text)

    video_sync_labs_id = json.loads(response.text)["id"]
    video_generating = True
    video_url = None
    while video_generating:
        url = f"https://api.synclabs.so/lipsync/{video_sync_labs_id}"
        headers = {
            "accept": "application/json",
            "x-api-key": os.environ["SYNCLABS_API_KEY"]
        }
        response = requests.request("GET", url, headers=headers)
        status = json.loads(response.text)["status"]
        if status == "COMPLETED":
            video_url = json.loads(response.text)["videoUrl"]
            util.lp("Video generation completed. Available at: " + video_url)
            video_generating = False
        else:
            util.lp("Video generation in progress. Status: " + status)
            time.sleep(5)
    return video_url


@app.route('/generate_local_video', methods=['POST'])
def generate_local_video(request_id=None):
    if not request_id:
        request_id = request.json['request_id']

    audio_path = util.ROOT_DIR + '/audio_files/' + request_id + '.mp3'
    video_path = util.ROOT_DIR + '/video/trimmed.mp4'
    output_path = util.ROOT_DIR + '/video_output/' + request_id + '.mp4'
    output_url = BASE_URL + '/get_video?filename=' + request_id + '.mp4'

    util.log_mini_task("audio_files path: " + audio_path)
    util.log_mini_task("video path: " + video_path)

    processor.run(video_path, audio_path, output_path, resize_factor=1)

    return json.dumps({'status': 'success',
                       'request_id': request_id,
                       'video_url': output_url,
                       'video_path': output_path})


# ---------------------- Get endpoints  -------------------------

@app.route('/get_audio', methods=['GET'])
def get_audio_file(filename=None):
    if filename is None:
        filename = request.args.get('filename')
    return send_file(util.ROOT_DIR + '/audio_files/' + filename, as_attachment=True)


@app.route('/get_video', methods=['GET'])
def get_video_file(filename=None):
    if filename is None:
        filename = request.args.get('filename')
    return send_file(util.ROOT_DIR + '/video_output/' + filename, as_attachment=True)


# ---------------- End-to-end endpoints ------------------------

@app.route('/get_video_from_text', methods=['POST'])
def get_video_from_text(message_from_user=None):
    if not message_from_user:
        message_from_user = request.json['message_from_user']
    audio_response_text = generate_patient_audio(message_from_user)
    audio_response = json.loads(audio_response_text)
    util.log_mini_task("audio_files response: " + audio_response_text)
    # fake_json = '''{"status": "success", "request_id": "79b0e694-399f-4cbd-b0d8-e9719a7697b8", "audio_url": "http://localhost:5000/get_audio?filename=79b0e694-399f-4cbd-b0d8-e9719a7697b8.mp3", "audio_path": "/Users/alexandergoodell/code/synthetic-patients-private/audio_files/79b0e694-399f-4cbd-b0d8-e9719a7697b8.mp3", "message_from_patient": "My favorite color is green. It reminds me of the lush green fields where I used to play softball with my daughters."}'''
    # audio_response = json.loads(fake_json)
    request_id = audio_response['request_id']
    video_response = json.loads(generate_local_video(request_id))
    return json.dumps({'status': 'success',
                       'request_id': request_id,
                       'video_url': video_response['video_url'],
                       'audio_url': audio_response['audio_url'],
                       'message_from_patient': audio_response['message_from_patient']})


@app.route('/client', methods=['GET'])
def client(message_from_user=None):
    client_html = '''
    <html lang="en"><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Chat</title>
        
        
        
    <style>

#submit_chat:hover {background-color: #3c3c3c;}

#submit_chat {
    background-color: black;
}

#submit_chat:active {
    background-color: #2f8383;
}
</style>

    </head>
    <body style="
    margin: 0px;
">
        <div>
            <video id="videoPlayer" width="100%" class="active-video sp-video" src="" style="position: absolute;width: 100%;" autoplay="" muted=""></video>
            <video id="idleVideoPlayer" class="idle-video sp-video" src="http://localhost:5000/get_video?filename=idle_high-res_720_26s_adapter.webm" autoplay="" loop="" muted="" style="
    width: 100%;
"></video>



        </div>
        <div style="
">
            <form id="chatForm" style="
    display: flex;
    flex-direction: column;
">

                <textarea type="textarea" id="userMessage" name="userMessage" style="
    border: 1px solid black;
    background: rgba(239, 239, 239, 1);
    min-height: 100px;
    font-family: 'IBM Plex Mono', monospace;
    padding: 10px;
    resize: none;
"> Enter your message here. </textarea>

                <div id="loading_overlay" name="loading_overlay" style="
    min-height: 152px;
    font-family: 'IBM Plex Mono', monospace;
    position: absolute;
    width: 100%;
    display: none;
    background: rgba(220, 220, 220, 0.8);
"> Loading... </div>


                <input type="submit" id="submit_chat" value="Submit" style="
    min-width: 119px;
    color: white;
    font-family: 'IBM Plex Mono',monospace;
    padding: 15px;
">
            </form>
        </div>

        <script>

        function sleep(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
        }

        async function example(ms) {
            console.log('Start');
            await sleep(ms);
            console.log('End');
        }



            document.getElementById('chatForm').addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent form submission

                // Get user message from input field
                const userMessage = document.getElementById('userMessage').value;

                // Package message in JSON format
                const messageJSON = JSON.stringify({ "message_from_user": userMessage });

                // Send JSON to the server
                fetch('http://localhost:5000/get_video_from_text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: messageJSON
                })
                .then(response => response.json())
                .then(data => {
                    // Extract video URL from server response
                    const videoUrl = data.video_url;

                    // Change the source of the placeholder video
                    const videoPlayer = document.getElementById('videoPlayer');
                    videoPlayer.muted = false
                    videoPlayer.hidden = false
                    videoPlayer.onended = function(){videoPlayer.hidden = true;}
                    videoPlayer.setAttribute('src', videoUrl);
                })
                .catch(error => console.error('Error:', error));
            });
        </script>


    </body><div></div></html>
    '''
    return client_html


# available at https://new-fond-dog.ngrok-free.app/synthetic_patient_demo
@app.route('/synthetic_patient_demo', methods=['GET'])
def demo(message_from_user=None):
    client_html = '''
    <html lang="en"><head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Chat</title>
        
        
        
    <style>

#submit_chat:hover {background-color: #3c3c3c;}

#submit_chat {
    background-color: black;
}

#submit_chat:active {
    background-color: #2f8383;
}
</style>

    </head>
    <body style="
    margin: 0px;
">
    <div id="holder" style="width: 100%; max-width: 600px; margin: 0 auto;">
        <div>
            <video id="videoPlayer" width="100%" class="active-video sp-video" src="" style="width: 100%;" autoplay muted hidden></video>
            <video id="idleVideoPlayer" class="idle-video sp-video" src="https://new-fond-dog.ngrok-free.app/get_video?filename=idle_high-res_720_26s_adapter.webm" autoplay="" loop="" muted="" style="
            width: 100%;
        "></video>
        </div>
                <div style="
        ">
                    <form id="chatForm" style="
            display: flex;
            flex-direction: column;
        ">
        
                        <textarea type="textarea" id="userMessage" name="userMessage" style="
            border: 1px solid black;
            background: rgba(239, 239, 239, 1);
            min-height: 100px;
            font-family: 'IBM Plex Mono', monospace;
            padding: 10px;
            resize: none;
        "> Enter your message here. </textarea>
        
                        <div id="loading_overlay" name="loading_overlay" style="
            min-height: 152px;
            font-family: 'IBM Plex Mono', monospace;
            position: absolute;
            width: 100%;
            display: none;
            background: rgba(220, 220, 220, 0.8);
        "> Loading... </div>
        
        
                        <input type="submit" id="submit_chat" value="Submit" style="
            min-width: 119px;
            color: white;
            font-family: 'IBM Plex Mono',monospace;
            padding: 15px;
        ">
                    </form>
                </div>
        </div>

        <script>

        function sleep(ms) {
          return new Promise(resolve => setTimeout(resolve, ms));
        }

        async function example(ms) {
            console.log('Start');
            await sleep(ms);
            console.log('End');
        }



            document.getElementById('chatForm').addEventListener('submit', function(event) {
                event.preventDefault(); // Prevent form submission

                // Get user message from input field
                const userMessage = document.getElementById('userMessage').value;

                // Package message in JSON format
                const messageJSON = JSON.stringify({ "message_from_user": userMessage });

                // Send JSON to the server
                fetch('https://new-fond-dog.ngrok-free.app/get_video_from_text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: messageJSON
                })
                .then(response => response.json())
                .then(data => {
                    // Extract video URL from server response
                    const videoUrl = data.video_url;

                    // Change the source of the placeholder video
                    const videoPlayer = document.getElementById('videoPlayer');
                    const idleVideoPlayer = document.getElementById('idleVideoPlayer');
                    
                    videoPlayer.muted = false 
                    videoPlayer.hidden = false 
                    videoPlayer.onended = function(){
                        videoPlayer.hidden = true; 
                        idleVideoPlayer.hidden = false; 
                        idleVideoPlayer.play(); 
                    } 
                    videoPlayer.setAttribute('src', videoUrl); idleVideoPlayer.hidden = true; }) .catch(error => 
                    console.error('Error:', error)); }); </script>


    </body><div></div></html>
    '''
    return client_html


processor = Processor()
request_patient_generation()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, threaded=False)
