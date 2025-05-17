import serial
import time

# A list of test commands to send to the pico.
# This will eventually get replaced by a list of points that
# make some icon
pos_list = [
  (1.0, 1.0),
  (4.0, 4.0),
  (1.0, 1.0),
  (4.0, 4.0)
]

pos_list = []

for i in range(800):
    pos_list.append((i/100.0, i/100.0))

def initialize(port):
    # If connection doesn't work, just try again until it does
    while True:
        try:
            # Initialize a UART connect and give it a moment to establish
            ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(2)
            print("Serial port opened.")
            return ser
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            time.sleep(2)

def send_floats(ser, val1: float, val2: float):
    msg = f"({val1},{val2})\n"
    ser.write(msg.encode('utf-8'))
    print(f"Sent: {msg.strip()}")

def send_path(ser, port, pos_list):
    curr = 0
    
    try:
        while True:
            try:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"Received: {line}")
                        if "READY" in line:
                            if curr < len(pos_list):
                                send_floats(ser, pos_list[curr][0], pos_list[curr][1])
                                curr += 1
                            else:
                                print("All positions sent.")
                                return
            except (serial.SerialException, OSError) as e:
                print(f"Serial Error: {e}. Reinitializing...")
                try:
                    ser.close()
                except:
                    pass
                initialize(port)
            time.sleep(0.01)  # small delay to reduce CPU usage

    except KeyboardInterrupt:
        if ser:
            ser.close()
        print("UART closed.")

