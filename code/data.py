class Data:
    def __init__(self, ui):
        self.ui = ui
        self._coins = 0
        self._health = 100   # _ stands for private, just for convencion
        self.ui.create_hearts(self._health)
        self.level_number = 1
        self.next_level = False

    @property               # Decorator
    def coins(self):
        return self._coins
    
    @coins.setter
    def coins(self, value):
        self._coins = value
        self.ui.show_coins(self.coins)

    @property               # Decorator
    def health(self):
        return self._health
    
    @health.setter
    def health(self, value):
        self._health = value
        self.ui.create_hearts(value)
