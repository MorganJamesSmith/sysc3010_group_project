#! /usr/bin/env python3


import sys
sys.path.append("../../hardware")

import smbus
from mlx90614 import MLX90614

# Get SMBus object
try:
    bus = smbus.SMBus(1)
except:
    print("Failed to get bus object.", file = sys.stderr)
    sys.exit(1)

# Create sensor driver object
s = MLX90614(bus)

#
# Test 1: ambient temperature sanity
#
a_temp = s.get_ambient_temp()
print(f"Ambient temperature: {a_temp:.2f} °C")

if a_temp == None or a_temp < 10.0 or a_temp > 30.0:
    print("Ambient temperature looks fishy!", file = sys.stderr)
    sys.exit(1)

print("Looks good!\n")

#
# Test 2: raise ambient temp
#
input("Please hold sensor to raise its temperature. Press enter to continue...")

new_a_temp = s.get_ambient_temp()
print(f"Ambient temperature: {new_a_temp:.2f} °C")

if new_a_temp == None or a_temp < 10.0 or a_temp > 30.0:
    print("Ambient temperature looks fishy!", file = sys.stderr)
    sys.exit(1)
elif new_a_temp <= a_temp:
    print("Ambient temperature did not rise. Please run test again.", file = sys.stderr)
    sys.exit(1)

print("Looks good!\n")

#
# Test 3: Measure IR temperature
#
ir_temp = s.get_ir_temp()
print(f"IR temperature: {ir_temp:.2f} °C")

# Should be somewhere around the ambient temp, usually higher
if ir_temp == None or ir_temp < 10.0 or ir_temp > 35.0:
    print("IR temperature looks fishy!", file = sys.stderr)
    sys.exit(1)

print("Looks good!\n")

#
# Test 4: Measure hand temperature
#
input("Please place hand in front of sensor. Press enter to continue...")

hand_ir_temp = s.get_ir_temp()
print(f"IR temperature: {hand_ir_temp:.2f} °C")

if hand_ir_temp == None or hand_ir_temp < 10.0 or hand_ir_temp > 35.0:
    print("IR temperature looks fishy!", file = sys.stderr)
    sys.exit(1)
elif hand_ir_temp <= ir_temp:
    print("IR temperature did not rise. Please run test again.", file = sys.stderr)
    sys.exit(1)

print("Looks good!\n")

#
# Test 5: Measure forehead temp
#
input("Please place forehead in front of sensor. Press enter to continue...")

head_ir_temp = s.get_ir_temp()
print(f"IR temperature: {head_ir_temp:.2f} °C")

if head_ir_temp == None or head_ir_temp < 10.0 or head_ir_temp > 35.0:
    print("IR temperature looks fishy!", file = sys.stderr)
    sys.exit(1)
elif head_ir_temp <= hand_ir_temp:
    print("IR temperature did not rise. Please run test again.", file = sys.stderr)
    sys.exit(1)

print("Looks good!\n")

