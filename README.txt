Task CLI v0.0.1
Author: Jean Carlos Tomicha Ressa | License: MIT

Entities: p (Projects), t (Tasks), e (Tags), v (Links)

USAGE:
python main.py p --add --name "X" --desc "Y"
python main.py p --list
python main.py p --update 1 --name "Z"
python main.py p --delete 1

python main.py t --add --title "X" --pid 1
python main.py t --list
python main.py t --update 1 --status "done"
python main.py t --delete 1

python main.py e --add --name "X"
python main.py e --list
python main.py e --delete 1

python main.py v --add --tid 1 --eid 1
