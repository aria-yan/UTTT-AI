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
END_GAME_FILENAME = 'end_game';
MOVE_FILENAME = 'move_file';
WAIT_REFRESH_SECONDS = 0.1;
LOG_DIRECTORY = './'
NAME = 'wongtron';
LOGGING = True;

# thinking parameters
MINMAX_DEPTH_LIMIT = 2;
THINKING_TIME = 8;
W_SCORE =  1000;
L_SCORE = -1000;
TIE_SCORE = 0;
GLOBAL_TWO = 0.9
GLOBAL_BLOCK = 0.7
FREE_BOARD = 0.1
OTHER_BOARD = 1.2
LOCAL_WIN = 5
LOCAL_BLOCK = 4
LOCAL_TWO = 3
LOCAL_WON = 20
LOCAL_LOST = -10
LOCAL_TIED = 0
LINE_RATIO_SCALE = 0

# dev controls
WAIT_FOR_OK_EACH_TURN = False;
PRINT_CHOSEN_MOVE = True;
MOVE_DELAY_SECONDS = 0; # time to wait before writing a calculated move (debugging purposes, should be 0 during tournament)

# -------------------------------------- #
# imports
# -------------------------------------- #

from time import sleep, time
from enum import Enum
import datetime
import argparse
import sys
import os

# -------------------------------------- #
# constants
# -------------------------------------- #

WINNING_LINES = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
INVALID_SCORE = -333555777999;

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

    def to_string(self):
        player_string = NAME if self.wongtron else 'opp';
        return f'{player_string} {self.board_number} {self.cell_number}';

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
    log('waiting for initial game files...')
    while not (file_present(MOVE_FILENAME) and either_go_file_present() and file_present(PREGAME_MOVES_FILENAME)): 
        sleep(WAIT_REFRESH_SECONDS);

def parse_pregame_moves():
    move_lines = [];
    moves = [];

    # parse first four moves
    with open(PREGAME_MOVES_FILENAME) as f:
        move_lines = f.readlines();
    for i, line in enumerate(move_lines):
        try:
            split_move_line = line.split();
            board_num = int(split_move_line[1]);
            cell_num = int(split_move_line[2]);
            player = split_move_line[0];

            # this move begins to wong if wong is first turn and this is the first or third pregame move
            wongs_move = player == NAME;
            
            moves.append(Move(wongs_move, board_num, cell_num));
        except Exception as e:
            log(f"ERROR {e} while parsing pre-game move: {line}")

    return moves;

def parse_move_file():
    move_lines = [];
    moves = [];

    with open(MOVE_FILENAME) as f:
        move_lines = f.readlines();
    for i, line in enumerate(move_lines):
        try:
            split_move_line = line.split();
            wongs_move = split_move_line[0] == NAME;
            board_num = int(split_move_line[1]);
            cell_num = int(split_move_line[2]);
            
            moves.append(Move(wongs_move, board_num, cell_num));
        
        except Exception as e:
            log(f'ERROR {e} when parsing move file line: {line}');

    return moves;

def parse_new_moves(moves):
    move_file_moves = parse_move_file();
    return move_file_moves;

#write given move to move file
def write_move(move):
    file = open(MOVE_FILENAME, 'r+')
    file.seek(0)
    file.write(NAME+" "+str(move.board_number)+" "+str(move.cell_number)+"\n");
    file.truncate()
    file.close()
    
# -------------------------------------- #
# logging functions
# -------------------------------------- #

def log_filepath():
    return LOG_DIRECTORY + NAME + '-log.txt';

def initial_log():
    if LOGGING:
        date_string = datetime.date.today().strftime("%m/%d/%y");
        with open(log_filepath(), 'w') as logfile:
            logfile.write(f'{NAME} - {date_string}\n');

def log_moves(moves):
    s = 'parsed moves\n';
    for move in moves:
        s += f'[{move.to_string()}]\n';
    log(s)

def log(msg):
    if LOGGING:
        print(msg);
        time_string = datetime.datetime.now().strftime("%H:%M:%S");
        string_to_log = f'{time_string} - {msg}\n';
        with open(log_filepath(), 'a') as logfile:
            logfile.write(string_to_log);

# -------------------------------------- #
# play functions
# -------------------------------------- #

