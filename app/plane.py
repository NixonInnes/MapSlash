import logging

from app.tile import Tile

class Plane:
    attributes = ['id', 'name']

    def __init__(self, model, world):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = model
        self.Base = type(model)
        self.world = world
        self.load()
        self.postload()

    def load(self):
        for attribute in self.attributes:
            setattr(self, attribute, getattr(self.model, attribute))

    def postload(self):
        self.tiles = {}

    def get(self, id):
        return self.tiles.get(id)

    def load_tile(self, model):
        new_tile = Tile(model, self)
        self.tiles[new_tile.model.id] = new_tile
        return new_tile

    def unload_tile(self, id):
        tile = self.tiles.get(id)
        if not tile:
            self.logger.warn(f'Attempted to unload a tile which isn\'t loaded: {tile}')
        else:
            del self.tiles[id]






