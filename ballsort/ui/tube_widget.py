import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, RoundedRectangle

class TubeWidget(Widget):
    def __init__(self, tube_idx, logic, colors_list, on_tap_callback, **kwargs):
        super().__init__(**kwargs)
        self.tube_idx = tube_idx
        self.logic = logic
        self.colors_list = colors_list
        self.on_tap_callback = on_tap_callback
        self.is_selected = False
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def get_layout_params(self):
        capacity = self.logic.tube_height
        available_w = self.width * 0.9
        available_h = self.height * 0.95
        
        # Maintain a mathematically sound aspect ratio scaling.
        # Height is composed of: bottom padding (0.15), capacity layers (0.85 per ball), top jump headroom (0.8)
        ideal_h_ratio = 0.15 + (capacity * 0.85) + 0.8
        
        if available_w <= 0 or available_h <= 0:
            return self.center_x, self.y, 10, 10
            
        if available_h / available_w < ideal_h_ratio:
            tube_h = available_h
            tube_w = tube_h / ideal_h_ratio
        else:
            tube_w = available_w
            tube_h = tube_w * ideal_h_ratio
            
        # Absolute soft-cap for insanely large screens
        if tube_w > 90:
            tube_w = 90
            tube_h = tube_w * ideal_h_ratio

        tube_x = self.center_x - tube_w / 2
        tube_y = self.y + (self.height - tube_h) / 2
        return tube_x, tube_y, tube_w, tube_h

    def get_ball_rect(self, index, is_popped_up):
        tube_x, tube_y, tube_w, tube_h = self.get_layout_params()
        ball_diameter = tube_w * 0.8
        ball_radius = ball_diameter / 2
        bottom_padding = tube_w * 0.15
        step_y = tube_w * 0.85 
        
        bx = tube_x + tube_w / 2 - ball_radius
        by = tube_y + bottom_padding + (index * step_y)
        if is_popped_up:
            by += (tube_w * 0.8) # Elevate significantly over the top rim
            
        return bx, by, ball_diameter

    def update_canvas(self, *args):
        self.canvas.clear()
        
        tube_data = self.logic.board[self.tube_idx]
        tube_x, tube_y, tube_w, tube_h = self.get_layout_params()
        
        with self.canvas:
            # Glossy Glass Tube Background
            if self.is_selected:
                Color(0.2, 0.4, 0.7, 0.3)
            else:
                Color(0.8, 0.8, 0.9, 0.1)
                
            tube_radius = tube_w * 0.25
            RoundedRectangle(pos=(tube_x, tube_y), size=(tube_w, tube_h), radius=[0, 0, tube_radius, tube_radius])
            
            # Rendering Balls natively
            for i, ball_color_idx in enumerate(tube_data):
                color = self.colors_list[ball_color_idx]
                is_popped = self.is_selected and i == len(tube_data) - 1
                bx, by, ball_diameter = self.get_ball_rect(i, is_popped)
                
                # Base Color Sphere
                Color(*color)
                Ellipse(pos=(bx, by), size=(ball_diameter, ball_diameter))
                
                # Glossy reflection (top offset)
                Color(1, 1, 1, 0.6)
                refl_size = ball_diameter * 0.35
                Ellipse(pos=(bx + ball_diameter*0.18, by + ball_diameter*0.52), size=(refl_size, refl_size))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_tap_callback(self.tube_idx)
            return True
        return super().on_touch_down(touch)