def verify_move(moves, new_move, print_errors):
    valid_move = True;
    boards = init_boards();
    for move in moves:
        boards = apply_move(boards, move);
    
    last_move = moves[-1];
    
    # check that it is in the right place
    if (new_move.board_number != last_move.cell_number) and not check_win_local(boards[last_move.cell_number])[0]:
        valid_move = False;
        if print_errors:
            print(f'INVALID MOVE: [{new_move.to_string()}] wrong local board')

    # check that it is in a neutral board    
    elif check_win_local(boards[new_move.board_number])[0]:
        valid_move = False;
        if print_errors:
            print(f'INVALID MOVE: [{new_move.to_string()}] local board already won')
    
    # check that cell is empty
    elif boards[new_move.board_number][new_move.cell_number] != CellState.EMPTY:
        valid_move = False;
        if print_errors:
            print(f'INVALID MOVE: [{new_move.to_string()}] cell occupied')

    return valid_move;

    
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

def global_tie(boards):
    check_result = check_win_global(boards);
    return check_result[0] and check_result[1] == "DRAW";

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
            wong, opp = count_cells_in_line(line, board)
            #if 2 cells in the line are wong, 3rd is empty and is the move
            if wong == 2: return True
    return False

def is_local_two_in_a_row(board, move):
    global WINNING_LINES
    for line in WINNING_LINES:
        if move in line: 
            wong, opp = count_cells_in_line(line, board)
            #1 current wong, no opp in line
            if wong == 1 and opp == 0: return True
    return False

def is_local_block(board, move):
    global WINNING_LINES
    for line in WINNING_LINES:
        if move in line: 
            wong, opp = count_cells_in_line(line, board)
            #2 current opp, move would block line
            if opp == 2: return True
    return False

#move is (global, local) tuple
def is_global_win(boards, board):
    global WINNING_LINES
    #move does not win local board
    for line in WINNING_LINES:
        if board in line:
            wong, opp = count_boards_in_line(line, boards)
            if wong == 2: return True
    return False
    
def is_global_two_in_a_row(boards, board):
    global WINNING_LINES
    for line in WINNING_LINES:
        if board in line:
            wong, opp = count_boards_in_line(line, boards)
            if wong == 1 and opp == 0: return True
    return False

def is_global_block(boards, board):
    global WINNING_LINES
    for line in WINNING_LINES:
        if board in line:
            wong, opp = count_boards_in_line(line, boards)
            if opp == 2: return True
    return False

#winning lines based on player, if 0, board is dead
def local_winning_lines(board):
    global WINNING_LINES
    wonglines=0
    opplines=0
    for line in WINNING_LINES:
        wong, opp = count_cells_in_line(line, board)
        if wong == 0: opp += 1
        if opp == 0: wong += 1
    return wonglines, opplines

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

#counts useful winning lines a move is a part of
def count_local_move_winning_lines(move, board):
    count = 0
    for line in WINNING_LINES:
        if (move in line) and (count_cells_in_line(line, board)[1] == 0):
            count += 1
    return count

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

# return true if minmax level is a wongtron move
def mm_wongtron_move(depth):
    return depth % 2 == 0; # TODO double check this

def minmax(boards, last_move, deadline, depth, levels_dominant_score):
    result_boards = apply_move(boards, last_move);

    #  check time
    if time() > deadline:
        return INVALID_SCORE;
    
    #  win
    elif wongtron_global_win(result_boards):
        return W_SCORE;

    #  loss
    elif opp_global_win(result_boards):
        return L_SCORE;

    #  tie
    elif global_tie(result_boards):
        return TIE_SCORE;

    # depth reached 
    elif depth >= MINMAX_DEPTH_LIMIT:
        return evaluate(result_boards);

    # gen new moves, minmax on each, prune 
    else:
        possible_moves = find_valid_moves(result_boards, last_move)

        dominant_move = possible_moves[0];
        dominant_score = minmax(result_boards, dominant_move, deadline, depth + 1, None);
        for move in possible_moves[1:]:

            # pruning: return if the levels dominant score leaves this branch unusable # TODO double check this
            if levels_dominant_score is not None:
                if (mm_wongtron_move(depth) and dominant_score < levels_dominant_score): # wong will select a previous branch
                    break;
                if (not mm_wongtron_move(depth) and dominant_score > levels_dominant_score): # opp will select a previous branch
                    break;
            
            score = minmax(result_boards, move, deadline, depth + 1, dominant_score);

            # check if score dominates
            if (score != INVALID_SCORE and 
                (mm_wongtron_move(depth) and score < dominant_score) or (not mm_wongtron_move(depth) and score > dominant_score)): # TODO double check this
                dominant_score = score;
                dominant_move = move;
    
    return dominant_score;

