
import sys
class MLX90614_stub:

    def __init__(self):
        try:
            with open("ambient_temperature.txt", "r") as ambient_temp_file:
                self.ambient_temp = ambient_temp_file.read().strip()
            with open("ir_temperature.txt", "r") as ir_temp_file:
                self.ir_temp = ir_temp_file.read().strip()
        except FileNotFoundError as e:
            print("Could not open testcase files.")
            exit(1)
    
    def get_ambient_temp(self):
        amb_temperature = int(self.ambient_temp)
        print(ir_temperature)
        return amb_temperature
    def get_ir_temp(self):
        ir_temperature = int(self.ir_temp)
        print(ir_temperature)
        return ir_temperature
