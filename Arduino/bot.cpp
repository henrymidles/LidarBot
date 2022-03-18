#include "bot.h"

Bot::Bot()
	:RightStepper(2, RIGHT_STEP_PIN, RIGHT_DIR_PIN), 
 	 LeftStepper(2, LEFT_STEP_PIN, LEFT_DIR_PIN)
{
	pinMode(RIGHT_EN_PIN, OUTPUT);
	pinMode(LEFT_EN_PIN, OUTPUT);
	digitalWrite(RIGHT_EN_PIN, HIGH);
	digitalWrite(LEFT_EN_PIN, HIGH);
	this->RightStepper.setMaxSpeed(MAX_SPEED);
	this->RightStepper.setAcceleration(MAX_ACCEL); 
	this->LeftStepper.setMaxSpeed(MAX_SPEED);
	this->LeftStepper.setAcceleration(MAX_ACCEL);

	this->battery = 0;
}

void Bot::update_steppers()
{
	static unsigned long rightTimer = 0;
	static unsigned long leftTimer = 0;
	static uint8_t moving = 0b0011;
	this->check_serial();
	this->LeftStepper.run();
	this->RightStepper.run();

	if(this->RightStepper.distanceToGo() == 0)
	{
		//if(rightTimer == 0) rightTimer = millis()+1500;
		if(millis() > rightTimer)
		{
			digitalWrite(RIGHT_EN_PIN, HIGH);
			rightTimer = millis()+500;
		}
	}
	if(this->LeftStepper.distanceToGo() == 0)
	{
		//if(leftTimer == 0) leftTimer = millis()+1500;
		if(millis() > leftTimer)
		{
			digitalWrite(LEFT_EN_PIN, HIGH);
			leftTimer = millis()+500;
		}
	}
}

//***************************************************************************//
// Run both motors until desired postion is reached
//***************************************************************************//
void Bot::run_to_position(int left, int right)
{
	uint8_t motors_finished = 0;
	uint16_t count = 0;
	this->LeftStepper.move(left);
	this->RightStepper.move(right);
	digitalWrite(RIGHT_EN_PIN, LOW);
   digitalWrite(LEFT_EN_PIN, LOW);
   Serial.print("Moving Left to: ");
   Serial.println(this->LeftStepper.distanceToGo());
   Serial.print("Moving Right to: ");
   Serial.println(this->RightStepper.distanceToGo());
	while(motors_finished != 0b0011)
	{
		if((this->RightStepper.distanceToGo() == 0) && ((motors_finished & 0b0001) == 0))
		{
			digitalWrite(RIGHT_EN_PIN, HIGH);
			motors_finished |= 0b0001;
			Serial.print("Right Finished");
			Serial.println(motors_finished, BIN);
		}
		if((this->LeftStepper.distanceToGo() == 0) && ((motors_finished & 0b0010) == 0))
		{
			digitalWrite(LEFT_EN_PIN, HIGH);
			motors_finished |= 0b0010;
			Serial.print("Left Finished");
			Serial.println(motors_finished, BIN);
		}
	}
}

//***************************************************************************//
// Check main serial input, communication with raspberry pi
//***************************************************************************//
void Bot::check_serial()
{
	if(Serial.available() > 0)
	{
		this->buff[b_idx] = Serial.read();
		if(buff[b_idx] == '\n')
		{
			this->decode_buff();
			this->b_idx = 0;
			return;
		}
		if(this->b_idx >= 99)
		{
			Serial.println("Buff Overflow");
			this->b_idx = 0;
			return;
		}
		this->b_idx += 1;
	}
}

//***************************************************************************//
// Decode the main buffer, these are primary commands from the feather
//***************************************************************************//
void Bot::decode_buff()
{
	if(this->b_idx < 4) {Serial.println("Short Message"); return;}
	String code = String(this->buff[0]) + String(this->buff[1]) + String(this->buff[2]);
	String data_s;
	for(uint8_t i=3; i<this->b_idx; i+=1){data_s.concat(this->buff[i]);}
	int data = data_s.toInt();
	int data_cm  = data*STEPS_PER_CM;
	int data_deg = data*STEPS_PER_DEG; 
	
	if(code == "RGT")
	{
		this->RightStepper.move(data_cm);
		digitalWrite(RIGHT_EN_PIN, LOW);
	}
	else if(code == "LFT")
	{
		this->LeftStepper.move(data_cm);
	   digitalWrite(LEFT_EN_PIN, LOW);
	}
	else if(code == "MOV")
	{
		this->LeftStepper.move(data_cm);
		this->RightStepper.move(data_cm);
	   digitalWrite(LEFT_EN_PIN, LOW);
	   digitalWrite(RIGHT_EN_PIN, LOW);
	}
	else if(code == "TRN")
	{
		this->LeftStepper.move(-data_deg);
		this->RightStepper.move(data_deg);
	   digitalWrite(LEFT_EN_PIN, LOW);
	   digitalWrite(RIGHT_EN_PIN, LOW);
	}
	else if(code == "STP")
	{
		if     (this->RightStepper.distanceToGo() >  STOP_STEPS) this->RightStepper.move(STOP_STEPS);
		else if(this->RightStepper.distanceToGo() < -STOP_STEPS) this->RightStepper.move(-STOP_STEPS);
		if     (this->LeftStepper.distanceToGo()  >  STOP_STEPS) this->LeftStepper.move(STOP_STEPS);
		else if(this->LeftStepper.distanceToGo()  < -STOP_STEPS) this->LeftStepper.move(-STOP_STEPS);
	}
	else if(code == "STA")
	{
		Serial.print(this->RightStepper.distanceToGo());
		Serial.print(',');
		Serial.print(this->LeftStepper.distanceToGo());
		Serial.print(',');
		Serial.println(this->battery);
	}
	else if(code == "ID?") Serial.println("micro");
	else Serial.print("Unknown Code");
}
