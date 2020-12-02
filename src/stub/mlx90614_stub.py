from time import sleep

class MLX90614_stub:
    def __init__(self, bus):
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

class MLX90614_Interactive_stub:
    def __init__(self, bus):
        pass

    @staticmethod
    def get_temp(name):
        print(f"MLX90614 Stub - {name} temp")
        while True:
            try:
                temp_value = float(input(f"{name} temp in °C: "))
            except ValueError:
                print("Invalid temperature.")
                continue
            else:
                return temp_value

    def get_ambient_temp(self):
        return MLX90614_Interactive_stub.get_temp("Ambient")

    def get_ir_temp(self):
        return MLX90614_Interactive_stub.get_temp("IR")
