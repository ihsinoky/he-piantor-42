"""Record inventory and DC analysis processes in the same frozen runtime."""
from common import *
import sys
W=sys.argv[1];env['OPENBLAS_NUM_THREADS']='1'
assert run('after-route-inventory',['/usr/bin/python3',E/'inspect-boards.py',W],timeout=240)==0
assert run('dc-full-factorial',['/usr/bin/python3',E/'evaluate-dc.py',W],timeout=1200)==0
