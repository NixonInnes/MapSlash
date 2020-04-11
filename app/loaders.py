

class ModelLoader:
    attributes = []
    base = None

    def __init__(self, model):
        self.preload()
        self.load(model)
        self.postload()

    def load(self, model):
        if not isinstance(model, self.base):
            self.logger.error(f'Attempted to load incorrect model: {model}')
        else:
            for attribute in self.attributes:
                setattr(self, attribute, getattr(model, attribute))
            self.base = model
            self.logger.debug(f'Loaded: {model}')

