import io
import pyaudio
import time
import wave
from grove.factory import Factory

# The button on the ReSpeaker 2-Mics Pi HAT
button = Factory.getButton("GPIO-LOW", 17)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Microphone and speaker card numbers
device_index = 2  # seeed-2mic-voicecard (hw:3,0)

# Audio settings
rate = 44100  # Sample rate
chunk_size = 4096  # Frames per buffer
channels = 2  # Use 1 for mono or 2 for stereo

def capture_audio():
    """Capture audio from the microphone while the button is pressed."""
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            rate=rate,
            channels=channels,
            input_device_index=device_index,
            input=True,
            frames_per_buffer=chunk_size
        )
        frames = []

        print("Recording... Press the button to stop.")
        while button.is_pressed():
            frames.append(stream.read(chunk_size, exception_on_overflow=False))

        print("Recording stopped.")
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
        print(f"Error during recording: {e}")
        return None

def play_audio(buffer):
    """Play back audio from a buffer."""
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            rate=rate,
            channels=channels,
            output_device_index=device_index,
            output=True
        )

        with wave.open(buffer, 'rb') as wf:
            print("Playing back audio...")
            data = wf.readframes(chunk_size)
            while len(data) > 0:
                stream.write(data)
                data = wf.readframes(chunk_size)

        stream.stop_stream()
        stream.close()
        print("Playback finished.")

    except Exception as e:
        print(f"Error during playback: {e}")

# Main loop
try:
    print("Press the button to start recording.")
    while True:
        if button.is_pressed():
            buffer = capture_audio()
            if buffer:
                play_audio(buffer)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting program.")

finally:
    audio.terminate()