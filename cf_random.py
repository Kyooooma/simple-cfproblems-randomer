import random
from time import *
import requests
from sqlalchemy import create_engine
from config.secure import SQL_DATABASE_URI


def getJson(url):
    # 访问api并返回json格式
    while True:
        try:
            # 用get请求获取数据
            html = requests.get(url)
            # 转换为json
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


def getAllAcList():
    # 获取数据库中所有人做过的题目列表
    s_time = time()
    try:
        ac_list = []
        # 链接数据库获取数据
        db = create_engine(SQL_DATABASE_URI)
        res = db.execute('''
                    select problem_pid
                    from problem
                    where id in (
                        select distinct problem_id
                        from accept_problem
                        where username in (
                            select username
                            from user
                            where status = 1
                            )
                    )
                      and oj_id = 2
                ''').fetchall()
        for i in res:
            ac_list.append(i[0])
        e_time = time()
        print('Start_Get_All_ac_list_Success and costs {}s'.format(e_time - s_time))
        return ac_list
    except:
        e_time = time()
        print('Start_Get_All_ac_list_Fail and costs {}s'.format(e_time - s_time))
        return []


def getPersonalAcList():
    # 获取特定某个人通过的题目
    print('Start_Get_Personal_ac_list')
    s_time = time()
    try:
        ac_list = []
        db = create_engine(SQL_DATABASE_URI)
        res = db.execute('''
                    select problem_pid
                    from problem
                    where id in (
                        select distinct problem_id
                        from accept_problem
                        where username = '32001267'
                    )
                      and oj_id = 2
                ''').fetchall()
        for i in res:
            ac_list.append(i[0])
        e_time = time()
        print('Get_Personal_ac_list_Success and costs {}s'.format(e_time - s_time))
        return ac_list
    except:
        e_time = time()
        print('Get_Personal_ac_list_Fail and costs {}s'.format(e_time - s_time))
        return []


def getAllProblemsInfo(banned_list, tags=None):
    # 获取codeforces所有题目的id和rating 并将special problem删去
    s_time = time()
    url = 'https://codeforces.com/api/problemset.problems'
    if tags is not None:
        url = 'https://codeforces.com/api/problemset.problems?tags='
        for i in tags:
            url = url + i + ';'
        print(url)
    problems = []
    info = getJson(url)
    # 去重并加快查询速度(但由于数量太少并没有比直接查询list快多少
    banned_set = set(banned_list)
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
            # 生成周赛题目时用来康康有没有人做过或者是不是什么奇怪的场次
        })
    e_time = time()
    print('getAllProblemsInfo costs {}s'.format(e_time - s_time))
    # print(problems)
    return problems


def getRandomProblems(problem_set, num):
    # 从problem_set中随机选num题
    vis = []
    for i in range(0, num):
        idx = random.randint(0, len(problem_set) - 1)
        while vis.count(problem_set[idx]) != 0:
            idx = random.randint(0, len(problem_set) - 1)
        vis.append(problem_set[idx])
    return vis


def Personal_gen(tags=None):
    # 个人训练题目生成
    rating_l = 1800  # 设置最低rating
    rating_r = 2200  # 设置最高rating
    cnt = 6  # 设置数量
    try:
        all_set = getAllProblemsInfo(banned_list=getPersonalAcList(), tags=tags)
        problem_set = []
        for i in all_set:
            rating = int(i.get('rating'))
            if rating_l <= rating <= rating_r:
                problem_set.append(i)
        for j in range(0, 5):
            t = getRandomProblems(problem_set, cnt)
            random.shuffle(t)
            for i in t:
                print('pid: {}, link: {}'.format(i.get('id'), i.get('link')))
            print('')
        print("Get_Personal_Contest_Success")
    except:
        print("Get_Personal_Contest_Fail")


def Weekly_gen(tags=None):
    # 周赛题目生成
    problem_set1 = []
    problem_set2 = []
    problem_set3 = []
    try:
        all_set = getAllProblemsInfo(banned_list=getAllAcList(), tags=tags)
        for i in all_set:
            rating = int(i.get('rating'))
            if 1200 <= rating <= 1700:
                problem_set1.append(i)
            elif 1800 <= rating <= 2000:
                problem_set2.append(i)
            elif 2100 <= rating <= 2300:
                problem_set3.append(i)

        for i in range(0, 5):
            t = [getRandomProblems(problem_set1, 3), getRandomProblems(problem_set2, 2),
                 getRandomProblems(problem_set3, 2)]
            used = []
            for j in t:
                for p in j:
                    used.append(p)
            random.shuffle(used)
            for j in used:
                print('pid: {}, link: {}'.format(j.get('id'), j.get('link')))
                # print(j)
            print("")
        print("Get_Weekly_Contest_Success")
    except:
        print("Get_Weekly_Contest_Fail")


if __name__ == "__main__":
    start_time = time()
    # Personal_gen()
    Weekly_gen()
    end_time = time()
    print('Progress success in {}s'.format(end_time - start_time))
