from time import sleep

class MLX90614_stub:
    def __init__(self):
        try:
            self.ambient_temp_file = open("./stub_text/ambient_temperature.txt", "r")
            self.ir_temp_file = open("./stub_text/ir_temperature.txt", "r")
        except FileNotFoundError as e:
            print("Could not open test files for IR temperature sensor.")
            exit(1)
    
    def get_ambient_temp(self):
        while True:
            line = self.ambient_temp_file.readline().strip()
            if line != '':
                break
            sleep(2)
        return float(line)
    
    def get_ir_temp(self):
        while True:
            line = self.ir_temp_file.readline().strip()
            if line != '':
                break
            sleep(2)
        return float(line)
