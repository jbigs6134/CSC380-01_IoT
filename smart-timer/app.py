# jack_control start, jack_control stop

import pyaudio

audio = pyaudio.PyAudio()

print("Available Audio Devices: ")

for i in range(audio.get_device_count()):

    info = audio.get_device_info_by_index(i)
    print(f"Index: {i},name {info['name']},maxInputChannels: {info['maxInputChannels']}, maxOutputChannels: {info['maxOutputChannels']}")

audio.terminate()

import io

import time
import wave
from grove.factory import Factory

# The button on the ReSpeaker 2-Mics Pi HAT
button = Factory.getButton("GPIO-LOW", 17)

audio = pyaudio.PyAudio()

microphone_card_number = 3
speaker_card_number = 3

rate = 44100 #48KHz
channels = 2 #mono
frames_per_buffer = 1024 #mono

def capture_audio():
    try:
        stream = audio.open(format = pyaudio.paInt16,
                        rate = rate,
                        channels = channels,   #was 1
                        input_device_index = microphone_card_number,
                        input = True,
                        frames_per_buffer = frames_per_buffer)
        frames = []

        print("Press button.")

        while button.is_pressed():
        
            print("Recording...")

            frames.append(stream.read(frames_per_buffer, exception_on_overflow = False))

        print("Stopping...")

        stream.stop_stream()
        stream.close()

        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, 'wb') as wavefile:
    
            wavefile.setnchannels(channels)
            wavefile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wavefile.setframerate(rate)
            wavefile.writeframes(b''.join(frames))
            wav_buffer.seek(0)

        return wav_buffer

    except Exception as e:

        print(f"error during recording: {e}")

        return None

def play_audio(buffer):
 
    try:

        stream = audio.open(format = pyaudio.paInt16,
        rate = rate,
        channels = channels,
        output_device_index = speaker_card_number,
        output = True)
 
        with wave.open(buffer, 'rb') as wf:
        
            data = wf.readframes(frames_per_buffer)
    
            while len(data) > 0:
            
                stream.write(data)
                data = wf.readframes(frames_per_buffer)
        
            stream.close()
    
    except Exception as e:
        
        print(f"error during playback: {e}")

while True:
 
    while not button.is_pressed():
        
        time.sleep(.1)
    
    buffer = capture_audio()
    play_audio(buffer)
