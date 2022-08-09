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
        self.config = None
        self.conn = pymysql.connect(host='localhost', user='galaxy', password='', db='galaxyscan', charset='utf8',
                                    database='galaxyscan')
        self.cur = self.conn.cursor()

    def open_spider(self, spider):
        self.config=spider.kwargs
        self.create_table()

    def create_table(self):
        tablename=self.config.get('server')
        sql = f"DROP table  IF EXISTS {tablename};"
        self.cur.execute(sql)
        sql=f"create table {tablename} (id int auto_increment primary key,name varchar(40) not null,pos varchar(20) not null , crystal int , metal int);"
        self.cur.execute(sql)
        self.conn.commit()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.commit()
        pass

    def process_item(self, item:dict, spider):
        self.cur.execute("insert into ze(name,pos,crystal,metal) VALUES (%s,%s,%s,%s)",
                         (item.get('username'), item.get('position'), int(item.get('derbis_crystal',0)), int(item.get('derbis_metal',0))))
        self.conn.commit()
        return item