# minmax call for the next wongtron move
def minmax_start(boards, next_wongtron_move_candidate, deadline):
    return minmax(boards, next_wongtron_move_candidate, deadline, 0, None); # TODO double check this

def play(moves, deadline):
    print('thinking... ', end='');
    sys.stdout.flush();
    our_move = None;
    #generate board from moves
    boards = init_boards();
    for move in moves:
        boards = apply_move(boards, move);

    last_move = moves[-1];
    valid_moves = find_valid_moves(boards, last_move);
    
    best_move = valid_moves[0];
    best_move_score = minmax_start(boards, best_move, deadline);

    for move in valid_moves[1:]:
        score = minmax_start(boards, move, deadline);
        if score > best_move_score:
            best_move_score = score;
            best_move = move;
    our_move = best_move;

    if PRINT_CHOSEN_MOVE:
        log(f'move #{len(moves)+1}: [{our_move.to_string()}] score: [{best_move_score}]');
        print(f'playing move: [{our_move.to_string()}]');

    if WAIT_FOR_OK_EACH_TURN:
        input('press enter to continue.');
    return our_move;

# -------------------------------------- #
# evaluation functions
# -------------------------------------- #

# TO-DO ADD weights
def calculate_weight(boards):
    weights = []
    
    weights = []
    for board in range(9):
        win_local = check_win_local(boards[board])
        local_lines = local_winning_lines(boards[board])
        if local_lines[1] == 0: line_ratio = 8*LINE_RATIO_SCALE
        else: line_ratio = local_lines[0]/local_lines[1]*LINE_RATIO_SCALE
        if(is_global_two_in_a_row(boards, board)):
            weights.append(GLOBAL_TWO+line_ratio)
        elif(is_global_block(boards,board)):
            weights.append(GLOBAL_BLOCK+line_ratio)
        elif(not win_local[0]):
            weights.append(FREE_BOARD)
        else:
            weights.append(OTHER_BOARD+line_ratio)
    return weights

def simple_eval(board,board_weights):
    
    #Check if we are in a finished board
    local_win = check_win_local(board)

    if (local_win[0] and local_win[1] == "WONG"):
        return LOCAL_WON
    if (local_win[0] and local_win[1] == "OPP"):
        return LOCAL_LOST
    if (local_win[0] and local_win[1] == "DRAW"):
        return LOCAL_TIED
        
    square_calcs = []

    for square in range(9):

        if (board[square] == CellState.EMPTY):
            
            if (is_local_win(board, square)):
                square_calcs.append(LOCAL_WIN*board_weights[square])
            elif (is_local_block(board,square)):
                square_calcs.append(LOCAL_BLOCK*board_weights[square])
            elif (is_local_two_in_a_row(board,square)):
                square_calcs.append(LOCAL_TWO*board_weights[square])
            else:
                square_calcs.append(LINE_RATIO_SCALE*count_local_move_winning_lines(square, board)*board_weights[square])
        else:
            square_calcs.append(0)

    return sum(list(filter(lambda x: (x),square_calcs)))


def weighted_eval(boards):
    
    board_eval = []
    board_weights = calculate_weight(boards)
    
    for board in range(9):
        board_eval.append(simple_eval(boards[board],board_weights))

    return sum(list(filter(lambda x: (x),board_eval)))


def evaluate(boards):
    
    global_win = check_win_global(boards)
    if (global_win[0] and global_win[1] == "WONG"):
        return W_SCORE
    if (global_win[0] and global_win[1] == "OPP"):
        return L_SCORE

    return weighted_eval(boards)



# -------------------------------------- #
# main
# -------------------------------------- #

