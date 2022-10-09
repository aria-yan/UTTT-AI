from time import sleep
import subprocess
import sys

def main():
    w1 = subprocess.Popen([sys.executable, 'wongtron.py', '--name', 'w1']);
    w2 = subprocess.Popen([sys.executable, 'wongtron.py', '--name', 'w2']);
    ref = subprocess.Popen([sys.executable, 'referee.py', 'w1', 'w2', '--headless']);
    while 1:
        sleep(1);
    w1.kill();
    w2.kill();
    ref.kill();

if __name__ == "__main__":
    main();