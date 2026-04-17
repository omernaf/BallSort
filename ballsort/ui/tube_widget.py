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
        
    def update_canvas(self, *args):
        self.canvas.clear()
        
        tube_data = self.logic.board[self.tube_idx]
        capacity = self.logic.tube_height
        
        tube_w = min(self.width * 0.75, 85)
        tube_h = self.height * 0.75
        
        tube_x = self.center_x - tube_w / 2
        tube_y = self.y + self.height * 0.05
        
        with self.canvas:
            # Glossy Glass Tube Background
            if self.is_selected:
                # Stronger blue-ish glass when selected
                Color(0.2, 0.4, 0.7, 0.3)
            else:
                # Subtle grey glass
                Color(0.8, 0.8, 0.9, 0.1)
                
            RoundedRectangle(pos=(tube_x, tube_y), size=(tube_w, tube_h), radius=[0, 0, 25, 25])
            
            # Tube outer rim accent
            if self.is_selected:
                Color(0.4, 0.8, 1.0, 0.8)
            else:
                Color(0.6, 0.6, 0.6, 0.3)
                
            # Create a light stroke using a smaller inset radius rect hack, or just a filled rect as border
            # Simple border simulation via larger bg and slightly smaller inset doesn't work well due to opened top.
            # Thus, keeping just the soft glass effect is cleaner and extremely modern.
            
            # --- Rendering Balls Math ---
            ball_radius = tube_w * 0.41
            ball_diameter = ball_radius * 2
            bottom_padding = tube_w * 0.15
            
            step_y = (tube_h - bottom_padding) / capacity
            
            for i, ball_color_idx in enumerate(tube_data):
                color = self.colors_list[ball_color_idx]
                
                bx = tube_x + tube_w / 2 - ball_radius
                by = tube_y + bottom_padding + (i * step_y)
                
                # Highlight "Pop up" effect if selected
                if self.is_selected and i == len(tube_data) - 1:
                    by += (tube_h * 0.25)
                
                # Base Color
                Color(*color)
                Ellipse(pos=(bx, by), size=(ball_diameter, ball_diameter))
                
                # Glossy highlight reflection (top-left offset)
                Color(1, 1, 1, 0.5)
                # Ensure the glossy reflection scales properly representing a curved surface
                refl_w = ball_diameter * 0.4
                refl_h = ball_diameter * 0.4
                Ellipse(pos=(bx + ball_diameter*0.15, by + ball_diameter*0.5), size=(refl_w, refl_h))

    def on_touch_down(self, touch):
        # We perform simple point-bounding box collision detection
        if self.collide_point(*touch.pos):
            self.on_tap_callback(self.tube_idx)
            return True
        return super().on_touch_down(touch)
