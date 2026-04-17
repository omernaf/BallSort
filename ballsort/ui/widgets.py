from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty
from kivy.metrics import dp

class ModernButton(ButtonBehavior, Label):
    bg_color = ListProperty([0.2, 0.6, 0.86, 1])
    bg_color_down = ListProperty([0.15, 0.45, 0.65, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = [1, 1, 1, 1]
        self.bold = True
        self.font_size = "15sp"
        
        with self.canvas.before:
            self.bg_instruction = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            
        self.bind(pos=self.update_rect, size=self.update_rect)
        
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        
    def on_state(self, instance, value):
        if value == 'down':
            self.bg_instruction.rgba = self.bg_color_down
        else:
            self.bg_instruction.rgba = self.bg_color
