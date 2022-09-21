#  WONGTRON
#  CS4341
#  Aria Yan
#  Jacob Salerno
#  Nestor Lopez

from time import sleep
from enum import Enum

# wongtron config variables
WAIT_REFRESH_SECONDS = 0.1;

# wongtron state enum
class State(Enum):
    WAITING_FOR_OPPONENT_TURN = 0; # after our turn, waiting for wongtron.go deletion
    WAITING_FOR_TURN = 1; # waiting to see wongtron.go
    PLAYING = 2;

def turn_file_present():
    print('checking for turn file');
    return False;

def play():
    pass;

def main():
    state = State.WAITING_FOR_TURN;
    while(True):
        
        # wait for referee to remove the wongtron.go file
        if state == State.WAITING_FOR_OPPONENT_TURN:
            if not turn_file_present():
                state = State.WAITING_FOR_TURN;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # wait for wongtron.go file
        if state == State.WAITING_FOR_TURN:
            if turn_file_present():
                state = State.PLAYING;
            else:
                sleep(WAIT_REFRESH_SECONDS);

        # play our turn 
        if state == State.PLAYING:
            play();
            state = State.WAITING_FOR_OPPONENT_TURN;

if __name__ == '__main__':
    main();
