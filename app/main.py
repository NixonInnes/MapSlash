import time

class MainLoop:
    def logic(self, dt):
        print(dt)


    def __call__(self):
        last_time = time.time()
        dt = 0.0
        while True:
            current_time = time.time()
            dt += current_time - last_time
            if dt > 1:
                self.logic(dt)
                dt = 0.0
            last_time = current_time