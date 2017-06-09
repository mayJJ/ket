import MySQLdb


class DataPersistance():
    def __init__(self):
        self.host = 'localhost'
        self.username = 'root'
        self.password = 'ymj710823'
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

    def add_data(self,partnumber,datasheet1,datasheet2):
        db = self.obtain_connect()
        cursor = db.cursor()
        SQL_ADD = 'INSERT INTO t_result(partnumber,datasheet1,datasheet2) VALUES ("%s","%s","%s")' %(partnumber, datasheet1,datasheet2)
        try:
            print(SQL_ADD)
            cursor.execute(SQL_ADD)
            print('数据写入成功：%s, %s, %s' % (partnumber, datasheet1, datasheet2))
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
        db.close()

