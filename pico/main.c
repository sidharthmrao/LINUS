
#include "pico/stdlib.h"

#include "hardware/pwm.h"
#include "hardware/irq.h"
#include "hardware/uart.h"

#include "pico/multicore.h"
#include <stdlib.h>
#include <stdio.h>

#include "motor.h"
#include "target.h"

#define WRAPVAL 5000
#define CLKDIV 25.0f

#define LED_PIN 25

#define X_AXIS_IN_PER_ROT (M_PI * .53)
#define X_AXIS_TOTAL_IN 16
#define X_AXIS_TOTAL_UNITS 100
#define X_AXIS_ROT_PER_UNITS .096 // ((X_AXIS_TOTAL_IN / X_AXIS_TOTAL_UNITS) / X_AXIS_IN_PER_ROT)

StepperMotor motor_x = {
    .STEP_PIN = 18,
    .DIR_PIN = 2,
    .EN_PIN = 6,
    .last_target_position = 0,
    .current_position = 0,
    .target_position = 0,
    .velocity_rps = 0,
    .max_velocity_rps = .5,
    .max_acceleration = 5.0,
    .flipped = false};

StepperMotor motor_y = {
    .STEP_PIN = 16,
    .DIR_PIN = 3,
    .EN_PIN = 7,
    .last_target_position = 0,
    .current_position = 0,
    .target_position = 0,
    .velocity_rps = 0,
    .max_velocity_rps = .5,
    .max_acceleration = 5.0,
    .flipped = false};

void core1_main()
{
    init_uart();

    set_target_position(&motor_x, &motor_y, 0.0, 0.0); // 50.0 * X_AXIS_ROT_PER_UNITS

    // Current time in microseconds
    uint32_t current_time = time_us_32();
    uint32_t last_time = current_time;

    while (current_time - last_time < 3000000)
    {
        current_time = time_us_32();
    }

    while (true)
    {
        // bool left_motor_reached_mid = false;
        // bool right_motor_reached_mid = false;

        // int mid_position_x = (motor_x.target_position - motor_x.last_target_position) / 2 + motor_x.last_target_position;
        // int mid_position_y = (motor_y.target_position - motor_y.last_target_position) / 2 + motor_y.last_target_position;

        // bool direction_x = (motor_x.target_position - motor_x.last_target_position) > 0;
        // bool direction_y = (motor_y.target_position - motor_y.last_target_position) > 0;

        // // While both motors have not gone beyond halfway point
        // while (!left_motor_reached_mid || !right_motor_reached_mid)
        // {
        //     if (motor_x.current_position >= mid_position_x && direction_x)
        //     {
        //         left_motor_reached_mid = true;
        //     }
        //     else if (motor_x.current_position <= mid_position_x && !direction_x)
        //     {
        //         left_motor_reached_mid = true;
        //     }

        //     if (motor_y.current_position >= mid_position_y && direction_y)
        //     {
        //         right_motor_reached_mid = true;
        //     }
        //     else if (motor_y.current_position <= mid_position_y && !direction_y)
        //     {
        //         right_motor_reached_mid = true;
        //     }
        // }

        while (motor_x.current_position != motor_x.target_position || motor_y.current_position != motor_y.target_position)
        {
        }

        float x, y;

        // When the motor hits its target position, it's ready to receive a new target
        printf("READYREADYREADYREADY\n");

        bool target = receive_target_position(&x, &y);

        if (target)
        {
            // printf("Target position: (%f, %f)\n", x, y);
            set_target_position(&motor_x, &motor_y, x, y);
        }
    }
}

// Main (runs on core 0)
int main()
{
    stdio_init_all();

    // Init pins for both stepper motors
    StepperMotor *motors[] = {&motor_x, &motor_y};
    for (int i = 0; i < 2; i++)
    {
        StepperMotor *m = motors[i];

        // After some testing, I found that the Stepper motor steps on the
        // falling edge of PUL+, so initialize it high and pulse it low.
        gpio_init(m->STEP_PIN);
        gpio_set_dir(m->STEP_PIN, GPIO_OUT);
        gpio_put(m->STEP_PIN, 1);

        gpio_init(m->DIR_PIN);
        gpio_set_dir(m->DIR_PIN, GPIO_OUT);
        gpio_put(m->DIR_PIN, 0);

        gpio_init(m->EN_PIN);
        gpio_set_dir(m->EN_PIN, GPIO_OUT);
        gpio_put(m->EN_PIN, 1);
    }

    // Turn on LED to indicate that the program has started
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    gpio_put(LED_PIN, 1);

    // start core 1
    multicore_reset_core1();
    multicore_launch_core1(&core1_main);

    // Current time
    uint64_t pulse_width = 5;
    uint64_t pulse_delay = 600;

    bool pulse_high = false;

    while (true)
    {
        if (pulse_high)
        {
            for (int i = 0; i < 2; i++)
            {
                StepperMotor *m = motors[i];

                gpio_put(m->STEP_PIN, 0); // Set step pin low

                m->current_position += m->step_direction; // Update the current position
            }

            pulse_high = false;
            sleep_us(pulse_delay); // Wait for the pulse width
        }
        else
        {
            for (int i = 0; i < 2; i++)
            {
                StepperMotor *m = motors[i];

                if (m->current_position < m->target_position)
                {
                    gpio_put(m->DIR_PIN, m->flipped ? 0 : 1); // Set direction pin high
                    m->step_direction = 1;                    // Set step direction to CCW

                    gpio_put(m->STEP_PIN, 1); // Set step pin high
                }
                else if (m->current_position > m->target_position)
                {
                    gpio_put(m->DIR_PIN, m->flipped ? 1 : 0); // Set direction pin low
                    m->step_direction = -1;                   // Set step direction to CW

                    gpio_put(m->STEP_PIN, 1); // Set step pin high
                }
                else
                {
                    m->step_direction = 0;    // Stop stepping
                    gpio_put(m->STEP_PIN, 0); // Set step pin high
                }
            }

            pulse_high = true;
            sleep_us(pulse_width); // Wait for the pulse delay
        }
    }
}
