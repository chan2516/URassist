# chat bot 
import hugchat
import pyttsx3
import speech_recognition as sr
import eel
import time
query = "hi"
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    eel.receiverText(text)
    engine.runAndWait()



heelo = "hi"
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    #print(response)
    speak(response) 
    return response
chatBot(heelo)
