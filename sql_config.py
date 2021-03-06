import pymysql

from config import mysql_info


def create_table():
    """
    Create table
    """
    # 打开数据库连接
    db = pymysql.connect(mysql_info['host'], mysql_info['user'], mysql_info['password'], mysql_info['database'])

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 创建表
    create_binance_tg = "create table IF NOT EXISTS binance_tg (" \
                        "user_name char(10)," \
                        "api_lable char(15)," \
                        "tg_id int not null," \
                        "b_api_key char(65) not null," \
                        "b_secret_key char(65) not null," \
                        "tg_token char(50) not null," \
                        "insert_time timestamp default current_timestamp()," \
                        "update_time timestamp default current_timestamp()," \
                        "UNIQUE (b_api_key)" \
                        ")"
    # 测试表
    create_binance_tg_t = "create table IF NOT EXISTS binance_tg_t (" \
                        "user_name char(10)," \
                        "api_lable char(15)," \
                        "tg_id int not null," \
                        "b_api_key char(65) not null," \
                        "b_secret_key char(65) not null," \
                        "tg_token char(50) not null," \
                        "insert_time timestamp default current_timestamp()," \
                        "update_time timestamp default current_timestamp()," \
                        "UNIQUE (b_api_key)" \
                        ")"

    try:
        cursor.execute(create_binance_tg)
        cursor.execute(create_binance_tg_t)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    # 关闭数据库连接
    db.close()


def insert_data(insert_sql):
    """
    Insert data
    """
    # 打开数据库连接
    db = pymysql.connect(mysql_info['host'], mysql_info['user'], mysql_info['password'], mysql_info['database'])

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    try:
        cursor.execute(insert_sql)
        db.commit()
        # 关闭数据库连接
        db.close()
        return True
    except Exception as e:
        print(e)
        db.rollback()
        return False


def select_data(select_sql):
    """
    Select data from table
    """
    results = []
    # 打开数据库连接
    db = pymysql.connect(mysql_info['host'], mysql_info['user'], mysql_info['password'], mysql_info['database'])

    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()

    try:
        cursor.execute(select_sql)
        results = cursor.fetchall()
        # 关闭数据库连接
        db.close()
        return results
    except Exception as e:
        print(e)
        return results


if __name__ == '__main__':
    create_table()