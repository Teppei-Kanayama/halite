import glob
import itertools
from datetime import datetime


def get_file_content_without_local_import(f):
    content_list = f.readlines()
    content_list = [c for c in content_list if 'from halite.' not in c]
    return ''.join(content_list)


target_directories = ['ship', 'shipyard', 'utils']
target_files = [glob.glob(f'./halite/{d}/*.py') for d in target_directories]
target_files = list(itertools.chain.from_iterable(target_files))

all_files_str = ''

for file in target_files:
    with open(file) as f:
        all_files_str += get_file_content_without_local_import(f)

with open('./halite/agent.py') as f:
    all_files_str += get_file_content_without_local_import(f)

filename = datetime.now().strftime("%m%dT%H%M")
with open(f'agents/submission_{filename}.py', mode='w') as f:
    f.write(all_files_str)
