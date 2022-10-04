import subprocess;

def main():
    w1 = subprocess.Popen(['python', 'wongtron.py', '--name', 'w1']);
    w2 = subprocess.Popen(['python', 'wongtron.py', '--name', 'w2']);
    ref = subprocess.Popen(['python', 'referee.py', 'w1', 'w2']);
    input('press enter to kill');
    w1.kill();
    w2.kill();
    ref.kill();

if __name__ == "__main__":
    main();