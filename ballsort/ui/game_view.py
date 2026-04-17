import copy
import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.animation import Animation
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

from ballsort.logic import BallSortLogic
from ballsort.colors import generate_kivy_colors
from ballsort.ui.tube_widget import TubeWidget
from ballsort.ui.widgets import ModernButton

class GameLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Deep Dark Background
        with self.canvas.before:
            Color(0.08, 0.08, 0.11, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        Window.bind(on_resize=self.on_window_resize)
        
        # Create an absolute main container that doesn't stretch when siblings are added
        self.main_box = BoxLayout(orientation='vertical', size_hint=(1, 1), pos_hint={'x': 0, 'y': 0})
        self.add_widget(self.main_box)
        
        self.logic = BallSortLogic(num_colors=5, tube_height=4, num_empty_tubes=2)
        self.colors_list = generate_kivy_colors(self.logic.num_colors)
        
        self.selected_tube_idx = None
        self.animating = False
        
        # --- Top Menu Row ---
        top_bar = BoxLayout(size_hint_y=0.1, padding=[20, 15, 20, 5], spacing=10)
        
        top_bar.add_widget(Label(text="Colors:", size_hint_x=None, width=60, font_size="16sp", bold=True))
        
        self.difficulty_spinner = Spinner(
            text=str(self.logic.num_colors),
            values=tuple(str(i) for i in range(3, 21)),
            size_hint_x=None, width=60,
            background_normal='', background_color=[0.15, 0.15, 0.2, 1],
            color=[0.8, 0.8, 0.8, 1], font_name='Roboto'
        )
        self.difficulty_spinner.bind(text=self.on_difficulty_change)
        top_bar.add_widget(self.difficulty_spinner)
        
        top_bar.add_widget(Label(text="Height:", size_hint_x=None, width=60, font_size="16sp", bold=True))
        
        self.height_spinner = Spinner(
            text=str(self.logic.tube_height),
            values=tuple(str(i) for i in range(4, 11)),
            size_hint_x=None, width=60,
            background_normal='', background_color=[0.15, 0.15, 0.2, 1],
            color=[0.8, 0.8, 0.8, 1], font_name='Roboto'
        )
        self.height_spinner.bind(text=self.on_difficulty_change)
        top_bar.add_widget(self.height_spinner)
        
        top_bar.add_widget(Widget())
        
        btn_restart = ModernButton(text="New", bg_color=[0.2, 0.7, 0.4, 1], bg_color_down=[0.15, 0.5, 0.3, 1], size_hint_x=None, width=100)
        btn_restart.bind(on_release=self.on_restart)
        top_bar.add_widget(btn_restart)
        
        self.main_box.add_widget(top_bar)
        
        # --- Secondary Utility Toolbar ---
        tools_bar = BoxLayout(size_hint_y=0.1, padding=[20, 5, 20, 15], spacing=15)
        
        btn_undo = ModernButton(text="Undo", bg_color=[0.25, 0.45, 0.8, 1], bg_color_down=[0.15, 0.35, 0.65, 1])
        btn_undo.bind(on_release=self.on_undo)
        tools_bar.add_widget(btn_undo)
        
        btn_cheat = ModernButton(text="+ Empty Tube", bg_color=[0.8, 0.3, 0.4, 1], bg_color_down=[0.6, 0.2, 0.3, 1])
        btn_cheat.bind(on_release=self.on_add_tube)
        tools_bar.add_widget(btn_cheat)
        
        self.main_box.add_widget(tools_bar)
        
        # --- Notification/Win Label ---
        self.status_label = Label(text="", font_size="28sp", bold=True, color=[1, 0.8, 0.2, 1], size_hint_y=0.08)
        self.main_box.add_widget(self.status_label)
        
        # Dynamic Grid Container
        self.grid = GridLayout(rows=1, spacing=10, padding=20)
        self.main_box.add_widget(self.grid)
        
        self.build_board()

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        
    def on_window_resize(self, window, width, height):
        self.reflow_grid()

    def reflow_grid(self):
        num_tubes = len(self.logic.board)
        if num_tubes == 0: 
            return
            
        max_cols_by_width = max(3, int(Window.width / 90))
        
        if num_tubes <= max_cols_by_width:
            self.grid.cols = num_tubes
            self.grid.rows = 1
        else:
            rows = math.ceil(num_tubes / max_cols_by_width)
            self.grid.cols = math.ceil(num_tubes / rows)
            self.grid.rows = rows

    def on_difficulty_change(self, *args):
        num_colors = int(self.difficulty_spinner.text)
        tube_height = int(self.height_spinner.text)
        self.logic = BallSortLogic(num_colors=num_colors, tube_height=tube_height, num_empty_tubes=2)
        self.colors_list = generate_kivy_colors(self.logic.num_colors)
        self.selected_tube_idx = None
        self.build_board()

    def build_board(self):
        self.grid.clear_widgets()
        self.reflow_grid()
            
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
            self.status_label.text = "YOU WIN! 🎉"
        else:
            self.status_label.text = ""

    def on_tube_tap(self, tube_idx):
        if self.animating or self.logic.is_win():
            return
            
        if self.selected_tube_idx is None:
            if len(self.logic.board[tube_idx]) > 0:
                self.selected_tube_idx = tube_idx
                self.refresh_ui()
        else:
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
        
        start_x, start_y, diam_start = src_tube_widget.get_ball_rect(len(self.logic.board[src_idx]) - 1, True)
        end_x, end_y, diam_end = dst_tube_widget.get_ball_rect(len(self.logic.board[dst_idx]), False)
        
        dummy = Widget(size_hint=(None, None), size=(diam_start, diam_start), pos=(start_x, start_y))
            
        def dummy_update(w, *args):
            w.canvas.clear()
            with w.canvas:
                Color(*color)
                Ellipse(pos=w.pos, size=w.size)
                Color(1, 1, 1, 0.6)
                Ellipse(pos=(w.x + w.width*0.18, w.y + w.height*0.52), size=(w.width*0.35, w.height*0.35))
        
        dummy.bind(pos=dummy_update, size=dummy_update)
        dummy_update(dummy) # Force draw on frame 0 to prevent (0,0) ghosting
        
        self.logic.history.append(copy.deepcopy(self.logic.board))
        ball_val = self.logic.board[src_idx].pop()
        self.selected_tube_idx = None
        self.refresh_ui()
        
        # Adding dummy to FloatLayout prevents any layout disruptions
        self.add_widget(dummy)
        
        anim = Animation(x=end_x, y=end_y, width=diam_end, height=diam_end, duration=0.22, t='out_quad')
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
