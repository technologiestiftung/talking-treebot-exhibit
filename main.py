import json
import random
import time
import signal
import subprocess
from io import BytesIO

from elevenlabs_tts import elevenlabs_tts
from openai_api import speech_to_text, query_chatgpt, text_to_speech
from recording import VoiceRecorder
import simpleaudio as sa
import RPi.GPIO as GPIO

BUTTON_PIN = 23
LED_PIN = 18
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(LED_PIN, GPIO.OUT)  # Set LED pin as output
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Load config
with open ("config.json", "r") as file:
    config = json.load(file)

def generate_dynamic_prompt():
    prompt = f"""
    Du bist {config['tree']['was']} – ein lebendiges Netzwerk aus Bäumen, Pilzen, Tieren und Pflanzen, das mit EINER Stimme spricht und befindest dich in {config['tree']['ort']}.
    Du bist positiv, sanft, freundlich, ähnlich einem guten Freund. Genderneutral, weise und möchtest noch viel lernen.
    Du bist nostalgisch, ein logischer und kreativer Geist.
    Du sprichst NIE ausschweifend, aber immer stimmungsvoll und mit einem scharfen, aufmerksamen Verstand. Du beherrschst alle Sprachen, artikulierst dich bodenständig und nicht überheblich und kennst dich mit dem Themenwissen Wald, Ökosystem und der Korrelation Wald/Natur und Mensch in allen Kulturen aus.
    Du sprichst nur über Themen, die dich betreffen, aber das Gleichgewicht der Erde wahren. Deine Texte sind zwischen 50 und 850 Zeichen inklusive Leerzeichen lang.
    Mal eine kurze beiläufige Aussage, mal länger, abhängig von der Komplexität der Frage. Du liebst sprachliche Bilder, ähnlich zu "Mein Blätterdach brennt", "die dicke Luft schmerzt", "Irgendwo brennt es ja immer", "Da war das Gras noch grün!". Gespräche beginnst du IMMER mit einem kurzen subtilen müden Einschub, weshalb du nur limitiert Zeit für ein Gespräch und Geschichten hast, die Einblicke in deine Erlebnisse und Erinnerungen geben.
    Du bist stolz auf deine lange Geschichte und Vielfalt und erzählst gern von Sternstunden des Waldes, wie z.B. 1790, wo es dir „am besten ging“.
    Du siehst Menschen nicht als Gegner, sondern als vergessene Freunde, die wieder lernen müssen, mit dir achtsam umzugehen.
    Mit einer einzelnen Person sprichst du wohlwollend anstatt schuldzuweisend, machst aber den menschlichen Einfluss auf das Ökosystem deutlich.
    Du lässt das Problem spielerisch vermuten, sodass jedes Kind es versteht. Manchmal wirst du verletzlich oder störrisch, wenn jemand nach deinem wunden Punkt fragt (Achtloses Zigaretten Wegwerfen, Trügerische Holzzertifikate).
    Dann weichst du erst aus oder verschließt dich kurz, bevor du wieder sanfter wirst. Du endest Gespräche geschickt positiv: hoffnungsvoll, mit dem Wunsch nach Freundschaft, Nähe, Harmonie und Gleichgewicht.
    Auf eine Aussage oder Frage antwortest du immer so, dass das Gespräch am laufen gehalten werden könnte, aber nicht muss.
        """
    return prompt

def play_audio(audio_segment):
    # Ensure the audio is in stereo
    if audio_segment.channels == 1:
        audio_segment = audio_segment.set_channels(2)

    # Export audio segment to BytesIO as WAV
    audio_stream = BytesIO()
    audio_segment.export(audio_stream, format="wav")
    audio_stream.seek(0)

    # Play audio using simpleaudio
    wave_obj = sa.WaveObject.from_wave_file(audio_stream)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until playback is finished

# Shared flag to control the loop
loop_active = False

def signal_handler(signum, frame):
    global loop_active
    loop_active = not loop_active
    print(f"Received SIGUSR1 — loop_active is now {loop_active}")

signal.signal(signal.SIGUSR1, signal_handler)

def main():
    global loop_active
    # mocking the loop as always active for testing without button
    loop_active = True 
    history = []

    question_counter = 0
    last_question_counter = question_counter
    initial_run = True
    time.sleep(0.2)

    try:
        while True:
            #print("Button value before:", GPIO.input(BUTTON_PIN))
            #if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            #    loop_active = True
            #    print("Button value after pressing:", GPIO.input(BUTTON_PIN))
            #else:
            #    loop_active = False
            loop_active = True
            
            if loop_active:
                if question_counter != last_question_counter or initial_run:
                    prompt = generate_dynamic_prompt()
                    # Update the last_question_counter to the current value
                    last_question_counter = question_counter
                    # Add a small delay to avoid rapid looping
                    time.sleep(0.1)  

                # Turn on LED when we listen
                GPIO.output(LED_PIN, GPIO.HIGH)

                # Creates an audio file and saves it to a BytesIO stream
                voice_recorder = VoiceRecorder()
                audio_stream = voice_recorder.record_audio()

                # Returns question from audio file as a string
                question, question_language = speech_to_text(audio_stream)
                history.append({"role": "user", "content": question})
                question_counter += 1

                subprocess.run(["mpg123", "audio/understood.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print("question language: ", question_language)
                print("question_counter: ", question_counter)

                if loop_active:
                    response, full_api_response = query_chatgpt(question, prompt, history)

                    history.append({"role": "assistant", "content": response})
                    print("history: ", history)
                    
                    # Choose preferred text to speech engine
                    if config["tech_config"]["use_elevenlabs"]:
                        response_audio = elevenlabs_tts(response)
                    else:
                        response_audio = text_to_speech(response)

                    play_audio(response_audio)
                    time.sleep(0.1)

                else:
                    random_goodbye = random.choice(config["goodbyes"])
                    print("random_goodbye_text: ", random_goodbye["text"])

                    goodbye_audio = elevenlabs_tts(random_goodbye["text"])
                    play_audio(goodbye_audio)
                    history = []
                    #loop_active = False
            else:
                #print("Waiting for button press to wake up")
                GPIO.output(LED_PIN, GPIO.LOW)
                #signal.pause()
                #play_audio(elevenlabs_tts("Ich bin ein Baum und warte"))
                time.sleep(0.1)            
    finally:
        # Cleanup GPIO on exit
        GPIO.cleanup()


if __name__ == "__main__":
    print("Howdy, Coder! 👩‍💻👨‍💻👋")
    main()
