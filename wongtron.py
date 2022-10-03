# -------------------------------------- #
#  WONGTRON
#  CS4341
#  Aria Yan
#  Jacob Salerno
#  Nestor Lopez
# -------------------------------------- #

# -------------------------------------- #
# wongtron config variables
# -------------------------------------- #

PREGAME_MOVES_FILENAME = 'first_four_moves';
MOVE_FILENAME = 'move_file';
WAIT_REFRESH_SECONDS = 0.1;
NAME = 'wongtron';
WINNING_LINES = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
MINMAX_DEPTH_LIMIT = 2;
W_SCORE =  1000;
L_SCORE = -1000;

#dev controls
PRINT_AND_WAIT_FOR_OK_EACH_TURN = True;

# -------------------------------------- #
# imports
# -------------------------------------- #

from email.base64mime import body_encode
from time import sleep
from enum import Enum
import argparse
import os

# -------------------------------------- #
# enums
# -------------------------------------- #

# wongtron state
class WongtronState(Enum):
    WAITING_FOR_OPP_TURN = 0; # after our turn, waiting for wongtron.go deletion
    WAITING_FOR_TURN = 1; # waiting to see wongtron.go
    PLAYING = 2;

# board cell state enum
class CellState(Enum):
    EMPTY = 0;
    WONG = 1;
    OPP = 2;

class CellType(Enum):
    CORNER = [0,2,6,8]
    MIDDLE = [4]
    EDGE = [1,3,5,7]

 
# -------------------------------------- #
# board types
# -------------------------------------- #

class Move():
    def __init__(self, wongtron, board, cell):
        self.wongtron = wongtron;
        self.board_number = board;
        self.cell_number = cell;

# -------------------------------------- #
# board functions
# -------------------------------------- #

# initialize a classic board. (1x9 array of CellState's, index 4 is center cell)
def init_classic_board():
    board = [];
    for i in range(9):
        board.append(CellState.EMPTY);
    return board;

# initialize the ultimate board. (1x9 array of classic boards, index 4 is center board)
def init_boards():
    boards = [];
    for board in range(9):
        boards.append(init_classic_board());
    return boards;

# deep copy a given ultimate board, return copy
def copy_boards(boards):
    new_boards = [];
    for board_num, board in enumerate(boards):
        new_boards.append([]);
        for cell in board:
            new_boards[board_num].append(cell);
    return new_boards;

# returns a new ultimate board with the given move applied
def apply_move(boards, move):
    # copy board
    new_boards = copy_boards(boards);
    board_number = move.board_number;
    cell_number = move.cell_number;
    cell_state = CellState.WONG if move.wongtron else CellState.OPP;
    new_boards[board_number][cell_number] = cell_state;
    return new_boards;

# -------------------------------------- #
# file IO functions
# -------------------------------------- #

# check if the given filename is present in cwd
def file_present(filename):
    cwd = os.getcwd();
    directory_contents = os.listdir(cwd);
    file_present = filename in directory_contents;
    return file_present;

# check if a go file is present
def either_go_file_present():
    cwd = os.getcwd();
    directory_contents = os.listdir(cwd);
    for name in directory_contents:
        if name[-3:] == '.go':
            return True;
    return False;

    # wait till move file and one of the go files exists
def wait_for_initial_game_files():
    while not (file_present(MOVE_FILENAME) and either_go_file_present()): 
        print('waiting for initial game files')
        sleep(WAIT_REFRESH_SECONDS);

def parse_pregame_moves():
    move_lines = [];
    moves = [];

    # parse first four moves
    with open(PREGAME_MOVES_FILENAME) as f:
        move_lines = f.readlines();
    for i, line in enumerate(move_lines):
        split_move_line = line.split();
        board_num = int(split_move_line[1]);
        cell_num = int(split_move_line[2]);
        player = split_move_line[0];

        # this move begins to wong if wong is first turn and this is the first or third pregame move
        wongs_move = player == NAME;
        
        moves.append(Move(wongs_move, board_num, cell_num));

    return moves;

def parse_move_file():
    move_lines = [];
    moves = [];

    with open(MOVE_FILENAME) as f:
        move_lines = f.readlines();
    for i, line in enumerate(move_lines):
        split_move_line = line.split();
        wongs_move = split_move_line[0] == NAME;
        board_num = int(split_move_line[1]);
        cell_num = int(split_move_line[2]);
        
        moves.append(Move(wongs_move, board_num, cell_num));

    return moves;

def parse_new_moves(moves):
    move_file_moves = parse_move_file();
    return move_file_moves;

#write given move to move file
def write_move(move):
    move_file = open(MOVE_FILENAME, "w");
    move_file.write(NAME+" "+str(move.board_number)+" "+str(move.cell_number)+"\n");

# -------------------------------------- #
# printing functions
# -------------------------------------- #

def print_move(move):
    player_string = 'wongtron' if move.wongtron else 'opp';
    print(f'{player_string} {move.board_number} {move.cell_number}');

# -------------------------------------- #
# play functions
# -------------------------------------- #

