import RPi.GPIO as GPIO
import time
import board
import neopixel
import subprocess

# --- Pin configuration ---
BUTTON_PIN = 23           # Button pin
LED_PIN = board.D18       # WS2812B data pin (GPIO18)
NUM_LEDS = 16
BRIGHTNESS = 0.9
ORDER = neopixel.GRB

# --- NeoPixel setup ---
pixels = neopixel.NeoPixel(
    LED_PIN,
    NUM_LEDS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

# --- GPIO setup for button ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("System ready ✅ — press button to trigger LED sequence")

# --- Helper functions ---
def interpolate_color(start, end, factor: float):
    """Linearly interpolate between two RGB colors."""
    return tuple(int(start[i] + (end[i] - start[i]) * factor) for i in range(3))


def smooth_dimmer(start, end, steps=150, delay=0.01):
    """Smoothly fade between two colors, up and down once."""
    # Fade up
    for i in range(steps):
        f = i / (steps - 1)
        color = interpolate_color(start, end, f)
        pixels.fill(color)
        pixels.show()
        time.sleep(delay)
    # Fade down
    for i in range(steps):
        f = i / (steps - 1)
        color = interpolate_color(end, start, f)
        pixels.fill(color)
        pixels.show()
        time.sleep(delay)

def dimmerThink():
    """Blue/aqua fade animation."""
    dark_aqua = (0, 10, 30)
    light_aqua = (0, 200, 255)
    smooth_dimmer(dark_aqua, light_aqua)

def dimmerTalk():
    """Fade from dark green → light green repeatedly."""
    dark_green  = (10, 40, 0)
    light_green = (100, 220, 20)
    smooth_dimmer(dark_green, light_green)

# def dimmerIdle():
# """Fade from dark green → light green repeatedly."""
#     dark_white = (20, 20, 15)    
#     bright_white = (255, 255, 240) 
#     smooth_dimmer(dark_white, bright_white)

try:
    while True:
        # Button pressed (active low)
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH: 
            print("Button value:", GPIO.input(BUTTON_PIN))
            time.sleep(0.05)  # Debounce delay
            print("🔘 Button pressed — triggering LED strip")

            # Trigger your systemd signal if you still need it
            subprocess.run(
                ["systemctl", "--user", "kill", "--signal=SIGUSR1", "treebot.service"]
            )

            # Run LED animation
            #dimmerThink()
            dimmerTalk()

            # Debounce delay
            time.sleep(0.5)

    # Small idle delay to avoid CPU spikes
    time.sleep(0.05)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    print("\nCleaning up... Turning off LEDs and releasing GPIO.")
    try:
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.1)
        pixels.deinit()
    except Exception as e:
        print(f"⚠️ LED cleanup error: {e}")

    GPIO.cleanup()
    print("Cleanup complete. LEDs off 🌲")