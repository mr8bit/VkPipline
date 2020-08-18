## Скрипты для загрузки постов пользователей

#### Загрузка постов с групп и пабликов

`parser.py` - Загрузка постов с групп и пабликов

На вход, список групп, на выходе  со всеми постами и всеми данными о постах

Пример запуска:

`python parser.py -login 79145467052 -password 3325cfv -input_file group_vk.txt -output_file output. -batch_size 25 -max_repeat 1 `


## Pipeline Vk API
### User
`pipeline/user.py` - пайпы которые относятся только к пользователям

#### GetUserMentionsPipeline
Получить все возможные обращения к пользователю

```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

**Example**

```python
from pipeline import user
from sklearn.pipeline import Pipeline

clearing = Pipeline([
    ('user_mentions', user.GetUserMentionsPipeline()),
])
tf = clearing.transform("https://vk.com/mzadornov")
#tf = clearing.transform([1,33,43123])
```
**Output** 
```
[{87896266: [{'id': 77442,
    'from_id': 144646146,
    'to_id': 137593188,
    'date': 1597163002,
    'post_id': 77441,
    'post_type': 'reply',
    'text': '[id87896266|Михаил Задорнов] ✌🏻😎✌🏻🇷🇺',
    'post_source': {'type': 'vk'},
    'comments': {'count': 0, 'can_post': 0},
    'likes': {'count': 3, 'user_likes': 0, 'can_like': 1, 'can_publish': 1},
    'reposts': {'count': 0, 'user_reposted': 0},
    'is_favorite': False},
    ...]}]
```
#### GetUserGroupsPipeline
Получить список групп в которых состоит пользователь

```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```
**Example**
```python
from pipeline import user
from sklearn.pipeline import Pipeline

clearing = Pipeline([
    ('user_groups', user.GetUserGroupsPipeline()),
])
tf = clearing.transform("https://vk.com/mzadornov")
#tf = clearing.transform([1,33,43123])
```
**Output** 
```
[{87896266: [27938289, 55290352, 38875204, 47245446, 23471538, 30643528]}]
```

#### GetUserSubscriptionPipeline
Получить список пабликов на которые подписан пользователь

```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

**Example**
```python
from pipeline import user
from sklearn.pipeline import Pipeline

clearing = Pipeline([
    ('user_subs', user.GetUserSubscriptionPipeline()),
])
tf = clearing.transform("https://vk.com/mzadornov")
#tf = clearing.transform([1,33,43123])
```
**Output** 
```
[{87896266: [23471538, 27938289, 30643528, 38875204, 47245446, 55290352]}]
```

#### GetUserFriendPipeline
Получить список друзей пользователя

```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

**Example**
```python
from pipeline import user
from sklearn.pipeline import Pipeline

clearing = Pipeline([
    ('user_friends', user.GetUserFriendPipeline()),
])
tf = clearing.transform("https://vk.com/mzadornov")
#tf = clearing.transform([1,33,43123])
```
**Output** 
```
[{87896266: [687426,
   8379667,
   17556755,
   30538603,
   174594973,
   184896543,
   193764464,
   368933704]}]
```

### Posts
`pipeline/posts.py` - пайпы которые относятся только к текстовым данным

#### GetAllTextPostsFromUserPipeline

Получить весь текст постов.

Заберт все посты у которых больше 5 слов в тексте (с учетом текста репоста)

**max_repeat_count** - количество повторов цикла, то есть сколько раз надо будет пройтись по стене пользователя загружая по 100 постов 


```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

```python
from pipeline import posts
from sklearn.pipeline import Pipeline

clearing = Pipeline([
    ('groups_textPosts', posts.GetAllTextPostsFromUserPipeline(max_repeat_count=0)),
])
tf = clearing.transform("https://vk.com/mzadornov")
#tf = clearing.transform([1,33,43123])
```

```
[{87896266: ['#Задорнов #конкурс #книги ... ..... .ru',]}]
```


#### GetAllTextPostsFromUserPipeline

Получить весь текст постов c стены группы/паблика

Заберт все посты у которых больше 5 слов в тексте (с учетом текста репоста)

**max_repeat_count** - количество повторов цикла, то есть сколько раз надо будет пройтись по стене пользователя загружая по 100 постов 


```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

```python
from pipeline import posts
from sklearn.pipeline import Pipeline