#returns True if game is over and winner of game
def check_win_global(boards):
    global WINNING_LINES
    finished_boards = 0
    for line in WINNING_LINES:
        wong, opp = count_boards_in_line(line, boards)
        if wong == 3: return [True, "WONG"]
        elif opp == 3: return [True, "OPP"]
        else: finished_boards += wong + opp
    if finished_boards == 24: return [True, "DRAW"]
    else: return [False]

def wongtron_global_win(boards):
    check_result = check_win_global(boards);
    return check_result[0] and check_result[1] == "WONG"; # TODO write test case for this

def opp_global_win(boards):
    check_result = check_win_global(boards);
    return check_result[0] and check_result[1] == "OPP"; # TODO write test case for this

#returns True if board is done and winner of finished board
def check_win_local(board):
    global WINNING_LINES
    filled_cells = 0
    for line in WINNING_LINES:
        wong, opp = count_cells_in_line(line, board)
        if wong == 3: return [True, "WONG"]
        elif opp == 3: return [True, "OPP"]
        else: filled_cells += wong + opp
    if filled_cells == 24: return [True, "DRAW"]
    else: return [False]

#returns the # of wongtron cells, opp cells, or empty cells in a WINNING_LINE
def count_cells_in_line(line, board): 
    board_line = [board[line[0]], board[line[1]], board[line[2]]]
    wong = board_line.count(CellState.WONG)
    opp = board_line.count(CellState.OPP)
    return wong, opp

#same as above but boards instead of cells
def count_boards_in_line(line, boards): 
    boards_line = map(check_win_local, [boards[line[0]], boards[line[1]], boards[line[2]]])
    wong, opp = 0, 0;
    for local_result in boards_line:
        if local_result[0] == True and local_result[1] == "WONG":
            wong += 1;
        if local_result[0] == True and local_result[1] == "OPP":
            opp += 1;
    return wong, opp

#move check functions assume moves are wongtron's moves and are occuring on empty cells
#move is integer of local move position
def is_local_win(board, move):
    global WINNING_LINES
    for line in WINNING_LINES:
        if move in line: 
            wong, opp = count_cells_in_line(board, line)
            #if 2 cells in the line are wong, 3rd is empty and is the move
            if wong == 2: return True
    return False

def is_local_two_in_a_row(board, move):
    global WINNING_LINES
    for line in WINNING_LINES:
        if move in line: 
            wong, opp = count_cells_in_line(board, line)
            #1 current wong, no opp in line
            if wong == 1 and opp == 0: return True
    return False

def is_local_block(board, move):
    global WINNING_LINES
    for line in WINNING_LINES:
        if move in line: 
            wong, opp = count_cells_in_line(board, line)
            #2 current opp, move would block line
            if opp == 2: return True
    return False

#move is (global, local) tuple
def is_global_win(boards, move):
    global WINNING_LINES
    #move does not win local board
    if not is_local_win(boards[move[0]], move[1]): return False
    for line in WINNING_LINES:
        if move[0] in line:
            wong, opp = count_boards_in_line(line, boards)
            if wong == 2: return True
    
def is_global_two_in_a_row(boards, move):
    global WINNING_LINES
    if not is_local_win(boards[move[0]], move[1]): return False
    for line in WINNING_LINES:
        if move[0] in line:
            wong, opp = count_boards_in_line(line, boards)
            if wong == 1 and opp == 0: return True

def is_global_block(boards, move):
    global WINNING_LINES
    if not is_local_win(boards[move[0]], move[1]): return False
    for line in WINNING_LINES:
        if move[0] in line:
            wong, opp = count_boards_in_line(line, boards)
            if opp == 2: return True

#winning lines based on player, if 0, board is dead
def local_winning_lines(board, player):
    global WINNING_LINES
    wonglines=0
    opplines=0
    for line in WINNING_LINES:
        wong, opp = count_cells_in_line(line, board)
        if wong == 0: opp += 1
        if opp == 0: wong += 1
    if player == "wong": return wonglines
    elif player == "opp": return opplines

def global_winning_lines(boards, player):
    global WINNING_LINES
    wonglines=0
    opplines=0
    for line in WINNING_LINES:
        wong, opp = count_boards_in_line(line, boards)
        if wong == 0: opp += 1
        if opp == 0: wong += 1
    if player == "wong": return wonglines
    elif player == "opp": return opplines
    

def find_valid_moves(boards, last_move):
    last_cell_num = last_move.cell_number;
    next_board = boards[last_cell_num];
    wongs_turn = not last_move.wongtron;
    valid_moves = [];

    # if board won, find valid moves in all incomplete boards
    if check_win_local(next_board)[0]:
        for board_num, board in enumerate(boards):
            if not check_win_local(board)[0]:
                for cell_num, cell in enumerate(board):
                    if cell == CellState.EMPTY:
                        valid_moves.append(Move(wongs_turn, board_num, cell_num));
    # elif board incomplete
    else: 
        for cell_num, cell in enumerate(next_board):
            if cell == CellState.EMPTY:
                valid_moves.append(Move(wongs_turn, last_cell_num, cell_num));

    return valid_moves;

