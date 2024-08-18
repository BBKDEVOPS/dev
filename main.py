import ollama
import speech_recognition as sr
from gtts import gTTS
import playsound
import os

# ฟังก์ชันสำหรับดึงข้อมูลจาก Ollama
def fetch_data(query):
    response = ollama.search(query)
    return response['data']

# ฟังก์ชันสำหรับแปลงข้อความเป็นเสียง
def text_to_speech(text, lang='th'):
    tts = gTTS(text=text, lang=lang)
    filename = "response.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# ฟังก์ชันสำหรับรับคำถามจากผู้ใช้
def get_user_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("พูดคำถามของคุณ:")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='th-TH')
            print(f"คุณพูดว่า: {text}")
            return text
        except sr.UnknownValueError:
            print("ไม่สามารถเข้าใจเสียงได้")
            return None
        except sr.RequestError:
            print("ไม่สามารถเชื่อมต่อกับบริการได้")
            return None

# ฟังก์ชันหลัก
def main():
    while True:
        user_query = get_user_input()
        if user_query:
            data = fetch_data(user_query)
            response = process_data(data)  # ฟังก์ชันสำหรับพัฒนาข้อมูล
            text_to_speech(response)

if __name__ == "__main__":
    main()
