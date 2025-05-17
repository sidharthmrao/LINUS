#pragma once

#include "pico/stdlib.h"
#include "hardware/uart.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#define UART_BAUD_RATE 115200
#define UART_TX_PIN 0
#define UART_RX_PIN 1

void init_uart()
{
    // Initialize UART
    uart_init(uart0, UART_BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
}

// Make buffer of size 64
char buf[64];

bool receive_target_position(float *x, float *y)
{
    // Wait for "("
    while (uart_getc(uart0) != '(')
    {
        // printf("Waiting for '('\n");
    }

    // Clear buffer
    memset(buf, 0, sizeof(buf));

    int size = 0;

    // printf("Receiving target position: ");

    char c = uart_getc(uart0);

    while (c != ')')
    {
        buf[size] = c;
        size++;
        c = uart_getc(uart0);
    }

    buf[size] = '\0'; // Null-terminate the string

    // Print buffer
    size = 0;
    while (buf[size] != '\0')
    {
        // printf("%c", buf[size]);
        size++;
    }

    // printf("\n");

    float x_, y_;

    if (sscanf(buf, "%f,%f", &x_, &y_) != 2)
    {
        printf("Failed to parse coordinates\n");
        return false;
    }

    // Save to floats
    *x = x_;
    *y = y_;

    return true;
}
