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
from kivy.metrics import dp, sp

from ballsort.logic import BallSortLogic
from ballsort.colors import generate_kivy_colors
from ballsort.ui.tube_widget import TubeWidget
from ballsort.ui.widgets import ModernButton

class GameLayout(FloatLayout):
    def __init__(self, save_file=None, **kwargs):
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
        
        # Initialize Logic (which handles file fetching invisibly if it exists)
        self.logic = BallSortLogic(num_colors=5, tube_height=4, num_empty_tubes=2, save_file=save_file)
        self.colors_list = generate_kivy_colors(self.logic.num_colors)
        
        self.selected_tube_idx = None
        self.animating = False
        self.active_animations = []
        self._pending_anim_moves = []
        
        # --- Top Menu Row ---
        top_bar = BoxLayout(size_hint_y=0.1, padding=[dp(10), dp(10), dp(10), dp(5)], spacing=dp(10))
        
        top_bar.add_widget(Label(text="Colors:", size_hint_x=0.2, font_size="14sp", bold=True))
        
        self.difficulty_spinner = Spinner(
            text=str(self.logic.num_colors),
            values=tuple(str(i) for i in range(3, 21)),
            size_hint_x=0.18,
            background_normal='', background_color=[0.15, 0.15, 0.2, 1],
            color=[0.8, 0.8, 0.8, 1], font_name='Roboto', font_size="15sp"
        )
        self.difficulty_spinner.bind(text=self.on_difficulty_change)
        top_bar.add_widget(self.difficulty_spinner)
        
        top_bar.add_widget(Label(text="Height:", size_hint_x=0.18, font_size="14sp", bold=True))
        
        self.height_spinner = Spinner(
            text=str(self.logic.tube_height),
            values=tuple(str(i) for i in range(4, 11)),
            size_hint_x=0.18,
            background_normal='', background_color=[0.15, 0.15, 0.2, 1],
            color=[0.8, 0.8, 0.8, 1], font_name='Roboto', font_size="15sp"
        )
        self.height_spinner.bind(text=self.on_difficulty_change)
        top_bar.add_widget(self.height_spinner)
        
        btn_undo = ModernButton(text="Undo", font_size="12sp", bg_color=[0.25, 0.45, 0.8, 1], bg_color_down=[0.15, 0.35, 0.65, 1], size_hint_x=0.13)
        btn_undo.bind(on_release=self.on_undo)
        top_bar.add_widget(btn_undo)
        
        btn_cheat = ModernButton(text="+Tube", font_size="12sp", bg_color=[0.8, 0.3, 0.4, 1], bg_color_down=[0.6, 0.2, 0.3, 1], size_hint_x=0.13)
        btn_cheat.bind(on_release=self.on_add_tube)
        top_bar.add_widget(btn_cheat)
        
        self.main_box.add_widget(top_bar)
        
        # --- Secondary Utility Toolbar ---
        tools_bar = BoxLayout(size_hint_y=0.1, padding=[dp(15), dp(5), dp(15), dp(5)], spacing=dp(15))
        
        btn_reset = ModernButton(text="Reset Level", font_size="18sp", bg_color=[0.8, 0.6, 0.2, 1], bg_color_down=[0.7, 0.5, 0.1, 1], size_hint_x=0.5)
        btn_reset.bind(on_release=self.on_reset_level)
        tools_bar.add_widget(btn_reset)
        
        btn_new = ModernButton(text="New Game", font_size="18sp", bg_color=[0.2, 0.7, 0.4, 1], bg_color_down=[0.15, 0.5, 0.3, 1], size_hint_x=0.5)
        btn_new.bind(on_release=self.on_new_game)
        tools_bar.add_widget(btn_new)
        
        self.main_box.add_widget(tools_bar)
        
        # --- Notification/Win Label ---
        self.status_label = Label(text="", font_size="28sp", bold=True, color=[1, 0.8, 0.2, 1], size_hint_y=0.08)
        self.main_box.add_widget(self.status_label)
        
        # Dynamic Grid Container
        self.grid = GridLayout(rows=1, spacing=dp(10), padding=dp(15))
        self.main_box.add_widget(self.grid)
        
        # Next Level Overlay Button
        self.next_level_btn = ModernButton(
            text="Next Level", font_size="28sp", 
            bg_color=[0.2, 0.8, 0.2, 1], bg_color_down=[0.15, 0.6, 0.15, 1],
            size_hint=(0.6, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.next_level_btn.bind(on_release=self.on_new_game)
        self.next_level_btn.opacity = 0
        self.next_level_btn.disabled = True
        self.add_widget(self.next_level_btn)
        
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
            
        max_cols_by_width = max(4, int(Window.width / dp(80)))
        
        if num_tubes <= max_cols_by_width:
            self.grid.cols = num_tubes
            self.grid.rows = 1
        else:
            rows = math.ceil(num_tubes / max_cols_by_width)
            self.grid.cols = math.ceil(num_tubes / rows)
            self.grid.rows = rows

    def force_finish_animations(self):
        if not self.animating: return
        for anim, dummy in self.active_animations:
            anim.cancel(dummy)
            self.remove_widget(dummy)
        for dst_idx, color_idx, count in self._pending_anim_moves:
            for _ in range(count):
                self.logic.board[dst_idx].append(color_idx)
        self.active_animations.clear()
        self._pending_anim_moves.clear()
        self.animating = False
        self.refresh_ui()

    def on_difficulty_change(self, *args):
        num_colors = int(self.difficulty_spinner.text)
        tube_height = int(self.height_spinner.text)
        
        if num_colors != self.logic.num_colors or tube_height != self.logic.tube_height:
            self.logic.num_colors = num_colors
            self.logic.tube_height = tube_height
            self.logic.generate_level() # Triggers the save_state functionality autonomously
            
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
            self.next_level_btn.opacity = 1
            self.next_level_btn.disabled = False
        else:
            self.status_label.text = ""
            self.next_level_btn.opacity = 0
            self.next_level_btn.disabled = True

    def on_tube_tap(self, tube_idx):
        if self.logic.is_win():
            return
            
        if self.animating:
            self.force_finish_animations()
            
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
        if self.animating:
            self.force_finish_animations()
            
        self.animating = True
        self.active_animations = []
        self._pending_anim_moves = []
        
        src_tube = self.logic.board[src_idx]
        dst_tube = self.logic.board[dst_idx]
        color_idx = src_tube[-1]
        
        # Calculate exactly how many matched consecutive balls exist, and how much headroom the target has
        identical_count = 0
        for c in reversed(src_tube):
            if c == color_idx:
                identical_count += 1
            else:
                break
                
        space_left = self.logic.tube_height - len(dst_tube)
        balls_to_move = min(identical_count, space_left)
        
        src_tube_widget = self.tube_widgets[src_idx]
        dst_tube_widget = self.tube_widgets[dst_idx]
        color = self.colors_list[color_idx]
        
        dummies = []
        for i in range(balls_to_move):
            src_ball_idx = len(src_tube) - balls_to_move + i
            is_top_ball = (src_ball_idx == len(src_tube) - 1)
            start_x, start_y, diam_start = src_tube_widget.get_ball_rect(src_ball_idx, is_top_ball)
            
            dst_ball_idx = len(dst_tube) + i
            end_x, end_y, diam_end = dst_tube_widget.get_ball_rect(dst_ball_idx, False)
            
            dummy = Widget(size_hint=(None, None), size=(diam_start, diam_start), pos=(start_x, start_y))
            
            def dummy_update(w, *args):
                w.canvas.clear()
                with w.canvas:
                    Color(*color)
                    Ellipse(pos=w.pos, size=w.size)
                    Color(1, 1, 1, 0.6)
                    Ellipse(pos=(w.x + w.width*0.18, w.y + w.height*0.52), size=(w.width*0.35, w.height*0.35))
                    
            dummy.bind(pos=dummy_update, size=dummy_update)
            dummy_update(dummy) 
            
            dummies.append((dummy, end_x, end_y, diam_end))
        
        self.logic.history.append(copy.deepcopy(self.logic.board))
        
        # Pop logical source structure gracefully
        for _ in range(balls_to_move):
            self.logic.board[src_idx].pop()
            
        self.selected_tube_idx = None
        self.refresh_ui()
        
        self._pending_anim_moves.append((dst_idx, color_idx, balls_to_move))
        
        self.active_anims = balls_to_move
        
        for dummy, end_x, end_y, diam_end in dummies:
            self.add_widget(dummy)
            
            anim = Animation(x=end_x, y=end_y, width=diam_end, height=diam_end, duration=0.18, t='out_quad')
            self.active_animations.append((anim, dummy))
            
            def create_callback(d):
                def on_anim_complete(a, widget):
                    if not self.animating: return
                    self.remove_widget(d)
                    self.active_anims -= 1
                    if self.active_anims == 0:
                        for dst, c_idx, count in self._pending_anim_moves:
                            for _ in range(count):
                                self.logic.board[dst].append(c_idx)
                        self._pending_anim_moves.clear()
                        self.active_animations.clear()
                        self.animating = False
                        self.refresh_ui()
                return on_anim_complete
                
            anim.bind(on_complete=create_callback(dummy))
            anim.start(dummy)

    def on_undo(self, instance):
        self.force_finish_animations()
        if self.logic.undo():
            self.selected_tube_idx = None
            self.build_board()

    def on_add_tube(self, instance):
        self.force_finish_animations()
        self.logic.add_empty_tube()
        self.build_board()
            
    def on_reset_level(self, instance):
        self.force_finish_animations()
        self.logic.reset_level()
        self.selected_tube_idx = None
        self.build_board()
            
    def on_new_game(self, instance):
        self.force_finish_animations()
        self.logic.generate_level()
        self.selected_tube_idx = None
        self.build_board()
