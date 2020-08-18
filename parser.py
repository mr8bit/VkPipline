import vk_api
import os
from reader import get_batches
import time
from tqdm import tqdm

import argparse

"""
Example run 
python parser.py -login 79145467052 -password 3325cfv -max_repeat 1 
"""

parser = argparse.ArgumentParser()
parser.add_argument("-login", type=str,help="vk login")
parser.add_argument("-password", type=str,help="password vk")
parser.add_argument("-input_file", type=str,help="File with vk group", default="group_vk.txt")
parser.add_argument("-output_file", type=str,help="Output file with post", default='output_file.json')
parser.add_argument("-batch_size", type=int,help="Output file with post", default=25)
parser.add_argument("-max_repeat", type=int,help="Output file with post", default=5)
args = parser.parse_args()


vk_session = vk_api.VkApi(args.login, args.password)
vk_session.auth()
vk = vk_session.get_api()

group_file = open(args.input_file, "r")
group_list = group_file.readlines()
group_list = [x.strip() for x in group_list]
group_file.close()

group_batches = get_batches(group_list, args.batch_size)

max_repeat_count = args.max_repeat

f = open(args.output_file, "w")
f.write("[")

for batch in tqdm(group_batches):
    time.sleep(0.4)
    for group in batch:
        print(group)
        screen_name = group.split('/')[-1]
        resp = vk.utils.resolveScreenName(screen_name=screen_name)
        if resp['type'] =='group':
            owner_id = resp['object_id']
            resp = vk.wall.get(owner_id=owner_id*-1, offset = 0, count=1)
            if resp['count']>100:
                repeat_post = int(resp['count']/100)
                offset = 0
                for post_100 in range(repeat_post):
                    time.sleep(0.4)
                    resp = vk.wall.get(owner_id=owner_id * -1, offset=0, count=100)
                    offset+=100
                    f.write(str(resp['items'])[1:-1])
                    if post_100 == max_repeat_count:
                        break

f.write("]")
f.close()
