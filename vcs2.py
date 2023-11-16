import tkinter as tk
from tkinter import *

# keyboard to be executed when Button 2 is clicked
def button2_click():
    import cv2
    from cvzone.HandTrackingModule import HandDetector
    import time

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # Width property is set at value 3
    cap.set(4, 720)  # Height property is set at value 4

    detector = HandDetector(detectionCon=1)  # By default, it is 0.5

    keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", "."]]

    finalText = ""
    backspaceClicked = False  # Flag to track if Backspace button was clicked

    def draw(img, btnList):
        for button in btnList:
            x, y = button.pos
            w, h = button.size
            cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
        return img

    class Button():
        def __init__(self, pos, text, size=[85, 85]):
            self.pos = pos
            self.size = size
            self.text = text

    # Define btnList before the loop
    btnList = []
    for i in range(len(keys)):
        for j, key in enumerate(keys[i]):
            btnList.append(Button([100 * j + 50, 100 * i + 50], key))

    # Add a Backspace button
    btnList.append(Button([950, 250], "<", [150, 85]))

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)

        img = detector.findHands(img)
        lmList, bboxInfo = detector.findPosition(img)
        img = draw(img, btnList)

        if lmList:
            for button in btnList:
                x, y = button.pos
                w, h = button.size

                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    if button.text == "<":
                        l, _, _ = detector.findDistance(8, 12, img, draw=False)
                        if l >= 30 and backspaceClicked:
                            continue
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        finalText = finalText[:-1]  # Remove the last character
                        backspaceClicked = False  # Set the Backspace flag
                        time.sleep(0.1555555)
                    else:
                        l, _, _ = detector.findDistance(8, 12, img, draw=False)
                        if l < 30:
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255),
                                        4)
                            finalText += button.text
                            backspaceClicked = False  # Reset the Backspace flag
                            time.sleep(0.1555555)

        cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        if cv2.waitKey(1) == ord("e"):
            break

        cv2.imshow("Image", img)
        cv2.waitKey(1)


