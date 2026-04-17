from kivy.app import App
from ballsort.ui.game_view import GameLayout

class BallSortApp(App):
    def build(self):
        return GameLayout()
