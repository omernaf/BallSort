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
        
        # Dimensions
        tube_w = min(self.width * 0.8, 80) # Cap maximum width to look nice
        tube_h = self.height * 0.7 # 70% of height for the actual tube
        
        tube_x = self.center_x - tube_w / 2
        tube_y = self.y + self.height * 0.05
        
        with self.canvas:
            # Base of the tube (highlighted if selected)
            if self.is_selected:
                Color(0.4, 0.4, 0.4, 1)
            else:
                Color(0.2, 0.2, 0.2, 1)
            RoundedRectangle(pos=(tube_x, tube_y), size=(tube_w, tube_h), radius=[0, 0, 20, 20])
            
            # Draw balls mathematically spaced inside the tube bounds
            ball_radius = tube_w * 0.4
            ball_diameter = ball_radius * 2
            bottom_padding = tube_w * 0.1
            
            # Distribute balls properly within tube height
            step_y = (tube_h - bottom_padding) / capacity
            
            for i, ball_color_idx in enumerate(tube_data):
                color = self.colors_list[ball_color_idx]
                Color(*color)
                
                bx = tube_x + tube_w / 2 - ball_radius
                by = tube_y + bottom_padding + (i * step_y)
                
                # If this tube is selected and it's the top ball, render it visually "popped up"
                if self.is_selected and i == len(tube_data) - 1:
                    by += (tube_h * 0.3)
                    
                Ellipse(pos=(bx, by), size=(ball_diameter, ball_diameter))

    def on_touch_down(self, touch):
        # We perform simple point-bounding box collision detection for ease of touch
        if self.collide_point(*touch.pos):
            self.on_tap_callback(self.tube_idx)
            return True
        return super().on_touch_down(touch)