# volume control to be executed when Button 3 is clicked
def button3_click():
    import cv2
    import time
    import numpy as np
    import hand_module as htm
    import math
    import pycaw
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    ####################################
    wCam, hcam = 640, 480
    #####################################

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hcam)
    pTime = 0
    cTime = 0
    detector = htm.handDetector(detectioncon=0.7)

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volRange = volume.GetVolumeRange()

    minVol = volRange[0]
    maxVol = volRange[1]
    vol = 0
    volBar = 400
    volPer = 0

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPos(img, draw=False)

        if len(lmList) != 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = ((x1 + x2) // 2), ((y1 + y2) // 2)

            cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (144, 298, 144), 3)  # line color
            cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)

            length = math.hypot(x2 - x1, y2 - y1)

            vol = np.interp(length, [50, 300], [minVol, maxVol])
            volBar = np.interp(length, [50, 300], [400, 150])
            volPer = np.interp(length, [50, 300], [0, 100])
            # print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)

            # Interpolate color from green to red based on volPer
            color = (0, int(255 - (volPer * 2.55)), int(volPer * 2.55))

            # Draw the volume bar with the interpolated color
            cv2.rectangle(img, (50, 150), (85, 400), color, 3)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), color, cv2.FILLED)

        cv2.putText(img, f'{int(volPer)} % ', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow("IMG", img)
        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def button4_click():
    import speech_recognition as sr
    import pyttsx3
    import datetime
    import wikipedia
    import webbrowser
    import os
    import time
    import subprocess
    from ecapture import ecapture as ec
    import wolframalpha
    import pygame
    import requests

    print('Welcome to MegaAI! How can I assist you today?')

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    pygame.mixer.init()

    def speak(text):
        engine.say(text)
        engine.runAndWait()

    def wishMe():
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            speak("Hello, Good Morning")
            print("Hello, Good Morning")
        elif 12 <= hour < 18:
            speak("Hello, Good Afternoon")
            print("Hello, Good Afternoon")
        else:
            speak("Hello, Good Evening")
            print("Hello, Good Evening")

    def play_music(query):
        music_folder = "C:\\Path\\To\\Your\\Music"
        music_file = None

        for root, dirs, files in os.walk(music_folder):
            for file in files:
                if query.lower() in file.lower():
                    music_file = os.path.join(root, file)
                    break

        if music_file:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play()
            speak(f"Now playing {query}. Enjoy!")
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
        else:
            speak(f"Sorry, I couldn't find {query} in your music collection.")

    def takeCommand():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)

        try:
            statement = r.recognize_google(audio, language='en-in')
            print(f"user said: {statement}\n")

        except Exception as e:
            speak("Sorry, I could not understand your audio.")
            return "None"
        return statement.lower()

    speak("Welcome to MegaAI! How can I assist you today?")
    wishMe()

    if __name__ == '__main__':
        while True:
            speak("Tell me how can I help you?")
            statement = takeCommand()

            if statement == 0:
                continue

            if "off" in statement or "exit" in statement or "stop" in statement:
                speak('Your personal assistant MegaAI is shutting down. Goodbye!')
                print('Your personal assistant MegaAI is shutting down. Goodbye!')
                break

            if 'wikipedia' in statement:
                speak('Searching Wikipedia...')
                statement = statement.replace("wikipedia", "")
                results = wikipedia.summary(statement, sentences=3)
                speak("According to Wikipedia")
                print(results)
                speak(results)

            elif "what is megatronix?" in statement:
                speak("megatronix is the official technical club of MSIT")
                print("megatronix is the official technical club of MSIT")

            elif 'open youtube' in statement:
                webbrowser.open_new_tab("https://www.youtube.com")
                speak("youtube is open now")
                time.sleep(5)

            elif 'open google' in statement:
                webbrowser.open_new_tab("https://www.google.com")
                speak("Google chrome is open now")
                time.sleep(5)

            elif 'open gmail' in statement:
                webbrowser.open_new_tab("gmail.com")
                speak("Google Mail open now")
                time.sleep(5)

            elif "weather" in statement or "climate" in statement:
                api_key = "8ef61edcf1c576d65d836254e11ea420"
                base_url = "https://api.openweathermap.org/data/2.5/weather?"
                speak("whats the city name")
                city_name = takeCommand()
                complete_url = base_url + "appid=" + api_key + "&q=" + city_name
                response = requests.get(complete_url)
                x = response.json()
                if x["cod"] != "404":
                    y = x["main"]
                    current_temperature = y["temp"]
                    current_humidiy = y["humidity"]
                    z = x["weather"]
                    weather_description = z[0]["description"]
                    speak(" Temperature in kelvin unit is " +
                          str(current_temperature) +
                          "\n humidity in percentage is " +
                          str(current_humidiy) +
                          "\n description  " +
                          str(weather_description))
                    print(" Temperature in kelvin unit = " +
                          str(current_temperature) +
                          "\n humidity (in percentage) = " +
                          str(current_humidiy) +
                          "\n description = " +
                          str(weather_description))

                else:
                    speak(" City Not Found ")



            elif 'time' in statement:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak(f"the time is {strTime}")

            elif "open stackoverflow" in statement:
                webbrowser.open_new_tab("https://stackoverflow.com/login")
                speak("Here is stackoverflow")

            elif 'news' in statement:
                news = webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
                speak('Here are some headlines from the Times of India,Happy reading')
                time.sleep(6)

            elif "camera" in statement or "take a photo" in statement:
                ec.capture(0, "robo camera", "img.jpg")

            elif 'search' in statement:
                statement = statement.replace("search", "")
                webbrowser.open_new_tab(statement)
                time.sleep(5)

            elif 'ask' in statement:
                speak(
                    'I can answer to computational and geographical questions and what question do you want to ask now')
                question = takeCommand()
                app_id = "R2K75H-7ELALHR35X"
                client = wolframalpha.Client('R2K75H-7ELALHR35X')
                res = client.query(question)
                answer = next(res.results).text
                speak(answer)
                print(answer)

            elif "play music" in statement:
                query = statement.replace('play music', '')
                play_music(query)
                speak("Playing music.")
                print("playing music")

            elif "log off" in statement or "sign out" in statement:
                speak("Ok , your pc will log off in 10 sec make sure you exit from all applications")
                subprocess.call(["shutdown", "/l"])

    time.sleep(3)




# Create the main window
root = tk.Tk()
root.title("Virtual Computer System 2")
root.geometry("1920x1200")  # Set window dimensions

# Customize the main window background color
root.configure(bg="#23272f")

# Create a custom font
custom_font = ("cambria", 16, "bold")

image = tk.PhotoImage(file="megalogowithstroke.png")
image_label = tk.Label(root, image=image, bg="#23272f")
image_label.pack()


# Create Button 2 with different colors and font and center it
button2_style = tk.Button(root, text="Virtual Keyboard", command=button2_click, relief="flat", font=custom_font,
                          bg="#087ea4", fg="white")
button2_style.pack(pady=20)

# Create Button 3 with another set of colors and font and center it
button3_style = tk.Button(root, text="Virtual volume control", command=button3_click, relief="flat", font=custom_font,
                          bg="#087ea4", fg="white")
button3_style.pack(pady=20)


button4_style = tk.Button(root, text="Mega AI", command=button4_click, relief="flat", font=custom_font,
                          bg="#087ea4", fg="white")
button4_style.pack(pady=20)




# Start the GUI main loop
root.mainloop()
