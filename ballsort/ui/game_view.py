import copy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.animation import Animation

from ballsort.logic import BallSortLogic
from ballsort.colors import generate_kivy_colors
from ballsort.ui.tube_widget import TubeWidget

class GameLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        # Dark clean background for high contrast
        with self.canvas.before:
            Color(0.1, 0.1, 0.12, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.logic = BallSortLogic(num_colors=4, tube_height=4, num_empty_tubes=2)
        self.colors_list = generate_kivy_colors(self.logic.num_colors)
        
        self.selected_tube_idx = None
        self.animating = False
        
        # --- UI Header ---
        header = BoxLayout(size_hint_y=0.15, padding=10, spacing=10)
        
        btn_undo = Button(text="Undo", background_color=[0.3, 0.5, 0.8, 1])
        btn_undo.bind(on_release=self.on_undo)
        
        btn_cheat = Button(text="+ Tube", background_color=[0.8, 0.3, 0.3, 1])
        btn_cheat.bind(on_release=self.on_add_tube)
        
        btn_restart = Button(text="Restart", background_color=[0.3, 0.8, 0.3, 1])
        btn_restart.bind(on_release=self.on_restart)
        
        header.add_widget(btn_undo)
        header.add_widget(btn_cheat)
        header.add_widget(btn_restart)
        self.add_widget(header)
        
        # Win Condition Banner
        self.win_label = Label(text="", font_size=32, color=[1, 1, 0, 1], size_hint_y=0.1)
        self.add_widget(self.win_label)
        
        # Automatic responsive tube container
        self.grid = GridLayout(rows=1, spacing=10, padding=20)
        self.add_widget(self.grid)
        
        self.build_board()

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def build_board(self):
        self.grid.clear_widgets()
        
        # Basic responsiveness: Wrap rows if user clicks +tube too many times
        if len(self.logic.board) > 6:
            self.grid.rows = 2
        else:
            self.grid.rows = 1
            
        self.tube_widgets = []
        for i in range(len(self.logic.board)):
            tw = TubeWidget(i, self.logic, self.colors_list, self.on_tube_tap)
            self.grid.add_widget(tw)
            self.tube_widgets.append(tw)
            
        self.refresh_ui()

    def refresh_ui(self):
        for tw in self.tube_widgets:
            tw.is_selected = (tw.tube_idx == self.selected_tube_idx)
            tw.update_canvas()
            
        if self.logic.is_win():
            self.win_label.text = "YOU WIN! Tap Restart"
        else:
            self.win_label.text = ""

    def on_tube_tap(self, tube_idx):
        if self.animating or self.logic.is_win():
            return
            
        # Tap 1: Select source
        if self.selected_tube_idx is None:
            if len(self.logic.board[tube_idx]) > 0:
                self.selected_tube_idx = tube_idx
                self.refresh_ui()
        else:
            # Tap 2: Attempt Move
            src_idx = self.selected_tube_idx
            dst_idx = tube_idx
            
            if src_idx == dst_idx:
                self.selected_tube_idx = None
                self.refresh_ui()
                return
                
            if self.logic.can_move(src_idx, dst_idx):
                self.animate_move(src_idx, dst_idx)
            else:
                self.selected_tube_idx = None
                self.refresh_ui()

    def animate_move(self, src_idx, dst_idx):
        self.animating = True
        
        src_tube_widget = self.tube_widgets[src_idx]
        dst_tube_widget = self.tube_widgets[dst_idx]
        
        ball_color_idx = self.logic.board[src_idx][-1]
        color = self.colors_list[ball_color_idx]
        
        tube_w = min(src_tube_widget.width * 0.8, 80)
        ball_radius = tube_w * 0.4
        ball_diameter = ball_radius * 2
        tube_h = src_tube_widget.height * 0.7
        
        # Compute exact positions for the ball animation
        start_x = src_tube_widget.center_x - ball_radius
        start_y = (src_tube_widget.y + src_tube_widget.height * 0.05 + 
                   (tube_w * 0.1) + 
                   ((len(self.logic.board[src_idx]) - 1) * ((tube_h - tube_w*0.1) / self.logic.tube_height)) + 
                   (tube_h * 0.3))
                   
        end_x = dst_tube_widget.center_x - ball_radius
        end_y = (dst_tube_widget.y + dst_tube_widget.height * 0.05 + 
                 (tube_w * 0.1) + 
                 (len(self.logic.board[dst_idx]) * ((tube_h - tube_w*0.1) / self.logic.tube_height)))
        
        # Instantiate temporary floating ball
        dummy = Widget(size_hint=(None, None), size=(ball_diameter, ball_diameter), pos=(start_x, start_y))
        with dummy.canvas:
            Color(*color)
            Ellipse(pos=(0, 0), size=(ball_diameter, ball_diameter))
            
        def dummy_update(w, *args):
            w.canvas.clear()
            with w.canvas:
                Color(*color)
                Ellipse(pos=w.pos, size=w.size)
        dummy.bind(pos=dummy_update)
        
        # Properly structure state so Undo ignores halfway-animation glitches
        self.logic.history.append(copy.deepcopy(self.logic.board))
        ball_val = self.logic.board[src_idx].pop()
        self.selected_tube_idx = None
        self.refresh_ui()
        
        self.add_widget(dummy)
        
        anim = Animation(x=end_x, y=end_y, duration=0.25, t='out_quad')
        def on_anim_complete(*args):
            self.remove_widget(dummy)
            self.logic.board[dst_idx].append(ball_val)
            self.animating = False
            self.refresh_ui()
            
        anim.bind(on_complete=on_anim_complete)
        anim.start(dummy)

    def on_undo(self, instance):
        if not self.animating:
            if self.logic.undo():
                self.selected_tube_idx = None
                self.build_board()

    def on_add_tube(self, instance):
        if not self.animating:
            self.logic.add_empty_tube()
            self.build_board()
            
    def on_restart(self, instance):
        if not self.animating:
            self.logic.generate_level()
            self.selected_tube_idx = None
            self.build_board()
