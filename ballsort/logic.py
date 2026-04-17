import copy
import random
import json
import os

class BallSortLogic:
    def __init__(self, num_colors=5, tube_height=4, num_empty_tubes=2, save_file=None):
        self.save_file = save_file
        self.num_empty_tubes = num_empty_tubes
        self.board = []
        self.initial_board = []
        self.history = []
        
        # Attempt to load state, otherwise generate clean setup via arguments
        if not self._load_state():
            self.num_colors = num_colors
            self.tube_height = tube_height
            self.generate_level()

    def _load_state(self):
        if not self.save_file or not os.path.exists(self.save_file):
            return False
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            self.num_colors = data['num_colors']
            self.tube_height = data['tube_height']
            self.num_empty_tubes = data['num_empty_tubes']
            self.initial_board = data['initial_board']
            self.reset_level()
            return True
        except Exception:
            return False

    def save_state(self):
        if not self.save_file:
            return
        try:
            data = {
                'num_colors': self.num_colors,
                'tube_height': self.tube_height,
                'num_empty_tubes': self.num_empty_tubes,
                'initial_board': self.initial_board
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def generate_level(self):
        self.board = []
        self.history = []
        
        while True:
            balls = []
            for i in range(self.num_colors):
                balls.extend([i] * self.tube_height)
                
            random.shuffle(balls)
            
            temp_board = []
            for i in range(self.num_colors):
                start = i * self.tube_height
                end = start + self.tube_height
                temp_board.append(balls[start:end])
                
            has_solved_tube = False
            for tube in temp_board:
                if len(set(tube)) == 1:
                    has_solved_tube = True
                    break
                    
            if not has_solved_tube:
                self.board = temp_board
                break
                
        for i in range(self.num_empty_tubes):
            self.board.append([])
            
        self.initial_board = copy.deepcopy(self.board)
        self.history = []
        
        # Commit structure automatically on generation
        self.save_state()

    def reset_level(self):
        self.board = copy.deepcopy(self.initial_board)
        self.history = []

    def can_move(self, src_idx, dst_idx):
        if src_idx == dst_idx:
            return False
            
        src_tube = self.board[src_idx]
        dst_tube = self.board[dst_idx]
        
        if not src_tube:
            return False
            
        if len(dst_tube) >= self.tube_height:
            return False
            
        moving_ball = src_tube[-1]
        if not dst_tube or dst_tube[-1] == moving_ball:
            return True
            
        return False

    def move(self, src_idx, dst_idx):
        if self.can_move(src_idx, dst_idx):
            self.history.append(copy.deepcopy(self.board))
            ball = self.board[src_idx].pop()
            self.board[dst_idx].append(ball)
            return True
        return False

    def undo(self):
        if self.history:
            self.board = self.history.pop()
            return True
        return False

    def add_empty_tube(self):
        self.board.append([])

    def is_win(self):
        for tube in self.board:
            if len(tube) == 0:
                continue
            if len(tube) != self.tube_height:
                return False
            
            first_color = tube[0]
            if any(ball != first_color for ball in tube):
                return False
        return True
