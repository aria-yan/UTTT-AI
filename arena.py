###
### BATTLE ARENA
###

# config
W1_NAME = 'w1';
W2_NAME = 'w2';
DATA_LOG_PATH = './arena-log.txt'

# useful constants
END_GAME_FILENAME = 'end_game';
MOVE_FIENAME = 'move_file';

# derived vars
LOGFILE_ONE = f'{W1_NAME}-log.txt'
LOGFILE_TWO = f'{W2_NAME}-log.txt'
GOFILE_ONE = f'{W1_NAME}.go';
GOFILE_TWO = f'{W2_NAME}.go';

# imports
from time import sleep
from enum import Enum
import subprocess
import datetime
import sys
import os

def clean_env(directorypath):
    # move_file
    move_file_path = os.path.join(directorypath, MOVE_FIENAME);
    if os.path.isfile(move_file_path):
        os.remove(move_file_path);
    # end_game
    endgame_path = os.path.join(directorypath, END_GAME_FILENAME);
    if os.path.isfile(endgame_path):
        os.remove(endgame_path);
    # w1.go
    go_path_1 = os.path.join(directorypath, GOFILE_ONE);
    if os.path.isfile(go_path_1):
        os.remove(go_path_1);
    # w2.go
    go_path_2 = os.path.join(directorypath, GOFILE_TWO);
    if os.path.isfile(go_path_2):
        os.remove(go_path_2);

def parse_winner(directorypath):
    winner = None;
    endgame_path = os.path.join(directorypath, END_GAME_FILENAME);
    if os.path.isfile(endgame_path):
        with open(endgame_path, 'r') as f:
            file_contents = f.read(); 
            if "END: Match TIED!" in file_contents:
                winner = None;
            elif "WINS!" in file_contents:
                winner = file_contents.split()[1];
    return winner;


class Wongtron():
    def __init__(self, name, depth):
        self.depth = depth;
        self.name = name;
        self.sp = None;

    def start(self):
        self.sp = subprocess.Popen([sys.executable, 'wongtron.py',
            '--name', self.name,
            '--depth', str(self.depth)
            ]);
        return self.sp;
    
    def kill(self):
        if (self.sp):
            self.sp.kill();

class Match():
    def __init__(self, w1, w2):
        self.envdir = './';
        self.w1 = w1;
        self.w2 = w2;
        self.winner = None;
        self.endgamemessage = None;

    def run(self):
        clean_env(self.envdir);

        self.w1.start();
        self.w2.start();
        ref = subprocess.Popen([sys.executable, 'referee.py', 'w1', 'w2', '--headless']);

        while not os.path.isfile(END_GAME_FILENAME):
            sleep(1);

        self.w1.kill();
        self.w2.kill();
        ref.terminate();

        winnername = parse_winner(self.envdir)
        if (winnername):
            if (winnername == self.w1.name):
                self.winner = self.w1;
            if (winnername == self.w2.name):
                self.winner = self.w2;

        endgame_path = os.path.join(self.envdir, END_GAME_FILENAME);
        if os.path.isfile(endgame_path):
            with open(endgame_path, 'r') as f:
                self.endgamemessage = f.read(); 

        return self.winner;

    def match_results_string(self):
        s = f'{self.w1.name}: depth={str(self.w1.depth)}\n'
        s += f'{self.w2.name}: depth={str(self.w2.depth)}\n'
        if self.winner:
            s += f'winner: {self.winner.name}\n';
        else:
            s += 'tie\n';
        s += self.endgamemessage;
        s += '\n\n';
        return s;

def log(msg):
    print(msg);
    time_string = datetime.datetime.now().strftime("%H:%M:%S");
    msg_to_log = f'[{time_string}]\n{msg}\n';
    with open(DATA_LOG_PATH, 'a') as log:
        log.write(msg_to_log)

def main():
    for i in range(10):
        w1 = Wongtron('w1', 2);
        w2 = Wongtron('w2', 2);
        match = Match(w1, w2);
        match.run();
        results = match.match_results_string();
        log(results);


if __name__ == "__main__":
    main();