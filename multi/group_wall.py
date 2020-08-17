from celery import Celery
import vk_api



app = Celery('data_collect', broker='redis://localhost:6379/0')



def get_all_post_from_group(login, password, max_repeat_count, batches):
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    vk = vk_session.get_api()

    for group in batches:
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
                    resp = vk.wall.get(owner_id=owner_id * -1, offset=0, count=100)
                    offset+=100
                    f.write(str(resp['items'])[1:-1])
                    if post_100 == max_repeat_count:
                        break
