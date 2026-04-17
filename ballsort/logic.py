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
            
        # 2. Perform sequence of random valid REVERSE moves to definitively scramble the puzzle.
        # A valid reverse move taking a ball of color C from tube dst_idx to src_idx requires:
        # - The tube we pull from MUST have C on top.
        # - The tube we pull from, once C is removed, MUST be empty OR still have C on top.
        iterations = 0
        moves_done = 0
        while moves_done < 1500 and iterations < 10000:
            iterations += 1
            src_idx = random.randint(0, len(self.board) - 1)
            dst_idx = random.randint(0, len(self.board) - 1)
            
            if src_idx != dst_idx:
                src_tube = self.board[src_idx]
                dst_tube = self.board[dst_idx]
                
                # Check valid reverse move constraints:
                if not src_tube or len(dst_tube) >= self.tube_height:
                    continue
                
                color = src_tube[-1]
                
                # If we remove the top ball, does the source tube's new top match the valid forward rule?
                # i.e., empty or matching color
                if len(src_tube) > 1 and src_tube[-2] != color:
                    continue
                    
                # Valid! Apply reverse move physically
                ball = self.board[src_idx].pop()
                self.board[dst_idx].append(ball)
                moves_done += 1
        
        # Clear history to establish the "start" of the level
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
