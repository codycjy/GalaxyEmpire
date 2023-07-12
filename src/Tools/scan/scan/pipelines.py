# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql


class ScanPipeline:
    def process_item(self, item, spider):
        return item


class DbPipeline:
    def __init__(self):
        # self.config = None
        self.conn = pymysql.connect(host='localhost', user='galaxy', password='', db='galaxyscan', charset='utf8mb4',
                                    database='galaxyscan')
        self.cur = self.conn.cursor()

    def open_spider(self, spider):
        self.config = spider.kwargs
        self.server=self.config.get('server')
        self.create_table()

    def create_table(self):
        tablename = self.config.get('server')
        self.table = tablename
        sql = f"DROP table  IF EXISTS {tablename};"
        self.cur.execute(sql)
        sql = f"create table {tablename} (id int auto_increment primary key," \
              f"name varchar(40) not null," \
              f"pos varchar(20) not null ," \
              f" crystal int , " \
              f"metal int," \
              f"has_ally int," \
              f"ally_name varchar(40));"
        self.cur.execute(sql)
        self.conn.commit()

    def close_spider(self, spider):
        from datetime import datetime

        print("close spider")
        # 获取当前时间戳
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 检查服务器是否存在
        select_query = "SELECT id FROM servers_status WHERE server_name = %s"
        self.cur.execute(select_query, (self.server,))
        result = self.cur.fetchone()
        print(result)

        if result:
            # 更新最后更新时间戳
            update_query = "UPDATE servers_status SET last_updated = %s WHERE id = %s"
            self.cur.execute(update_query, (current_timestamp, result[0]))
        else:
            # 插入新服务器记录
            insert_query = "INSERT INTO servers_status (server_name, last_updated) VALUES (%s, %s)"
            self.cur.execute(insert_query, (self.server, current_timestamp))
            self.conn.commit()

        # 关闭数据库连接和游标
        self.cur.close()
        self.conn.close()

    def process_item(self, item: dict, spider):
        self.cur.execute(f"insert into {self.table}(name,pos,crystal,metal,has_ally,ally_name) VALUES (%s,%s,%s,%s,%s,%s)",
                         (item.get('username'),
                          item.get('position'),
                          int(item.get('derbis_crystal', 0)),
                          int(item.get('derbis_metal', 0)),
                          item.get('has_ally', 0),
                          item.get('ally_name', ''))
                         )

        self.conn.commit()
        return item
