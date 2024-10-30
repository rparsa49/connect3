import random 
import math 
import numpy as np

COLUMN_COUNT = 5
ROW_COUNT = 4
Row = tuple[int, int, int, int, int]
Board = tuple[Row, Row, Row, Row]

EmptyRow = COLUMN_COUNT*(0,)
EmptyBoard = ROW_COUNT*(EmptyRow,)

PLAYER = 1
BOT = 2
WINDOW = 3
EMPTY = 0

def show(board: Board):
    for row in board:
        print(row)
    print()

def is_valid_move_in(board: Board, col: int) -> bool:
    """Return true if and only if there is a space in the given column to drop a piece."""
    return board[ROW_COUNT - 1][col] == 0

def get_valid_location(board):
    '''Return all empty locations on the board'''
    valid = []
    for col in range(COLUMN_COUNT):
        if is_valid_move_in(board, col):
            valid.append(col)
    return valid

def game_won_by(board, player):
    # Check horizontal locations
    for c in range(COLUMN_COUNT - 2):
        for r in range(ROW_COUNT):
            if all(board[r][c+i] == player for i in range(3)):
                return True

    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 2):
            if all(board[r+i][c] == player for i in range(3)):
                return True

    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT - 2):
        for r in range(ROW_COUNT - 2):
            if all(board[r+i][c+i] == player for i in range(3)):
                return True

    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT - 2):
        for r in range(2, ROW_COUNT):
            if all(board[r-i][c+i] == player for i in range(3)):
                return True

def evaluate_window(window, piece):
    score = 0
    opponent = PLAYER
    if piece == PLAYER:
        opponent = BOT
    
    if window.count(piece) == 3:
        score += 1000
    elif window.count(piece) == 2 and window.count(EMPTY) == 1:
        score += 100
    elif window.count(piece) == 1 and window.count(EMPTY) == 2:
        score += 10
        
    if window.count(opponent) == 2 and window.count(EMPTY) == 1:
        score -= 12
    return score

def score_position(board, piece):
    '''Assign a score to a positions'''
    score = 0
    
    # Score center column
    center = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center.count(piece)
    score += center_count * 15
    
    # Score horizontal by counting rows in windows of 3
    for r in range(ROW_COUNT):
        rows = [int(i) for i in list(board[r,:])]
        for col in range(COLUMN_COUNT - 2):
            window = rows[col:col + WINDOW]
            score += evaluate_window(window, piece)
    
    # Score vertical similarly
    for c in range(COLUMN_COUNT):
        columns = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 2):
            window = columns[r:r + WINDOW]
            score += evaluate_window(window, piece)

    
    # Score positive sloped diagonal
    for r in range(ROW_COUNT - 2):
        for c in range(COLUMN_COUNT - 2):
            window = [board[r+i][c+i] for i in range(WINDOW)]
            score += evaluate_window(window, piece)

                
    # Score negatively sloped diagonal
    for r in range(ROW_COUNT - 2):
        for c in range(COLUMN_COUNT - 2):
            window = [board[r+2-i][c+i] for i in range(WINDOW)]
            score += evaluate_window(window, piece)

    return score

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def drop_piece(board, row, col, piece):
    board[row][col] = piece
    
def pick_move(board, piece):
    '''Function that simulates dropping a piece and keeping track of the score. It will update the score with the 'best' score and return the column associated with it '''
    valid_moves = get_valid_location(board)
    best_score = 0
    best_col = random.choice(valid_moves)
    for col in valid_moves:
        row = get_next_open_row(board, col)
        # simulate dropping piece
        temp = board
        drop_piece(temp, row, col, piece)
        score = score_position(temp, piece)
        if score > best_score:
            best_score = score
            best_col = col
            
    return best_col

def is_terminal_node(board):
    """Tells us if the game has won"""
    return game_won_by(board,PLAYER) or game_won_by(board,BOT) or len(get_valid_location(board)) == 0

def minimax(board, depth, alpha, beta, maximizing):
    valid_locations = get_valid_location(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if game_won_by(board, BOT): # when the AI Wins
                return (None, 99999999)
            elif game_won_by(board, PLAYER): # when the player wins
                return (None, -99999999)
            else: # When there are no empty spots and no winner
                return (None, 0)
        else: # depth is 0
            # Find heuristic value of the board
            return (None, score_position(board, BOT))
    if maximizing:  # if max is playing
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            copy = np.copy(board)
            drop_piece(copy, row, col, BOT)
            new_score = minimax(copy, depth - 1, alpha, beta, False)[1] # now we pass in false, because the next turn is min
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value) # pruning
            if alpha >= beta:
                break  
        return column, value
    else: # if min is playing
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            copy = np.copy(board)
            drop_piece(copy, row, col, PLAYER)
            # now we pass in true, because the next turn is max
            new_score = minimax(copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value) # pruning
            if alpha >= beta:
                break
        return column, value

def move_for_player_2(board: Board) -> int:
    """Given a board and assuming it is player 2's turn, choose a column to play in"""
    col, value = minimax(board, 3, -math.inf, math.inf, True)
    return col    




