from board import Direction, Rotation, Action, Shape
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError


class PlayerX(Player):
    def __init__(self, a= 0.0000, b=-0.0659, c=-0.3595, d=-0.7527, e= 0.1223, f= 0.0000, g=-0.8372, h= 0.0000, i= 0.5923, j= 1.0000):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h
        self.i = i
        self.j = j
    
    def get_num_rotations(self, shape):
        shape_to_unique_rotations = {
            Shape.I: 2,
            Shape.J: 4,
            Shape.L: 4,
            Shape.O: 1,
            Shape.S: 2,
            Shape.T: 4,
            Shape.Z: 2,
            Shape.B: 1
        }
        return shape_to_unique_rotations[shape]

    def get_col_height(self, sandbox):
        col_heights = []
        for x in range(sandbox.width):
            height = 0
            for y in range(sandbox.height):
                if (x,y) in sandbox.cells:
                    height = sandbox.height - y
                    break
            col_heights.append(height)
        return col_heights
    
    def get_col_holes(self, sandbox):
        col_holes = []
        for x in range(sandbox.width):
            holes = 0
            found_cell = False
            for y in range(sandbox.height):
                if not found_cell and (x,y) in sandbox.cells:
                    found_cell = True
                elif found_cell and (x,y) not in sandbox.cells:
                    holes += 1
            col_holes.append(holes)
        return col_holes

    def get_num_lines(self, sandbox, old_score):
        score_gained = sandbox.score - old_score
        if score_gained >= 1600:
            return 4
        elif score_gained >= 400:
            return 3
        elif score_gained >= 100:
            return 2
        elif score_gained >= 25:
            return 1
        return 0

    def get_bumpiness(self, col_heights):
        bumpiness = 0
        for i in range(len(col_heights) - 1):
            bumpiness += abs(col_heights[i] - col_heights[i+1])
        return bumpiness
    
    def b4(self, col_heights):
        found = False
        repeat = False
        for i in range(len(col_heights) - 1):
            if i == 0:
                if (col_heights[1] - col_heights[0]) >= 4:
                    if not found:
                        found = True
                    else:
                        repeat = True
            elif i == len(col_heights) - 2:
                if (col_heights[len(col_heights)-2] - col_heights[len(col_heights)-1]) >= 4:
                    if not found:
                        found = True
                    else:
                        repeat = True
            else:
                if (col_heights[i-1] - col_heights[i]) >= 4 and (col_heights[i+1] - col_heights[i]) >= 4:
                    if not found:
                        found = True
                    else:
                        repeat = True
        return found and not repeat

    def get_average_height(self, col_heights):
        return sum(col_heights) / len(col_heights)

    def get_heuristic(self, sandbox, prev_score, shape, y_pos):
        # guides used to calculate move heuristic value - no code copied and pasted
        # https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
        # https://youtu.be/os4DcbpL0Nc

        col_heights = self.get_col_height(sandbox)
        col_holes = self.get_col_holes(sandbox)

        total_height = self.a * sum(col_heights)
        lines = self.b * self.get_num_lines(sandbox, prev_score)
        holes = self.c * sum(col_holes)
        bumpiness = self.d * self.get_bumpiness(col_heights)
        max_height = self.e * max(col_heights)
        delta_height = self.f * (max(col_heights) - min(col_heights))

        not_tetris = 0 # more than 0, but less than 4 lines cleared
        if self.get_num_lines(sandbox, prev_score) > 0 and self.get_num_lines(sandbox, prev_score) < 4:
            not_tetris = self.g * 5

        empty_last_col = 0
        if y_pos == sandbox.width - 1 and self.get_num_lines(sandbox, prev_score) < 4:
            empty_last_col = self.h * 5

        bump4 = 0
        if self.b4(col_heights):
            bump4 = self.i * 5

        tetris = 0
        if self.get_num_lines(sandbox, prev_score) == 4:
            tetris = self.j * 100

        return (total_height + lines + holes + bumpiness + max_height + delta_height + not_tetris + empty_last_col + bump4 + tetris)
    
    def get_best_moves(self, board, depth):
        best_moves = [Action.Discard]
        best_value = -1000 * depth
        shape = board.falling.shape
        for y in range(board.width):
            for num_rotations in range(self.get_num_rotations(shape)):
                moves = []
                sandbox = board.clone()
                previous_score = sandbox.score
                has_landed = False

                if num_rotations == 3:
                    has_landed = sandbox.rotate(Rotation.Anticlockwise)
                    moves.append(Rotation.Anticlockwise)
                else:
                    i = 0
                    while not has_landed and i < num_rotations:
                        has_landed = sandbox.rotate(Rotation.Clockwise) 
                        moves.append(Rotation.Clockwise)
                        i += 1

                while not has_landed and sandbox.falling.left > y:
                    has_landed = sandbox.move(Direction.Left)
                    moves.append(Direction.Left)
                while not has_landed and sandbox.falling.right < y:
                    has_landed = sandbox.move(Direction.Right)
                    moves.append(Direction.Right)

                if not has_landed:
                    sandbox.move(Direction.Drop)
                    moves.append(Direction.Drop)
                
                if sum(self.get_col_holes(sandbox)) == 0 or board.discards_remaining == 0:
                    if depth > 1:
                        best_next_moves, best_next_value = self.get_best_moves(sandbox, depth-1)
                        value = self.get_heuristic(sandbox, previous_score, shape, y) + best_next_value
                        if value > best_value:
                            best_moves = moves + best_next_moves
                            best_value = value
                            # if sum(self.get_col_holes(sandbox)) > 0 and board.discards_remaining > 0:
                            #     best_moves = [Action.Discard]
                            #     best_value = -1000
                    else:
                        value = self.get_heuristic(sandbox, previous_score, shape, y)
                        if value > best_value:
                            best_moves = moves
                            best_value = value
                            # if sum(self.get_col_holes(sandbox)) > 0 and board.discards_remaining > 0:
                            #     best_moves = [Action.Discard]
                            #     best_value = -1000
        return best_moves, best_value
    
    def choose_action(self, board):
        depth = 2
        best_moves, best_value = self.get_best_moves(board, depth)

        if max(self.get_col_height(board)) >= 20 and board.bombs_remaining > 0:
            return [Action.Bomb for _ in range(board.bombs_remaining)]

        return best_moves
    
SelectedPlayer = PlayerX