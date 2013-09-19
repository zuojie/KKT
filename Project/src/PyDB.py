#!/usr/bin/env python
#coding=gb2312

'''
@<author value = ������ />
@<date value = 2012/2/26 />
'''

import MySQLdb
import sys
from PyLog import CLog

'''
DB�ࣺ��������DB����
@����
cect�������ݿ⽨���������
@������
__init__:��ʼ����Ա���ԣ�����DB��������
getConnect����ȡ��DB������
reSet()�����ú�DB������
close���ر�DB������
'''
class CDB(object):
	def __init__(self):
		try:
			self.cect = MySQLdb.connect(host='localhost',\
									   user='root',\
									   passwd='123456',\
									   db='user_info',\
									   port=3306,\
									   charset='gb2312')
		except Exception, e:
			#py_log.log("DB connect failed")
			pass
		self.py_log = CLog()
	def getConnect(self):
		return self.cect
	def reSet(self):
		try:
			self.cect = MySQLdb.connect(host='localhost',\
								user='root',\
								passwd='123456',\
								db='user_info',\
								port=3306,\
								charset='gb2312')
		except Exception, e:
			self.py_log.log("DB reset failed", self.py_log.get_file_name(), \
							self.py_log.get_line())
			pass
	def close(self):
		try:
			self.cect.close()
		except Exception, e:
			self.py_log.log("DB�ر�ʧ��", self.py_log.get_file_name(),\
							self.py_log.get_line())
			pass
		
#example
if __name__ == "__main__":
	cdb = CDB()
	cect = cdb.getConnect()
	cur = cect.cursor()
	sql = 'select * from acmerINFO'
	cur.execute(sql)
	res = cur.fetchall()
	for i in res:
		if i <> '':
			print str(i[0]).encode('gb2312') + ' ' + \
						i[1].encode('gb2312') + ' ' + \
						i[2].encode('gb2312') + ' ' + \
						i[3].encode('gb2312') + ' ' + \
						i[4].encode('gb2312') + '\n'