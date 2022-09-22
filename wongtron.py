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

# -------------------------------------- #
# imports
# -------------------------------------- #

from time import sleep
from enum import Enum
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

def parse_pregame_moves():
    move_lines = [];
    moves = [];

    # the first and third pregame moves belong to whoever gets the first turn.
    wongtrons_turn_first = file_present(TURN_INDICATOR_FILENAME);

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

# -------------------------------------- #
# play functions
# -------------------------------------- #

def play():
    pass;

# -------------------------------------- #
# main
# -------------------------------------- #

def main():
    # init game variables
    state = WongtronState.WAITING_FOR_TURN;
    boards = init_boards();

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
            play();
            state = WongtronState.WAITING_FOR_OPP_TURN;

if __name__ == '__main__':
    main();
