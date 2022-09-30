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

# -------------------------------------- #
# imports
# -------------------------------------- #

from time import sleep
from enum import Enum
import argparse
import os

# -------------------------------------- #
# derived variables
# -------------------------------------- #

TURN_INDICATOR_FILENAME = (NAME + '.go');

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

# apply the given move object to the given boards
def apply_move(boards, move):
   board_number = move.board_number;
   cell_number = move.cell_number;
   cell_state = CellState.WONG if move.wongtron else CellState.OPP;
   boards[board_number][cell_number] = cell_state;

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

def parse_pregame_moves():
    move_lines = [];
    moves = [];

    # wait till move file and one of the go files exists
    while not (file_present(MOVE_FILENAME) and either_go_file_present()): 
        print('waiting for initial game files')
        sleep(WAIT_REFRESH_SECONDS);

    # the first and third pregame moves belong to whoever gets the first turn.
    wongtrons_turn_first = file_present(TURN_INDICATOR_FILENAME) and (len(parse_move_file()) == 0);

    # parse first four moves
    with open(PREGAME_MOVES_FILENAME) as f:
        move_lines = f.readlines();
    for i, line in enumerate(move_lines):
        split_move_line = line.split();
        board_num = int(split_move_line[1]);
        cell_num = int(split_move_line[2]);

        # this move begins to wong if wong is first turn and this is the first or third pregame move
        wongs_move = wongtrons_turn_first if (i % 2 == 0) else not wongtrons_turn_first;
        
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

#NOT FINISHED
def check_win_global(boards):
    return False;

#returns True if board is done and winner if board is done
def check_win_local(board):
    global WINNING_LINES
    filled_cells = 0
    for line in WINNING_LINES:
        wong, opp, empty = count_cells_in_line(line, board)
        if wong == 3: return [True, "WONG"]
        elif opp == 3: return [True, "OPP"]
        else: filled_cells +=  + wong + opp
    if filled_cells == 24: return [True, "DRAW"]
    else: return [False]

#returns the # of wongtron cells, opp cells, or empty cells in a WINNING_LINE
def count_cells_in_line(line, board): 
    board_line = [board[line[0]], board[line[1]], board[line[2]]]
    wong = board_line.count(CellState.WONG)
    opp = board_line.count(CellState.OPP)
    empty = board_line.count(CellState.EMPTY)
    return wong, opp, empty

#NOT FINISHED
def count_boards_in_line(line, boards): 
    boards_line = [boards[line[0]], boards[line[1]], boards[line[2]]]
    wong = boards_line
    return wong, opp, empty

def find_valid_moves(boards, last_move):
    valid_moves = [];
    last_cell_num = last_move.cell_number;
    next_board = boards[last_cell_num];

    # if board won, find valid moves in all incomplete boards
    if check_win_local(next_board)[0]:
        for board_num, board in enumerate(boards):
            if not check_win_local(board)[0]:
                for cell_num, cell in enumerate(next_board):
                    if cell == CellState.EMPTY:
                        valid_moves.append(Move(True, board_num, cell_num));
    # elif board incomplete
    else: 
        for cell_num, cell in enumerate(next_board):
            if cell == CellState.EMPTY:
                valid_moves.append(Move(True, last_cell_num, cell_num));

    return valid_moves;

def play(moves):
    #generate board from moves
    boards = init_boards();
    for move in moves:
        apply_move(boards, move);

    last_move = moves[-1];
    valid_moves = find_valid_moves(boards, last_move);
    
    return valid_moves[0];

# -------------------------------------- #
# main
# -------------------------------------- #

def main():
    boards = init_boards();
    m = Move(False, 4, 4);
    apply_move(boards, m);
    mvs = find_valid_moves(boards, m);
    for mv in mvs:
        print_move(mv);
    return;

    # init game state
    state = WongtronState.WAITING_FOR_TURN;
    moves = parse_pregame_moves();

    while(True):
        # wait for referee to remove the wongtron.go file
        if state == WongtronState.WAITING_FOR_OPP_TURN:
            if not file_present(TURN_INDICATOR_FILENAME):
                state = WongtronState.WAITING_FOR_TURN;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # wait for wongtron.go file
        elif state == WongtronState.WAITING_FOR_TURN:
            if file_present(TURN_INDICATOR_FILENAME):
                state = WongtronState.PLAYING;
            else:
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
