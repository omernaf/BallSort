import os
from kivy.app import App
from ballsort.ui.game_view import GameLayout

class BallSortApp(App):
    def build(self):
        # Access the cross-platform generic storage root assigned gracefully by Kivy Application instance
        save_file = os.path.join(self.user_data_dir, 'ballsort_save.json')
        return GameLayout(save_file=save_file)
