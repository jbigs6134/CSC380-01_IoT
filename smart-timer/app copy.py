import requests
import pyaudio
import io
import time
import wave
from grove.factory import Factory
import atexit

# The button on the ReSpeaker 2-Mics Pi HAT
button = Factory.getButton("GPIO-LOW", 17)

audio = pyaudio.PyAudio()

microphone_card_number = 3
speaker_card_number = 3

rate = 44100  # 48KHz
channels = 1  # mono

def capture_audio():
    try:
        # Open the audio stream
        stream = audio.open(format=pyaudio.paInt16,
                            rate=rate,
                            channels=channels,
                            input_device_index=microphone_card_number,
                            input=True,
                            frames_per_buffer=4096)
        frames = []

        print("Press button.")

        # Capture audio until the button is pressed
        while button.is_pressed():
            print("Recording...")
            frames.append(stream.read(4096))

        print("Stopping...")
        stream.stop_stream()
        stream.close()

        # Save the audio to a buffer
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wavefile:
            wavefile.setnchannels(channels)
            wavefile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wavefile.setframerate(rate)
            wavefile.writeframes(b''.join(frames))
            wav_buffer.seek(0)

        return wav_buffer

    except Exception as e:
        print(f"Error during recording: {e}")
        return None

speech_api_key = 'e7b8fbed3ce1438591728a379d9134a6'
location = 'northcentralus'
language = 'en-GB'

def get_access_token():
    headers = {
        'Ocp-Apim-Subscription-Key': speech_api_key
    }
    token_endpoint = f'https://{location}.api.cognitive.microsoft.com/sts/v1.0/issuetoken'
    response = requests.post(token_endpoint, headers=headers)
    return str(response.text)

def convert_speech_to_text(buffer):
    url = f'https://{location}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'
    
    headers = {
        'Authorization': 'Bearer ' + get_access_token(),
        'Content-Type': f'audio/wav; codecs=audio/pcm; samplerate={rate}',
        'Accept': 'application/json;text/xml'
    }
    params = {
        'language': language
    }

    response = requests.post(url, headers=headers, params=params, data=buffer)
    response_json = response.json()

    if response_json['RecognitionStatus'] == 'Success':
        return response_json['DisplayText']
    else:
        return ''

def process_text(text):
    print(text)

# Main loop
while True:
    # Wait for the button to be pressed
    while not button.is_pressed():
        time.sleep(0.1)

    # Capture audio when button is pressed
    buffer = capture_audio()

    if buffer:
        # Convert speech to text
        text = convert_speech_to_text(buffer)
        # Process the recognized text
        process_text(text)

def cleanup_gpio():
    # Clean up GPIO (optional, Grove library usually manages this)
    pass

atexit.register(cleanup_gpio)

