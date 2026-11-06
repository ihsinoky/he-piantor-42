from common import *
label=sys.argv[1]
assert run(label+'-independent-inspection',['/usr/bin/python3',E/'inspect-board.py',label],timeout=1800)==0
