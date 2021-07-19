import datetime

import pymysql
from dishonest.settings import MYSQL_HOST,MYSQL_PORT,MYSQL_DB,MYSQL_USER,MYSQL_PASSWORD

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class DishonestPipeline:
    def open_item(self,spider):
        #建立数据库连接
        self.connection=pymysql.connect(host=MYSQL_HOST,
                                        port=MYSQL_PORT,
                                        db=MYSQL_DB,
                                        user=MYSQL_USER,
                                        password=MYSQL_PASSWORD)
        #获取操作数据
        self.cursor=self.connection.cursor()
    def close_spider(self,spider):
        #关闭cursor
        self.cursor.close()
        #关闭数据库连接
        self.connection.close()
    def process_item(self, item, spider):
        #自然人根据身份证号判断，企业通过区域和企业名称判断
        if item['age'] == 0:
            # 如果年龄 == 0 , 就是企业, 就根据公司名和区域进行查询
            name = item['name']
            area = item['area']
            select_sql = "select count(1) from t_dishonest where name='{}' and area = '{}'".format(name, area)
        else:
            # 如果是个人根据证件号, 数据条数
            select_sql = "select count(1) from t_dishonest where card_num='{}'".format(item['card_num'])

        # 根据证件号, 数据条数
        # select_sql = "select count(1) from dishonest where card_num='{}'".format(item['card_num'])
        # 执行查询SQL
        self.cursor.execute(select_sql)
        # 获取查询结果
        count = self.cursor.fetchone()[0]
        # 如果查询的数量为0, 说明该人不存在, 不存在就插入
        if count == 0:
            # 获取当前的时间, 为插入数据库的时间
            item['create_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['update_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 把数据转换为键, 值的格式, 方便插入数据库
            keys, values = zip(*dict(item).items())
            # 插入数据库SQL
            insert_sql = 'insert into t_dishonest ({}) values({})'.format(
                ','.join(keys),
                ','.join(['%s'] * len(values))
            )
            # 执行插入数据SQL
            self.cursor.execute(insert_sql, values)
            # 提交
            self.connect.commit()
            spider.logger.info('插入数据')

        else:
            spider.logger.info('{}  重复'.format(item))
        return item
