import speech_recognition as sr
import pyaudio
import wave


# pip install pyaudio


# Initialize the recognizer
r = sr.Recognizer()

# Define the keyword to trigger the action
keyword = "hello kitchen"

# Set the audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open the microphone stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("Listening...")
while True:
    frames = []
    # Capture audio data in chunks
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # Stop the microphone stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("Recording finished.")

    # Save the captured audio to a WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print("Audio saved to", WAVE_OUTPUT_FILENAME)

    # Load the captured audio file for speech recognition
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio = r.record(source)

    try:
        # Recognize speech using Google Speech Recognition
        text = r.recognize_google(audio)
        print("Heard:", text)

        # Check if the keyword is present in the recognized text
        if keyword in text:
            # Extract the action from the recognized text
            action = text.split(keyword)[1].strip().lower()
            print("Action:", action)

            # Perform actions based on the recognized command
            if action.startswith("add"):
                item = action.split("add")[1].strip()
                # print("Adding", item)
                # Check if the item is for the fridge list
                if "to fridge list" in action:
                    print("Adding", item, "to the fridge list")
                    # Perform the logic to add the item to the fridge list

                # Check if the item is for the pantry list
                elif "to pantry list" in action:
                    print("Adding", item, "to the pantry list")
                    # Perform the logic to add the item to the pantry list

                # Check if the item is for the counter list
                elif "to counter list" in action:
                    print("Adding", item, "to the counter list")
                    # Perform the logic to add the item to the counter list

                # Check if the item is for the shopping list
                elif "to shopping list" in action:
                    print("Adding", item, "to the shopping list")
                    # Perform the logic to add the item to the shopping list

                else:
                    print("Invalid target list")

            elif action.startswith("delete"):
                item = action.split("delete")[1].strip()
                # print("Deleting", item)
                # Perform the logic to delete the item from the respective list
                # Check if the item is for the fridge list
                if "to fridge list" in action:
                    print("Deleting", item, "to the fridge list")
                    # Perform the logic to delete the item to the fridge list

                # Check if the item is for the pantry list
                elif "to pantry list" in action:
                    print("Deleting", item, "to the pantry list")
                    # Perform the logic to delete the item to the pantry list

                # Check if the item is for the counter list
                elif "to counter list" in action:
                    print("Deleting", item, "to the counter list")
                    # Perform the logic to delete the item to the counter list

                # Check if the item is for the shopping list
                elif "to shopping list" in action:
                    print("Deleting", item, "to the shopping list")
                    # Perform the logic to delete the item to the shopping list

                else:
                    print("Invalid target list")
            else:
                print("Invalid action")

    except sr.UnknownValueError:
        print("Could not understand audio")

    except sr.RequestError as e:
        print("Error: {0}".format(e))
