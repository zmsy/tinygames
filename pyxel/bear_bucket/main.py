import pyxel


class Const:
    SCREEN_WIDTH = 240
    SCREEN_HEIGHT = 120


class App:
    def __init__(self):
        pyxel.init(Const.SCREEN_WIDTH, Const.SCREEN_HEIGHT, title="Bear Bucket")
        pyxel.run(self.update, self.draw)

        # load custom color palette
        pyxel.load("palette.pyxpal")

    def update(self):
        # Game logic goes here
        pass

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 30, 15)
        pyxel.text(50, 60, "Hello, Pyxel!", 7)


App()
