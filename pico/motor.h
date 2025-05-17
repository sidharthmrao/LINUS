#pragma once

#include "pico/stdlib.h"
#include <math.h>

#define MICROSTEP_RESOLUTION 8   // 1/16 microstepping
#define STEPS_PER_REVOLUTION 200 // 1.8 degree stepper motor
#define TICKS_PER_REVOLUTION (STEPS_PER_REVOLUTION * MICROSTEP_RESOLUTION)

#define REVOLUTIONS_PER_UNIT_X 1.0f
#define REVOLUTIONS_PER_UNIT_Y 1.0f

#define TICKS_PER_UNIT_X REVOLUTIONS_PER_UNIT_X *TICKS_PER_REVOLUTION
#define TICKS_PER_UNIT_Y REVOLUTIONS_PER_UNIT_Y *TICKS_PER_REVOLUTION

// Pulse width in microseconds (step pulse duration)
#define STEP_PULSE_WIDTH_US 5

typedef struct
{
    uint STEP_PIN;
    uint DIR_PIN;
    uint EN_PIN;
    volatile int last_target_position;
    volatile int current_position;
    volatile int target_position;
    volatile float velocity_rps; // current speed in rps
    float max_velocity_rps;      // max speed in rps
    float max_acceleration;      // max acceleration in rps/s
    int step_direction;          // direction of rotation (1 for CW, -1 for CCW)
    bool flipped;
    uint64_t last_time_us;
    repeating_timer_t timer;
} StepperMotor;

void set_target_position(StepperMotor *x, StepperMotor *y, float target_x, float target_y)
{
    x->last_target_position = x->target_position;
    y->last_target_position = y->target_position;
    x->target_position = (int)(target_x * TICKS_PER_UNIT_X);
    y->target_position = (int)(target_y * TICKS_PER_UNIT_Y);
}