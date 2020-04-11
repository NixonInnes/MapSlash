from app import config
from app.models import Compass

class LazyTileLoader:
    def __init__(self, attr):
        self.attr = attr
        self.value = None

    def __set__(self, instance, value):
        self.value = value

    def __get__(self, instance, owner):
        print(type(instance.model))
        if not self.value:
            model = getattr(instance.model, self.attr)

            if not model:
                return

            if model.id in instance.plane.tiles:
                self.value = instance.plane.tiles[model.id]
            else:
                self.value = instance.plane.load_tile(model)
        return self.value


def Tile(*args, **kwargs):
    class Tile:
        attributes = ['id']


        def __init__(self, model, plane):
            self.model = model
            self.plane = plane
            self.load()

        def load(self):
            for attribute in self.attributes:
                setattr(self, attribute, getattr(self.model, attribute))

    Tile.attributes += list(config['tile_properties'].keys())

    for direction in Compass:
        setattr(Tile, direction, LazyTileLoader(direction))

    return Tile(*args, **kwargs)





