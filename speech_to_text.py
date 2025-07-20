import speech_recognition as sr
import re 
import threading
from calculator_gui import NumberDisplayGUI 

# a Recognizer to recognize and process auio input
r = sr.Recognizer()

# Function to continuously listen for audio input and recognize speech
# and return the recognized text using Google Web Speech API
def record_text(language="en-US"):
    while True:
        try:
            with sr.Microphone() as source2:
                # Reduces background noise influence
                r.adjust_for_ambient_noise(source2, duration=0.2)
                print("Listening...")
                # Listening for audio input
                audio2 = r.listen(source2)
                # Sending the audio to Google Web Speech API for recognition
                my_text = r.recognize_google(audio2, language=language)
                return my_text

        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            return ""
        except sr.UnknownValueError:
            print("Unknown error occurred")
            return ""

# Function to output recognized text to output.txt
def output_text(text):
    with open("output.txt", "a") as f:
        f.write(text + "\n")

# Function to run the speech recognition in a loop
# and handle specific keywords for number input
def run_recognition(gui):
    while True:
        text = record_text()
        print("Recognized:", text)

        if not text:
            continue
 
        output_text(text)

        # Important:
        # If the text includes trigger keywords, a secondary prompt is initiated to listen for a number.
        if any(keyword in text.lower() for keyword in ["wait", "yes", "ready", "okay", "equals"]):
            print("🔔 Triggered. The next input will be taken as a number.")
            number_text = record_text()
            # Searching and extracting the number from the recognized text (using regex)
            match = re.search(r"\d+", number_text)
            if match:
                number = match.group()
                print("📊 The number:", number)
                gui.update_number(number)
            else:
                print("⚠️ No number found after command.")

if __name__ == "__main__":
    gui = NumberDisplayGUI()

    threading.Thread(target=run_recognition, args=(gui,), daemon=True).start()

    gui.run()
