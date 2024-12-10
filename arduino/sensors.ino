#include <Wire.h>
#include "rgb_lcd.h"

// Initialize the RGB LCD
rgb_lcd lcd;

// Pin definitions
const int lightSensorPin = A2;
const int tempSensorPin = A1;

// Room identifier (unique per Arduino)
const char *room = "room1"; // Update this for each Arduino

void setup()
{
    // Initialize the LCD
    lcd.begin(16, 2);
    lcd.setRGB(255, 0, 255);

    Serial.begin(9600);
    // Print a welcome message
    lcd.print("Initializing...");
    delay(2000);
    lcd.clear();
}

void loop()
{
    int light = analogRead(lightSensorPin);

    // Read temperature (convert to Celsius)
    float temperature = analogRead(tempSensorPin) / 10.0 - 10.0;

    // Send data over Serial in JSON format, including the room identifier
    Serial.print("{\"room\":\"");
    Serial.print(room);
    Serial.print("\",\"temp\":");
    Serial.print(temperature);
    Serial.print(",\"light\":");
    Serial.print(light);
    Serial.println("}");

    // Display data on the LCD
    lcd.setCursor(0, 0);
    lcd.print("Light: ");
    lcd.print(light);

    lcd.setCursor(0, 1);
    lcd.print("Temp: ");
    lcd.print(temperature);
    lcd.print(" C");

    delay(500); // Update every 500ms
}
