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
class State(Enum):
    WAITING_FOR_OPPONENT_TURN = 0; # after our turn, waiting for wongtron.go deletion
    WAITING_FOR_TURN = 1; # waiting to see wongtron.go
    PLAYING = 2;

def file_present(filename):
    cwd = os.getcwd();
    directory_contents = os.listdir(cwd);
    file_present = filename in directory_contents;
    return file_present;

def play():
    pass;

def main():
    state = State.WAITING_FOR_TURN;
    while(True):
        
        # wait for referee to remove the wongtron.go file
        if state == State.WAITING_FOR_OPPONENT_TURN:
            if not file_present(TURN_INDICATOR_FILENAME):
                state = State.WAITING_FOR_TURN;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # wait for wongtron.go file
        elif state == State.WAITING_FOR_TURN:
            if file_present(TURN_INDICATOR_FILENAME):
                state = State.PLAYING;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # play our turn 
        elif state == State.PLAYING:
            play();
            state = State.WAITING_FOR_OPPONENT_TURN;

if __name__ == '__main__':
    main();
