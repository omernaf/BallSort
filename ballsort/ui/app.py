import os
import traceback
from kivy.app import App
from kivy.uix.label import Label
from ballsort.ui.game_view import GameLayout

class BallSortApp(App):
    def build(self):
        try:
            # Access the cross-platform generic storage root assigned gracefully by Kivy Application instance
            save_file = os.path.join(self.user_data_dir, 'ballsort_save.json')
            return GameLayout(save_file=save_file)
        except Exception:
            err = traceback.format_exc()
            return Label(text=err, font_size='12sp', text_size=(None, None))
