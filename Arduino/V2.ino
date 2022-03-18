#include "bot.h"
#include <Adafruit_DotStar.h>

#define NUMPIXELS      1 
#define LED_DATAPIN    8
#define LED_CLOCKPIN   6

Bot StepperBot;
Adafruit_DotStar strip(NUMPIXELS, LED_DATAPIN, LED_CLOCKPIN, DOTSTAR_BRG);

//***************************************************************************//
// Setup code
//***************************************************************************//
void setup() 
{
	strip.begin(); // Initialize pins for output
	strip.setPixelColor(0, 5, 0, 0);
	strip.show();

	pinMode(A5, INPUT);

	Serial.begin(250000);
	delay(6000);
	Serial.println("Starting!");
}

//***************************************************************************//
// Main Loop
//***************************************************************************//
void loop() 
{
	static unsigned long timer = 0;
	static uint16_t bat;
	StepperBot.update_steppers();

	if(millis() > timer)
	{
		bat = analogRead(A5);
		if(bat < 600)
		{
			strip.setPixelColor(0, 0, 20, 0);
			while(true)
			{
				Serial.println("Battery Low!");
				delay(1000);
			}
		}
		timer = millis() + 1000;
	}
}