def end_game_print(moves):
    moves += parse_new_moves(moves);
    boards = init_boards();
    for move in moves:
        boards = apply_move(boards, move);
    if wongtron_global_win(boards):
        log(f"I win! Muahahahahaaaa");
    elif opp_global_win(boards):
        log(f"Opponent wins. ):");
    elif global_tie(boards):
        log(f"Its a draw.");

def boards_string(boards):
    s = '';
    for board_num, board in enumerate(boards):
        s += str(board_num) + ':\n'
        for i in range(3):
            for j in range(3):
                cell = board[3*i + j];
                if cell == CellState.WONG: s += 'W';
                if cell == CellState.OPP: s += 'O';
                if cell == CellState.EMPTY: s += '.';
                s += ' | ';
            s += '\n';
    return s;

def main():
    # init log
    initial_log();

    # init game state
    state = WongtronState.WAITING_FOR_TURN;
    wait_for_initial_game_files();
    moves = parse_pregame_moves();

    while(True):
        # check for end game
        if file_present(END_GAME_FILENAME):
            end_game_print(moves);
            log("game over");
            break;

        # wait for referee to remove the wongtron.go file
        if state == WongtronState.WAITING_FOR_OPP_TURN:
            if not file_present(NAME + '.go'):
                state = WongtronState.WAITING_FOR_TURN;
                log('waiting for opp')
                sleep(WAIT_REFRESH_SECONDS);
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # wait for wongtron.go file
        elif state == WongtronState.WAITING_FOR_TURN:
            if file_present(NAME + '.go'):
                state = WongtronState.PLAYING;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # play our turn 
        elif state == WongtronState.PLAYING:
            # parse and verify moves
            new_moves = parse_new_moves(moves);
            if len(new_moves) > 0:
                verify_move(moves, new_moves[0], True);
            moves += new_moves;

            # calculate deadline
            deadline = time() + THINKING_TIME;
            log_moves(moves);
            log('calculating next move')
            
            # minimax
            our_move = play(moves, deadline);

            # write/store our move
            moves.append(our_move);
            sleep(MOVE_DELAY_SECONDS);
            write_move(our_move);

            # wait for ref
            state = WongtronState.WAITING_FOR_OPP_TURN;
            log('waiting for ref')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--name', type=str)
    parser.add_argument('--depth', type=int)
    parser.add_argument('--time', type=int)
    parser.add_argument('--log', type=str)
    parser.add_argument('--w_score', type=int)
    parser.add_argument('--l_score', type=int)
    parser.add_argument('--tie_score', type=int)
    parser.add_argument('--global_two', type=int)
    parser.add_argument('--global_block', type=int)
    parser.add_argument('--free_board', type=int)
    parser.add_argument('--other_board', type=int)
    parser.add_argument('--local_win', type=int)
    parser.add_argument('--local_block', type=int)
    parser.add_argument('--local_two', type=int)
    parser.add_argument('--local_won', type=int)
    parser.add_argument('--local_lost', type=int)
    parser.add_argument('--local_tied', type=int)
    parser.add_argument('--line_ratio', type=int)
    args = parser.parse_args();

    if args.name is not None: NAME = args.name;
    if args.depth is not None: MINMAX_DEPTH_LIMIT = args.depth;
    if args.time is not None: THINKING_TIME = args.time;
    if args.w_score is not None: W_SCORE = args.w_score
    if args.l_score is not None: L_SCORE = args.l_score
    if args.tie_score is not None: TIE_SCORE = args.tie_score
    if args.global_two is not None: GLOBAL_TWO = args.global_two
    if args.global_block is not None: GLOBAL_BLOCK = args.global_block
    if args.free_board is not None: FREE_BOARD = args.free_board
    if args.other_board is not None: OTHER_BOARD = args.other_board
    if args.local_win is not None: LOCAL_WIN = args.local_win
    if args.local_block is not None: LOCAL_BLOCK = args.local_block
    if args.local_two is not None: LOCAL_TWO = args.local_two
    if args.local_won is not None: LOCAL_WON = args.local_won
    if args.local_lost is not None: LOCAL_LOST = args.local_lost
    if args.local_tied is not None: LOCAL_TIED = args.local_tied
    if args.line_ratio is not None: LINE_RATIO_SCALE = args.line_ratio

    main();
