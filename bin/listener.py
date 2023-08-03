import os

from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import openai
from playsound import playsound
from pynput.keyboard import Controller as KeyboardController, Key, Listener
from scipy.io import wavfile

from oa import apply_whisper, chatgpt
from polly import text_to_speech

load_dotenv()
key_label = os.environ.get("RECORD_KEY", "ctrl_r")
RECORD_KEY = Key[key_label]

recording = False
audio_data = []
sample_rate = 16000
keyboard_controller = KeyboardController()
message_history = []


def main():
    def on_press(key):
        global recording
        global audio_data
        # When the right shift key is pressed, start recording
        if key == RECORD_KEY:
            recording = True
            audio_data = []
            print("Recording started...")

    def on_release(key):
        global recording
        global audio_data
        global message_history
        
        # When the right shift key is released, stop recording
        if key == RECORD_KEY:
            recording = False
            print("Recording stopped.")
            
            try:
                audio_data_np = np.concatenate(audio_data, axis=0)
            except ValueError as e:
                print(e)
            
            audio_data_int16 = (audio_data_np * np.iinfo(np.int16).max).astype(np.int16)
            wavfile.write('recording.wav', sample_rate, audio_data_int16)

            transcript = None
            try:
                transcript = apply_whisper('recording.wav', 'transcribe')
            except openai.error.InvalidRequestError as e:
                print(e)
            
            if transcript:
                # clear history when "clear" is said
                letters_only = ''.join([char for char in transcript if char.isalpha()])
                if letters_only.lower().strip() == 'clear':
                    message_history = []
                    playsound('bin/sounds/clear.mp3')
                    return
                history = chatgpt(transcript, message_history)
                message_history = history
                print(message_history)
                response = history[-1]['content']
                text_to_speech(response)
                playsound('output.mp3')


    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())  # make sure to copy the indata


    with Listener(on_press=on_press, on_release=on_release) as listener:
        # This is the stream callback
        with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
            # Just keep the script running
            listener.join()

if __name__ == "__main__":
    playsound('bin/sounds/start.mp3')
    try:
        main()
    except KeyboardInterrupt:
        playsound('bin/sounds/stop.mp3')