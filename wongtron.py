#  WONGTRON
#  CS4341
#  Aria Yan
#  Jacob Salerno
#  Nestor Lopez

from time import sleep
from enum import Enum
import os

# wongtron config variables
WAIT_REFRESH_SECONDS = 1;
NAME = 'wongtron';

# derived variables
TURN_INDICATOR_FILENAME = (NAME + '.go');

# wongtron state enum
class WongtronState(Enum):
    WAITING_FOR_OPP_TURN = 0; # after our turn, waiting for wongtron.go deletion
    WAITING_FOR_TURN = 1; # waiting to see wongtron.go
    PLAYING = 2;

# board cell state enum
class CellState(Enum):
    EMPTY = 0;
    WONG = 1;
    OPP = 2;

# move class
class Move():
    def __init__(self, wongtron, board, cell):
        self.wongtron = wongtron;
        self.board_number = board;
        self.cell_number = cell;

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

# check if the given filename is present in cwd
def file_present(filename):
    cwd = os.getcwd();
    directory_contents = os.listdir(cwd);
    file_present = filename in directory_contents;
    return file_present;

def play():
    pass;

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
