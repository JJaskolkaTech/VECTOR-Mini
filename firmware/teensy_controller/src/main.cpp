// VECTOR Mini v0.2 firmware scaffold — Teensy 4.0
// Hardware actuation remains disabled until pin mapping and bench limits are verified.
#include <Arduino.h>

enum class State { IDLE, ARMING, FLEX, HOLD, EXTEND, RESET, E_STOP };

constexpr uint32_t WATCHDOG_TIMEOUT_MS = 150;
constexpr int MOTOR_ENABLE_PIN = 255;  // Deliberately invalid: configure before hardware use.

State state = State::IDLE;
uint32_t lastSensorFrameMs = 0;
bool faultLatched = false;

void safeStop() {
  faultLatched = true;
  state = State::E_STOP;
  // A future hardware revision must de-energize through an independent safety path.
}

void setup() {
  Serial.begin(115200);
  safeStop();  // Power-up state is non-actuating by design.
}

void loop() {
  const uint32_t now = millis();
  if (now - lastSensorFrameMs > WATCHDOG_TIMEOUT_MS) {
    safeStop();
  }
  // v0.2 work: framed serial input, sensor validation, explicit arming,
  // bounded controller output, and physical e-stop input.
}

