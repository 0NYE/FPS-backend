import pymysql
import configparser

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

class Database:
    def __init__(self):
        self.db = pymysql.connect(
            host = config['DATABASE']['HOST'],
            user = config['DATABASE']['USER'],
            password = config['DATABASE']['PASSWORD'],
            db = config['DATABASE']['DB'],
            port = int(config['DATABASE']['PORT']),
            charset = config['DATABASE']['CHARSET']
        )
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
        
    def execute(self, query, args={}):
        self.cursor.execute(query, args)
    
    # fetchone()은 한번 호출에 하나의 Row 만을 가져올 때 사용된다.
    def execute_one(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()    
        return row
    
    # fetchall() 메서드는 모든 데이터를 한꺼번에 가져올 때 사용된다.
    def execute_all(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()    
        return row

    def commit(self):
        self.db.commit()

    def close(self):
        self.cursor.close()
        
        
# pymysql로 쿼리문 테스트 -> 230514 테스트 완료
'''
database = Database()

sql = """ 
    CREATE TABLE product(
        PRODUCT_CODE VARCHAR(20) NOT NULL,
        TITLE VARCHAR(200) NOT NULL,
        ORI_PRICE INT,
        DISCOUNT_PRICE INT,
        DISCOUNT_PERCENT INT,
        DELIVERY VARCHAR(2),
        PRIMARY KEY(PRODUCT_CODE)
);
"""
database.execute(sql) 

database.commit() 

database.close()
'''