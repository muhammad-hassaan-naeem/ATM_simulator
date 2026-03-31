from playsound import playsound
import threading
import time

def play_sound(path):
    threading.Thread(target=playsound, args=(path,), daemon=True).start()

def delayed_sound(path, delay=0.5):
    def run():
        time.sleep(delay)
        playsound(path)
    threading.Thread(target=run, daemon=True).start()