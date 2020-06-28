import glob
import itertools
from datetime import datetime


target_directories = ['ship', 'shipyard', 'utils']
target_files = [glob.glob(f'./halite/{d}/*.py') for d in target_directories]
target_files = list(itertools.chain.from_iterable(target_files))

all_files_str = ''
for file in target_files:
    with open(file) as f:
        s = f.read()
        all_files_str += s

with open('./halite/agent.py') as f:
    s = f.read()
    all_files_str += s

now = datetime.now()
filename = now.strftime("%m%dT%H%M")
with open(f'agents/submission_{filename}.py', mode='w') as f:
    f.write(all_files_str)
