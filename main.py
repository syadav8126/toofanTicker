import time
import math
import sys
import subprocess

global s
global e
file=open('fincode.csv','r')
lines = 0
Content = file.read() 
CoList = Content.split("\n") 
for i in CoList: 
	if i: 
		lines += 1
s=0
e=s+50
loop=math.ceil(lines/50)
print(loop)
for i in range(0,loop):
	subprocess.call([sys.executable, './baseInfo.py',str(s),str(e)])
	time.sleep(8)
	s=s+50
	e=e+50
