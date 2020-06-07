import pymysql
import time
import json
import traceback
import requests


def get_tencent_data():
    """
    :return: 返回历史数据和当日详细数据
    """
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other'
    url2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36',
        'Referer': ' https://news.qq.com/zt2020/page/feiyan.htm'
    }
    r = requests.get(url, headers)
    r2 = requests.get(url2, headers)
    res = json.loads(r.text)  # json字符串转字典
    res2 = json.loads(r2.text)
    data_all = json.loads(res['data'])
    data_all2 = json.loads(res2['data'])
    # print(data_all2)

    history = {}  # 历史数据
    for i in data_all["chinaDayList"]:
        ds = "2020." + i["date"]
        tup = time.strptime(ds, "%Y.%m.%d")
        ds = time.strftime("%Y-%m-%d", tup)  # 改变时间格式,不然插入数据库会报错，数据库是datetime类型
        confirm = i["confirm"]
        suspect = i["suspect"]
        heal = i["heal"]
        dead = i["dead"]

        history[ds] = {"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead}
    i = data_all2["chinaTotal"]
    ds = "2020.06.04"
    tup = time.strptime(ds, "%Y.%m.%d")
    ds = time.strftime("%Y-%m-%d", tup)
    confirm = i["confirm"]
    suspect = i["suspect"]
    heal = i["heal"]
    dead = i["dead"]
    history[ds].update({"confirm_add": confirm, "suspect_add": suspect, "heal_add": heal, "dead_add": dead})

    details = []  # 当日详细数据
    update_time = data_all2["lastUpdateTime"]
    data_country = data_all2["areaTree"]  # list 25个国家
    data_province = data_country[0]["children"]  # 中国各省
    for pro_infos in data_province:
        province = pro_infos["name"]  # 省名
        for city_infos in pro_infos["children"]:
            city = city_infos["name"]
            confirm = city_infos["total"]["confirm"]
            confirm_add = city_infos["today"]["confirm"]
            heal = city_infos["total"]["heal"]
            dead = city_infos["total"]["dead"]
            details.append([update_time, province, city, confirm, confirm_add, heal, dead])
    return history, details


def get_conn():
    """
    :return: 连接，游标l
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="wa131452",
                           db="test",
                           charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor


def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def update_details():
    """
    更新 details 表
    :return:
    """
    cursor = None
    conn = None
    try:
        li = get_tencent_data()[1]  # 0 是历史数据字典,1 最新详细数据列表
        conn, cursor = get_conn()
        sql = "insert into main_app_details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
        sql_query = 'select %s=(select update_time from main_app_details order by id desc limit 1)'  # 对比当前最大时间戳
        cursor.execute(sql_query, li[0][0])
        if not cursor.fetchone()[0]:
            print(f"{time.asctime()}开始更新最新数据")
            for item in li:
                cursor.execute(sql, item)
            conn.commit()  # 提交事务 update delete insert操作
            print(f"{time.asctime()}更新最新数据完毕")
        else:
            print(f"{time.asctime()}已是最新数据！")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


def insert_history():
    """
        插入历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dic = get_tencent_data()[0]  # 0 是历史数据字典,1 最新详细数据列表
        print(f"{time.asctime()}开始插入历史数据")
        conn, cursor = get_conn()
        sql = "insert into main_app_history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for k, v in dic.items():
            # item 格式 {'2020-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
            cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                 v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                 v.get("dead"), v.get("dead_add")])

        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}插入历史数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


def update_history():
    """
    更新历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dic = get_tencent_data()[0]  # 0 是历史数据字典,1 最新详细数据列表
        print(f"{time.asctime()}开始更新历史数据")
        conn, cursor = get_conn()
        sql = "insert into main_app_history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql_query = "select confirm from main_app_history where ds=%s"
        for k, v in dic.items():
            # item 格式 {'2020-03-28': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
            if not cursor.execute(sql_query, k):
                cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                     v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                     v.get("dead"), v.get("dead_add")])
        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}历史数据更新完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)


if __name__ == "__main__":
    update_details()
    update_history()
