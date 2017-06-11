import MySQLdb


class DataPersistance():
    def __init__(self):
        self.host = 'localhost'
        self.username = 'root'
        self.password = 'password'
        self.database = 'ket'
        self.port = 3306

    def obtain_connect(self):
        connect = MySQLdb.connect(host=self.host,
                                  user=self.username,
                                  password=self.password,
                                  database=self.database,
                                  port=self.port)
        return connect

    def obtain_cursor(self):
        cursor = self.obtain_connect().cursor()
        return cursor

    def add_data(self, partnumber, dic):
        for k, v in dic.items():
            product_type = k
            url = v

            db = self.obtain_connect()
            cursor = db.cursor()
            SQL_ADD = 'INSERT INTO result(pn,url , product_type) VALUES ("%s","%s","%s")' % (partnumber, url, product_type)
            SQL_SEARCH = 'SELECT pn, url, product_type FROM result WHERE pn = "%s" and url = "%s" and product_type ="%s"' % (partnumber, url, product_type)
            try:
                cursor.execute(SQL_SEARCH)
                result = cursor.fetchall()
                if len(result) == 0:
                    cursor.execute(SQL_ADD)
                    print(SQL_ADD)
                    db.commit()
                    print('数据写入成功：%s, %s, %s' % (partnumber, url, product_type))
                else:
                    print("数据已存在")
            except Exception as e:
                db.rollback()
                print(e)
            db.close()

