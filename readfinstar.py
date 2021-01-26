import finstar
import csv
import sys
import subprocess
from subprocess import Popen
import time

input_file='standalone.csv'
with  open(input_file, 'r') as f:
	data = csv.reader(f)
	for row in data:
		cmd=[sys.executable, './finstar.py',row[0]]
		Popen(cmd,shell=False,stdin=None,stdout=None,stderr=None,close_fds=True)
		time.sleep(0.18)
		#subprocess.call([sys.executable, './finstar.py',row[0]])

