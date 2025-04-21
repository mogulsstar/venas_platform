import pymysql

try:
    # 连接到MySQL服务器
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='000000'
    )

    cursor = conn.cursor()

    # 创建数据库
    cursor.execute("CREATE DATABASE IF NOT EXISTS venas_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

    print("数据库创建成功！")

    # 关闭连接
    cursor.close()
    conn.close()

except Exception as e:
    print(f"发生错误: {e}")
