from app.loaders import ModelLoader
from app.models import Mob as MobModel

class Mob(ModelLoader):
    base_model = MobModel
    attributes = ['hp', 'mn', 'str', 'int', 'wis', 'dex', 'cha', 'lck', 'abilities']

    def postload(self)
        self.in_combat = False


    def move(self, tile):
        if self.tile:
            self.tile.leave(self)

        try:
            tile.enter(self)
            self.tile = room
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f'{self} unable to enter {room}')