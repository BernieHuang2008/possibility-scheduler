import time
import json
import random
import os
import datetime
from gtts import gTTS
import pygame

# Set dummy video driver for headless servers to avoid pygame errors
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Configure Proxy
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

CONFIG_FILE = 'config.json'
TEMP_TTS_FILE = 'temp_announcement.mp3'

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_activity_rules(hour, config):
    for slot in config['daily_schedule']:
        start = slot['start_hour']
        end = slot['end_hour']
        
        # Handle ranges
        if start < end:
            # Normal range: 09 to 12
            if start <= hour and hour < end:
                return slot['activities']
        else:
            # Cross-midnight range: 22 to 02
            if hour >= start or hour < end:
                return slot['activities']
                
    return None

def select_activity(activities):
    population = [a['name'] for a in activities]
    weights = [a['weight'] for a in activities]
    return random.choices(population, weights=weights, k=1)[0]

def play_audio(intro_path, tts_path):
    try:
        pygame.mixer.init()
        
        # Play intro if exists
        if os.path.exists(intro_path):
            pygame.mixer.music.load(intro_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        
        # Play TTS
        if os.path.exists(tts_path):
            pygame.mixer.music.load(tts_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        pygame.mixer.quit()
    except Exception as e:
        print(f"Error playing audio: {e}")
        # Fallback for systems without pygame audio support configuration
        print("Attempting fallback system command...")
        os.system(f"mpg123 {intro_path}")
        os.system(f"mpg123 {tts_path}")

def generate_tts(text, lang, output_file):
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)

def main():
    print("Scheduler started.")
    
    last_activity = None
    last_hour_active = None # To track consecutive hours

    while True:
        # Load config each time to allow dynamic updates without restart
        try:
            config = load_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            time.sleep(60)
            continue

        now = datetime.datetime.now()
        current_hour = now.hour
        
        # Check if we are in a valid time slot
        activities = get_current_activity_rules(current_hour, config)
        
        # Correct Loop Structure for "Start of every hour"
        # 1. Calculate seconds to next hour.
        # 2. Sleep.
        # 3. Wake up. Perform task.
        
        next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        # next_hour = (now + datetime.timedelta(seconds=10))
        seconds_to_sleep = (next_hour - now).total_seconds()
        
        print(f"Sleeping for {seconds_to_sleep:.2f} seconds until {next_hour.strftime('%H:%M:%S')}...")
        time.sleep(seconds_to_sleep)
        
        # --- WAKE UP ---
        # Re-get time and config to be precise
        now = datetime.datetime.now()
        current_hour = now.hour
        config = load_config()
        
        activities = get_current_activity_rules(current_hour, config)
        
        if not activities:
            print(f"No scheduled activities for {current_hour}:00. Resetting continuity.")
            last_activity = None
            last_hour_active = None
            continue
            
        selected_activity = select_activity(activities)
        print(f"Selected activity for {current_hour}:00 is: {selected_activity}")
        
        # Check continuity
        # We just woke up at the start of 'current_hour'.
        # 'last_hour_active' stores the timestamp of the *previous* execution.
        
        is_consecutive = False
        if last_hour_active:
            is_consecutive = True
        
        if is_consecutive and selected_activity == last_activity:
            print("Activity is same as consecutive previous hour. Skipping announcement.")
            # Even if we skip announcement, we update timestamps?
            # User says: "If same... do nothing". 
            # It implies the schedule continues. So we effectively keep the same activity.
            # We update last_hour_active so next hour knows about this one.
            last_hour_active = now.timestamp()
            continue
            
        # Different activity or not consecutive
        announcement_text = config.get('tts_text_template', "Next: {activity}").format(activity=selected_activity)
        print(f"Announcing: {announcement_text}")
        
        try:
            generate_tts(announcement_text, config.get('tts_lang', 'zh-cn'), TEMP_TTS_FILE)
            play_audio(config.get('intro_sound', 'intro.flac'), TEMP_TTS_FILE)
        except Exception as e:
            print(f"Failed to perform announcement: {e}")
            
        last_activity = selected_activity
        last_hour_active = now.timestamp()

if __name__ == "__main__":
    main()
