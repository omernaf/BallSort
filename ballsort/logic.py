import copy
import random

class BallSortLogic:
    def __init__(self, num_colors=5, tube_height=4, num_empty_tubes=2):
        self.num_colors = num_colors
        self.tube_height = tube_height
        self.num_empty_tubes = num_empty_tubes
        self.board = []
        self.history = []
        self.generate_level()

    def generate_level(self):
        self.board = []
        self.history = []
        
        # We will deal a completely chaotic, perfectly packed board.
        # This guarantees every colored tube starts exactly full, making it vastly harder 
        # and more complex to untangle properly.
        # With 2 empty tubes + the `+ Empty Tube` cheat button available, any rare deadlock is gracefully bypassable.
        
        while True:
            # 1. Create a deck containing exactly `tube_height` balls for every color
            balls = []
            for i in range(self.num_colors):
                balls.extend([i] * self.tube_height)
                
            # 2. Maximum chaos shuffle
            random.shuffle(balls)
            
            # 3. Deal perfectly into tubes
            temp_board = []
            for i in range(self.num_colors):
                start = i * self.tube_height
                end = start + self.tube_height
                temp_board.append(balls[start:end])
                
            # 4. Check to ensure we didn't randomly deal an already-solved tube, 
            #    which would reduce the target difficulty.
            has_solved_tube = False
            for tube in temp_board:
                if len(set(tube)) == 1:
                    has_solved_tube = True
                    break
                    
            if not has_solved_tube:
                self.board = temp_board
                break
                
        # 5. Append perfectly empty tubes at the end
        for i in range(self.num_empty_tubes):
            self.board.append([])
            
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
        # The Cheat Button - essential for brute-forcing any extremely difficult seed
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