clearing = Pipeline([
    ('user_textPosts', posts.GetAllTextPostsFromUserPipeline(max_repeat_count=0)),
])
tf = clearing.transform("https://vk.com/mnzador")
#tf = clearing.transform([1,33,43123])
```

```
[{27938289: ['Фотоальбомы "Задорные наблюдашки". Собрано 40000. \n \nПравила добавлений vk.cc/1i4gLg...', ... ]}]_
```


### Photos
`pipeline/posts.py` - пайпы которые относятся только к фотографиям

#### GetGroupPhotosPipeline

Получить список фотографий с учетом размера и типа фотоальбома 

**max_repeat_count** - количество повторов цикла, то есть сколько раз надо будет пройтись по стене пользователя загружая по 100 постов <br/>
**sizes** - размер фотографии (рекомендую использовать размер `x`) <br/>
**photo_type** - тип альбома  `wall` или `profile` <br/>


```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

```python
from pipeline import photos
from sklearn.pipeline import Pipeline
clearing = Pipeline([
    ('group_photo', photos.GetGroupPhotosPipeline(max_repeat_count=0, sizes=['x'], photo_type='profile')),
])
tf = clearing.transform("https://vk.com/mnzador")
#tf = clearing.transform([1,33,43123])
```

```
[{27938289: [{'date': 1408020284,
    'image': ['https://sun9-33.userapi.com/ndV51Ztcw_xmMRxbcK-BYcBjeyNtJy7bz8uc6A/-GNDpjKnggI.jpg']},
   {'date': 1450794156,
    'image': ['https://sun9-67.userapi.com/c629430/v629430406/2c3a4/xXzSrDfwFFU.jpg']}]}]
```

#### GetUserPhotoPipeline

Получить список фотографий с учетом размера и типа фотоальбома 

**max_repeat_count** - количество повторов цикла, то есть сколько раз надо будет пройтись по стене пользователя загружая по 100 постов <br/>
**sizes** - размер фотографии (рекомендую использовать размер `x`) <br/>
**photo_type** - тип альбома  `wall` , `profile` или `saved` <br/>


```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

```python
from pipeline import photos
from sklearn.pipeline import Pipeline
clearing = Pipeline([
    ('user_photo', photos.GetUserPhotoPipeline(max_repeat_count=0, sizes=['x'], photo_type='profile')),
])
tf = clearing.transform("https://vk.com/mnzador")
#tf = clearing.transform([1,33,43123])
```

```
[{87896266: [{'date': 1538472271,
    'image': ['https://sun1-86.userapi.com/c850436/v850436168/156b9/cb1OqydQcGs.jpg']},
 ... ]}]
```


### Group
`pipeline/groups.py` - пайпы которые относятся только к группе

#### GetUsersFromGroupPipeline

Получить всех пользователей из группы

**max_repeat_count** - количество повторов цикла, то есть сколько раз надо будет пройтись по стене пользователя загружая по 1000 постов <br/>

```Принимает на вход два типа данных:
str - ссылка на пользователя
list - массив id'шников пользователей
```

```python
from pipeline import group
from sklearn.pipeline import Pipeline
clearing = Pipeline([
    ('member_group', group.GetUsersFromGroupPipeline(max_repeat_count=0)),
])
tf = clearing.transform("https://vk.com/lambdamai")
#tf = clearing.transform([1,33,43123])
```

```
[{105873414: [24147,
   74372,
   112394,
   160502,
   301541,
   327023,
   719314,
   771358,
   787248, ... ]}]
```


### Ml

`pipeline/ml` - пайпы которые относятся к интелектуальной обработке

#### ClassificationNSFWContentPipeline

Классфикация пользовательских изображений на NSFW контент. 
Модель взята от https://github.com/GantMan/nsfw_model

**model_path** - путь к модели <br/>
**threshold_prediction** - пороговое значение для классфикации
 
**Example**

```python
from sklearn.pipeline import Pipeline
from pipeline import photos
from pipeline.ml import nsfw
clearing = Pipeline([
    ('user_photos', photos.GetUserPhotoPipeline(max_repeat_count=0, sizes=['x'], photo_type='wall')),
    ('nsfw_content', nsfw.ClassificationNSFWContentPipeline(model_path='./models/nsfw.299x299.h5'))
])
tf = clearing.transform("https://vk.com/satanoll")
```
**Output**
```
[{332256187: {'hentai': 0,
   'drawings': 0,
   'neutral': 13,
   'porn': 0,
   'sexy': 0}}]
```
