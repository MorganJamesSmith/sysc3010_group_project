
import sys
class MLX90614_stub:

    def __init__(self):
        try:
            with open("./stub_text/ambient_temperature.txt", "r") as ambient_temp_file:
                self.ambient_temp = ambient_temp_file.read().strip()
            with open("./stub_text/ir_temperature.txt", "r") as ir_temp_file:
                self.ir_temp = ir_temp_file.read().strip()
        except FileNotFoundError as e:
            print("Could not open testcase files.")
            exit(1)
    
    def get_ambient_temp(self):
        amb_temperature = float(self.ambient_temp)
        print(amb_temperature)
        return amb_temperature
    def get_ir_temp(self):
        ir_temperature = float(self.ir_temp)
        print(ir_temperature)
        return ir_temperature
