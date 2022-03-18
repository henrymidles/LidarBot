
#include "Arduino.h"
#include <AccelStepper.h>

#define RIGHT_DIR_PIN  7
#define RIGHT_STEP_PIN 9
#define RIGHT_EN_PIN   10

#define LEFT_DIR_PIN   11
#define LEFT_STEP_PIN  12
#define LEFT_EN_PIN    13

#define MAX_SPEED		 5000 // speed in steps / second
#define MAX_ACCEL	 	 7000 // Acceleration steps / second^2
#define STOP_STEPS	 1785 // number of steps to go from full speed to stop

#define STEPS_PRE_REV 2133
#define STEPS_PER_CM  97
#define STEPS_PER_DEG 17

class Bot
{
	public:
		Bot();
		void run_to_position(int left, int right);
		void check_serial();
		void update_steppers();
		AccelStepper RightStepper;
		AccelStepper LeftStepper;
	private:
		void decode_buff();
		char buff[100];
		uint8_t b_idx;
		float battery;
};
