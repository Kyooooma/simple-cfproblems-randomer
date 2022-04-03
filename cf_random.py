import random
from time import *
import requests
from sqlalchemy import create_engine
from config.secure import SQLALCHEMY_DATABASE_URI


def getJson(url):  # 访问api并返回json格式
    while True:
        try:
            html = requests.get(url)
            html = html.json()
            break
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            sleep(3)
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            sleep(3)
    return html


def getAcList(username):  # 获取user的ac题目集
    url = 'https://codeforces.com/api/user.status?handle=' + username
    ac_list = []
    info = getJson(url)
    if info['status'] != 'OK':
        print('getAcList status false!! Username = ' + username)
        return []
    info = info['result']
    for i in info:
        verdict = i['verdict']
        if (verdict != 'OK') or ('problem' not in i):
            continue
        j = i['problem']
        if ('contestId' not in j) or ('index' not in j):
            continue
        pid = str(j['contestId']) + j['index']
        ac_list.append(pid)
    return ac_list


def getAllProblemsInfo(banned_list):  # 获取cf所有题目的id和rating并将special problem删去
    url = 'https://codeforces.com/api/problemset.problems'
    problems = []
    info = getJson(url)
    banned_set = set(banned_list)  # 去重并加快查询速度(但由于数量太少并没有比直接查询list快多少
    if info['status'] != 'OK':
        print('getAllPid status false!!')
        return []
    info = info['result']['problems']
    for i in info:
        if ('rating' not in i) or ('contestId' not in i) or ('index' not in i) or ('tags' not in i):
            continue
        pid = str(i['contestId']) + i['index']
        if pid in banned_set:
            continue
        if '*special' in i['tags']:
            continue
        problems.append({
            'id': pid,
            'rating': i['rating'],
            'link': 'https://codeforces.com/contest/{}/standings/friends/true'.format(i['contestId'])
            # 生成周赛题目时用来康康有没有人做过或者是不是什么奇怪的场次捏
        })
    return problems


def getUsersHandle():  # 获取users的cf id (并没有使用 因为同时ban掉所有人太慢了
    users = []
    db = create_engine(SQLALCHEMY_DATABASE_URI)
    res = db.execute('''
        select username, oj_username
        from oj_username,
             oj
        where oj.id = oj_username.oj_id
            and oj.name = 'codeforces'
            and username in (
                select username
                from user
                where user.status = 1
            )
        order by username
    ''').fetchall()
    for username, oj_username in res:
        users.append(oj_username)
    return users


def getBannedList(user_list):  # ban掉已ac的题目
    print("Start_Get_Banned_List")
    banned_problems = []
    for i in user_list:
        print(i)
        ac_list = getAcList(i)
        for j in ac_list:
            banned_problems.append(j)
    print("Get_Banned_List_Success")
    return banned_problems


def getRandomProblems(problem_set, num):  # 从problem_set中随机选num题
    vis = []
    for i in range(0, num):
        idx = random.randint(0, len(problem_set) - 1)
        while vis.count(problem_set[idx]) != 0:
            idx = random.randint(0, len(problem_set) - 1)
        vis.append(problem_set[idx])
    for i in vis:
        print('id: ' + i.get('id') + '   link: ' + i.get('link'))
        # print(i)


def Personal_gen():  # 个人训练题目生成
    print("Start_Get_Personal_Contest")
    rating_l = 1800  # 设置最低rating
    rating_r = 2200  # 设置最高rating
    cnt = 4  # 设置数量
    users = ['Kyooma']  # 设置banned_user, 防止生成ac过的题目
    all_set = getAllProblemsInfo(banned_list=getBannedList(users))
    problem_set = []
    for i in all_set:
        rating = int(i.get('rating'))
        if rating_l <= rating <= rating_r:
            problem_set.append(i)
    getRandomProblems(problem_set, cnt)
    print("Get_Personal_Contest_Success")


def Weekly_gen():  # 周赛题目生成
    users = ['Yinghuo', 'Kyooma', '333lfy', 'zty_123', 'Hile_Meow']  # 设置banned_user, 防止生成ac过的题目
    all_set = getAllProblemsInfo(banned_list=getBannedList(users))
    print("Start_Get_Weekly_Contest")
    problem_set1 = []
    problem_set2 = []
    problem_set3 = []
    for i in all_set:
        rating = int(i.get('rating'))
        if 1200 <= rating <= 1700:
            problem_set1.append(i)
        elif 1800 <= rating <= 2000:
            problem_set2.append(i)
        elif 2100 <= rating <= 2300:
            problem_set3.append(i)
    for i in range(0, 1):
        getRandomProblems(problem_set1, 3)
        getRandomProblems(problem_set2, 2)
        getRandomProblems(problem_set3, 2)
        print("")
    print("Get_Weekly_Contest_Success")


if __name__ == "__main__":
    start_time = time()
    # Personal_gen()
    Weekly_gen()
    end_time = time()
    print('Progress success in {}s'.format(end_time - start_time))
