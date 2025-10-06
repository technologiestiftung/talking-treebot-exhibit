import time
import board
import neopixel

# --- LED strip configuration ---
LED_PIN = board.D18        # GPIO18 (physical pin 12)
NUM_LEDS = 16              # Number of LEDs on your strip
BRIGHTNESS = 0.8          # Overall brightness (0.0–1.0)
ORDER = neopixel.GRB       # WS2812B uses GRB order

pixels = neopixel.NeoPixel(
    LED_PIN,
    NUM_LEDS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

print("LED strip initialized ✅")

def interpolate_color(start, end, factor: float):
    """Linearly interpolate between two RGB colors."""
    return tuple(int(start[i] + (end[i] - start[i]) * factor) for i in range(3))

def smooth_dimmer(start, end, steps=100, delay=0.02):
    """Smoothly fade between two colors."""
    for i in range(steps):
        f = i / (steps - 1)
        color = interpolate_color(start, end, f)
        pixels.fill(color)
        pixels.show()
        time.sleep(delay)


# --- Animation modes ---
def dimmerThink(steps=200, delay=0.02):
    """Fade from dark blue → light blue repeatedly."""
    dark_blue = (0, 0, 60)       # raw RGB
    light_blue = (0, 0, 255)     # raw RGB
    print("Running dimmerThink (blue fade)...")
    while True:
        # Fade up
        for i in range(steps):
            factor = i / (steps - 1)
            color = interpolate_color(dark_blue, light_blue, factor)
            pixels.fill(color)
            pixels.show()
            time.sleep(delay)
        # Fade down
        for i in range(steps):
            factor = i / (steps - 1)
            color = interpolate_color(light_blue, dark_blue, factor)
            pixels.fill(color)
            pixels.show()
            time.sleep(delay)


def dimmerTalk(steps=200, delay=0.02):
    """Fade from dark green → light green repeatedly."""
    dark_green = (0, 60, 0)
    light_green = (0, 255, 0)
    print("Running dimmerTalk (green fade)...")
    while True:
        # Fade up
        for i in range(steps):
            factor = i / (steps - 1)
            color = interpolate_color(dark_green, light_green, factor)
            pixels.fill(color)
            pixels.show()
            time.sleep(delay)
        # Fade down
        for i in range(steps):
            factor = i / (steps - 1)
            color = interpolate_color(light_green, dark_green, factor)
            pixels.fill(color)
            pixels.show()
            time.sleep(delay)


# --- Main entry point ---
if __name__ == "__main__":
    try:
        print("Select mode: 'think' or 'talk'")
        mode = input("Mode: ").strip().lower()

        if mode == "think":
            dimmerThink()
        elif mode == "talk":
            dimmerTalk()
        else:
            print("Unknown mode. Use 'think' or 'talk'.")

    except KeyboardInterrupt:
        print("\nStopping and clearing LEDs...")
        pixels.fill((0, 0, 0))
        pixels.show()
        print("LEDs off. Goodbye 👋")
