Wongtron is an AI that plays Ultimate Tic Tac Toe (UTTT) using a minimax algorithm. 
This program was created in two weeks and placed 5 out of 19 among all the programs produced by the class. 

To play UTTT with Wongtron on Windows, type "python wongtron.py" into one terminal and "python referee.py wongtron 'player2'" into another terminal. 

Wongtron's arguments:
\n--name (string) changes the name wongtron plays under. This is especially helpful to play wongtron against itself. 
--depth (int) changes the depth of the minimax algorithm
--time (int) changes the time wongtron allows itself to think before producing a move
--log (boolean) If true, wongtron will log the moves it parses, the move it produces, and the score of the move
Other arguments are used to optimize the evaluation score

Referee's arguments:
--player_one (string)
--player_two (string)
--time_limit (int) The time limit allowed by the referee. Default = 10
--headless (boolean) Displays the UTTT game. Default = true
