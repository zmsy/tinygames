import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Bear Bucket")
        pyxel.run(self.update, self.draw)

    def update(self):
        # Game logic goes here
        pass

    def draw(self):
        pyxel.cls(0)
        pyxel.text(50, 60, "Hello, Pyxel!", 7)


App()
