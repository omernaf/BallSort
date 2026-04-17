import copy
import random

class BallSortLogic:
    def __init__(self, num_colors=4, tube_height=4, num_empty_tubes=2):
        self.num_colors = num_colors
        self.tube_height = tube_height
        self.num_empty_tubes = num_empty_tubes
        self.board = []
        self.history = []
        self.generate_level()

    def generate_level(self):
        self.board = []
        self.history = []
        
        # 1. Start with sorted tubes
        for i in range(self.num_colors):
            self.board.append([i] * self.tube_height)
        
        # Add empty tubes
        for _ in range(self.num_empty_tubes):
            self.board.append([])
            
        # 2. Perform sequence of random valid moves to shuffle.
        # Since forward and reverse moves share the exact same validation 
        # constraints in Ball Sort, ANY valid sequence of moves from a 
        # solved state is mathematically guaranteed to be solvable!
        iterations = 0
        moves_done = 0
        while moves_done < 200 and iterations < 1500:
            iterations += 1
            src_idx = random.randint(0, len(self.board) - 1)
            dst_idx = random.randint(0, len(self.board) - 1)
            
            if src_idx != dst_idx and self.can_move(src_idx, dst_idx):
                self._apply_move(src_idx, dst_idx)
                moves_done += 1
        
        # Clear history to establish the "start" of the level
        self.history = []

    def can_move(self, src_idx, dst_idx):
        if src_idx == dst_idx:
            return False
            
        src_tube = self.board[src_idx]
        dst_tube = self.board[dst_idx]
        
        if not src_tube:
            return False  # Source is empty
            
        if len(dst_tube) >= self.tube_height:
            return False  # Target is full
            
        # Target must be empty, or its top ball must match the source's top ball
        moving_ball = src_tube[-1]
        if not dst_tube or dst_tube[-1] == moving_ball:
            return True
            
        return False

    def _apply_move(self, src_idx, dst_idx):
        ball = self.board[src_idx].pop()
        self.board[dst_idx].append(ball)

    def move(self, src_idx, dst_idx):
        if self.can_move(src_idx, dst_idx):
            self.history.append(copy.deepcopy(self.board))
            self._apply_move(src_idx, dst_idx)
            return True
        return False

    def undo(self):
        if self.history:
            self.board = self.history.pop()
            return True
        return False

    def add_empty_tube(self):
        # We append a new empty tube without invalidating history
        self.board.append([])

    def is_win(self):
        for tube in self.board:
            # Tube must be perfectly empty or perfectly full with one color
            if len(tube) == 0:
                continue
            if len(tube) != self.tube_height:
                return False
            
            first_color = tube[0]
            if any(ball != first_color for ball in tube):
                return False
        return True
