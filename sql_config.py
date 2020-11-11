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
    create_binance_tg = "create table binance_tg (" \
                        "user_name char (10)" \
                        "tg_id int not null," \
                        "b_api_key char(65) not null," \
                        "b_secret_key char(65) not null," \
                        "tg_token char(50) not null)," \
                        "insert_time timestamp DEFAULT CURRENT_TIMESTAMP," \
                        "update_time timestamp default CURRENT_TIMESTAMP" \
                        "UNIQUE (b_api_key)"
    try:
        cursor.execute(create_binance_tg)
        db.commit()
    except:
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
    except:
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
    except:
        return results


if __name__ == '__main__':
    create_table()