import logging
from time import time

from app import session
from app.models import Plane as PlaneModel
from app.plane import Plane


class Task:
    def __init__(self, func, period):
        self.func = func
        self.period = period
        self.since_last = 0

    def __call__(self, *args, **kwargs):
        self.since_last += 1
        if self.since_last >= self.period:
            self.func(*args, **kwargs)
            self.since_last = 0



class World:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.planes = {}
        self.player = {}

        self.tasks = []

        self.load()


    def load(self):
        for plane_model in session.query(PlaneModel).all():
            self.logger.debug(f'Loading plane: {plane_model} ...')
            self.planes[plane_model.id] = Plane(plane_model, self)
        self.add_task(self.logger.debug, 100, '100 ticks have passed')

    def tick(self):
        for task, args, kwargs in self.tasks:
            task(*args, **kwargs)

    def add_task(self, func, period, *args, **kwargs):
        self.tasks.append((Task(func, period), args, kwargs))

    def run(self):
        self.__loop()

    def __loop(self, tick_speed=0.3):
        self.logger.info(f'Starting world loop ({tick_speed} s/tick)...')
        last = time()
        dt = 0.0
        while True:
            current = time()
            dt += current - last
            if dt > tick_speed:
                self.tick()
                dt = 0.0
            last = current
            if time() - last > tick_speed:
                self.logger.warning('Ticks taking longer than tick speed!')