def eval(boards):
    return 1;

# return true if minmax level is a wongtron move
def mm_wongtron_move(depth):
    return depth % 2 == 0; # TODO double check this

def minmax(boards, last_move, depth, levels_dominant_score):
    result_boards = apply_move(boards, last_move);
    
    #  win
    if wongtron_global_win(boards):
        return W_SCORE;

    #  loss
    elif opp_global_win(boards):
        return L_SCORE;

    # depth reached 
    elif depth > MINMAX_DEPTH_LIMIT:
        return eval(result_boards);

    # gen new moves, minmax on each, prune 
    else:
        possible_moves = find_valid_moves(boards, last_move)

        dominant_move = possible_moves[0];
        dominant_score = minmax(result_boards, dominant_move, depth + 1, None);
        for move in possible_moves[1:]:

            # pruning: return if the levels dominant score leaves this branch unusable # TODO double check this
            if levels_dominant_score is not None:
                if (mm_wongtron_move(depth) and dominant_score < levels_dominant_score): # wong will select a previous branch
                    break;
                if (not mm_wongtron_move(depth) and dominant_score > levels_dominant_score): # opp will select a previous branch
                    break;
            
            score = minmax(result_boards, move, depth + 1, dominant_score);

            # check if score dominates
            if (mm_wongtron_move(depth) and score < dominant_score) or (not mm_wongtron_move(depth) and score > dominant_score): # TODO double check this
                dominant_score = score;
                dominant_move = move;
    
    return dominant_score;

# minmax call for the next wongtron move
def minmax_start(boards, next_wongtron_move_candidate):
    return minmax(boards, next_wongtron_move_candidate, 0, None); # TODO double check this

def play(moves):
    our_move = None;
    #generate board from moves
    boards = init_boards();
    for move in moves:
        boards = apply_move(boards, move);

    last_move = moves[-1];
    valid_moves = find_valid_moves(boards, last_move);
    
    best_move = valid_moves[0];
    best_move_score = minmax_start(boards, best_move);

    for move in valid_moves[1:]:
        score = minmax_start(boards, move);
        if score > best_move_score:
            best_move_score = score;
            best_move = move;
    our_move = best_move;

    if PRINT_AND_WAIT_FOR_OK_EACH_TURN:
        print('our move: ', end='');
        print_move(our_move);
        input('press enter to continue.');
    return our_move;

# -------------------------------------- #
# evaluation functions
# -------------------------------------- #

# TO-DO ADD weights

def simple_eval(board):
    
    #Check if we are in a finished board
    if (check_win_local(board)[0] and check_win_local(board)[1] == "WONG"):
        return 20
    if (check_win_local(board)[0] and check_win_local(board)[1] == "OPP"):
        return -10
    if (check_win_local(board)[0] and check_win_local(board)[1] == "DRAW"):
        return 0 
        
    square_calcs = []

    for square in range(9):

        if (board[square] == CellState.EMPTY):
            
            if (is_local_win(board, square)):
                square_calcs.append(5)
            
            elif (is_local_block(board,square)):
                square_calcs.append(4)
            
            elif (is_local_two_in_a_row(board,square)):
                square_calcs.append(3)
            
            else:
                if(square in CellType.EDGE):
                    square_calcs.append(1)
                elif(square in CellType.CORNER):
                    square_calcs.append(0.75)
                else:
                    square_calcs.append(0.5)

        else:
            square_calcs.append(0)
            
        
        
            
    return sum(list(filter(lambda x: (x),square_calcs)))


def weighted_eval(boards):
    
    board_calcs = []
    
    for board in boards:
        board_calcs.append(simple_eval(board))

    return sum(list(filter(lambda x: (x),board_calcs)))


def evaluate (boards):
    
    if (check_win_global(boards)[0] and check_win_global(boards)[1] == "WONG"):
        return 10000
    if (check_win_global(boards)[0] and check_win_global(boards)[1] == "OPP"):
        return -10000

    return weighted_eval(boards)


    
    
        


# -------------------------------------- #
# main
# -------------------------------------- #

def main():
    # init game state
    state = WongtronState.WAITING_FOR_TURN;
    wait_for_initial_game_files();
    moves = parse_pregame_moves();

    while(True):
        # wait for referee to remove the wongtron.go file
        if state == WongtronState.WAITING_FOR_OPP_TURN:
            if not file_present(NAME + '.go'):
                state = WongtronState.WAITING_FOR_TURN;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # wait for wongtron.go file
        elif state == WongtronState.WAITING_FOR_TURN:
            if file_present(NAME + '.go'):
                state = WongtronState.PLAYING;
            else:
                print('waiting')
                sleep(WAIT_REFRESH_SECONDS);

        # play our turn 
        elif state == WongtronState.PLAYING:
            moves += parse_new_moves(moves);
            our_move = play(moves);
            moves.append(our_move);
            write_move(our_move);
            state = WongtronState.WAITING_FOR_OPP_TURN;

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--name', type=str)
    args = parser.parse_args();

    if args.name is not None: NAME = args.name;

    main();
