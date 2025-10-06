// --- Touch Sensor mit Median-Filter und 5s-Haltezeit ---
// Board: ESP32 DevKitC (Beispiel: TouchPin GPIO27, LED GPIO25)

const int touchPin = 27;   // Touch input (ESP32: e.g. GPIO27)
const int ledPin   = 25;   // LED pin (z.B. GPIO25)

int threshold = 0;         // Touch-Schwelle (Kalibrierung)
bool calibrated = false;   // Kalibrierungs-Status

const int N = 31;          // Anzahl Samples für Median (ungerade)
int buffer[N];

// Timer für 5s Haltezeit
unsigned long touchStart = 0;
const unsigned long holdTime = 500; // 0.5 Sekunden

// --- Setup ---
void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  Serial.println("Calibration (5 seconds)... do not touch!");
  long sum = 0;
  int count = 0;
  unsigned long start = millis();

  // 5 Sekunden Mittelwert für Baseline sammeln
  while (millis() - start < 5000) {
    int val = touchRead(touchPin);
    sum += val;
    count++;
    delay(50);
  }

  threshold = (sum / count) - 15;  // Threshold etwas unter Baseline
  calibrated = true;

  Serial.print("Calibration done. Threshold = ");
  Serial.println(threshold);
}

// --- Hilfsfunktion: Median von N Samples ---
int readMedian(int pin) {
  for (int i = 0; i < N; i++) {
    buffer[i] = touchRead(pin);
    delay(2);
  }
  // sortieren (Bubble Sort, reicht für N=31)
  for (int i = 0; i < N - 1; i++) {
    for (int j = 0; j < N - i - 1; j++) {
      if (buffer[j] > buffer[j + 1]) {
        int tmp = buffer[j];
        buffer[j] = buffer[j + 1];
        buffer[j + 1] = tmp;
      }
    }
  }
  return buffer[N/2]; // Median zurückgeben
}

// --- Loop ---
void loop() {
  int val = readMedian(touchPin);   // val = Medianwert

  Serial.print("Touch (median): ");
  Serial.print(val);
  Serial.print("  Threshold: ");
  Serial.println(threshold);

  if (calibrated && val < threshold) {
    // Finger erkannt
    if (touchStart == 0) {
      touchStart = millis();  // Timer starten
    }

    // wenn 5s lang berührt → LED an
    if (millis() - touchStart >= holdTime) {
      digitalWrite(ledPin, HIGH);
    }
  } else {
    // kein Finger → LED aus, Timer zurücksetzen
    digitalWrite(ledPin, LOW);
    touchStart = 0;
  }
}