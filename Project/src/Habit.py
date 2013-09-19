#!/usr/bin/env python
#coding=gb2312

'''
@<author value = "������" />
@<date value = 2012/3/14 />
'''

import sys
import urllib2
import re, string
from lib.BeautifulSoup import BeautifulSoup
import mechanize, chardet
from lib.fetion import *

from PyLog import CLog
from PyDB import *

MOTTO = 'It takes at least 21 days to form a habit, come on!'
DAYS = 21
'''
CUser�ࣺ
@����
motto���˿����Ҽ����Ļ�����̾�����������50�����ڡ�
task���û�Ҫ���Ҽල������Ҳ����Ҫ���ɵ�ϰ�ߡ�������100�����ڡ�
nick���û��ǳ�
phoneNum���û��ĵ绰����
days���Ѿ����˿ͷ��˶������ˡ���21�졿
hour���û�����ÿ��ļ��㱻����
'''
class CUser:
	def __init__(self, id, motto, task, nick, phoneNum, hour, days = 0):
		self.id = id
		self.motto = motto
		self.task = task
		self.nick = nick
		self.phoneNum = phoneNum
		self.days = days
		self.hour = hour

'''
CHabitMain��:
@��Ա����
users������һ���˿Ͷ���ȡ��DB
@����
getUsers: ��DB�л�ȡһ���˿ͣ��˿��������ҽ���ǰ��д��DB
generateMsg�����ݹ˿͵�motto��task�Լ�������Ϣ�������Ѷ���
loginFetion����½����
sendSMS: �������û�Ԥ�ڵ���Ϣ���ͳ�ȥ
updateUser���������ݿ����û���Ϣ
setUser�������ݿ���д���û���Ϣ
habitRun��ִ���ܵĵ���
'''
class CHabitMain:
	def __init__(self):
		self.users = []
		self.py_log = CLog()
	def getUsers(self, cdb):
		cdb = CDB()
		cect = cdb.getConnect()
		cur = cect.cursor()
		sql_lock = 'lock table user_info_habitinfo write'
		sql_unlock = 'unlock tables'
		sql_query = 'select * from user_info_habitinfo'
		sql_remove = 'truncate table user_info_habitinfo'
		print '-----------------'
		try:
			cur.execute(sql_lock) #����
			cur.execute(sql_query)
			res = cur.fetchall()
			cur.execute(sql_remove) #��ձ�������
			for i in res:
				if i <> '':
					#print str(i[0]) + ' ' + i[1] + ' ' + i[2] + ' ' + i[3] + ' ' + i[4] + ' ' + str(i[5]) + ' ' + i[6]
					self.users.append(CUser(i[0], i[1], i[2], i[3], i[4], i[6], i[5]))
			#self.users.append(CUser('ÿ���ܲ�', '����', "15801178340", '15'))
			cur.execute(sql_unlock) #����
		except Exception, e:
			cect.rollback()
			print e
			self.py_log.log("���ݿ�ɾ��ʧ�ܣ������ع�", self.py_log.get_file_name(), self.py_log.get_line())
	def updateUser(self, cdb, user):
		if user.days < DAYS:
			user.days = user.days + 1
		#print 'user days update ' + str(user.days)
	def setUser(self, cdb):
		cdb = CDB()
		cect = cdb.getConnect()
		cur = cect.cursor()
		sql_insert = 'insert into user_info_habitinfo values (%s, %s, %s, %s, %s, %s)'
		for user in self.users:
			if user.days < DAYS:
				try:
					cur.execute(sql_insert, (user.id, user.motto, user.task, user.nick,\
							user.phoneNum, str(user.days), user.hour))
				except Exception ,e:
					cect.rollback()
					self.py_log.log("���ݿ�ɾ��ʧ�ܣ������ع�", self.py_log.get_file_name(), self.py_log.get_line())
		cect.commit()
	def loginFetion(self):
		is_login = False
		phone = PyFetion('15801178340', 'passwd', "TCP", debug="FILE")
		try:
			is_login = phone.login(FetionHidden)
		except Exception, e:
			self.py_log.log("���ŵ�½ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
			pass #��¼ʧ�ܣ����涼��������
		if is_login:
			self.py_log.log("���ŵ�½�ɹ�", self.py_log.get_file_name(), self.py_log.get_line())
		else:
			self.py_log.log("���ŵ�½ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
		return phone
	def	generateMsg(self, user):
		msg = 'Hi, ' + user.nick + ', ' + user.motto + ' ' + user.task +\
			' you have insist on ' + str(user.days + 1) + 'days, keep going!' 
		return msg
	def sendSMS(self, phone, msg, phoneNum):
		#print chardet.detect(msg)
		return phone.send_sms(msg.encode('utf-8'), phoneNum)
	def habitRun(self):
		cdb = CDB()
		self.getUsers(cdb)
		time_current = time.localtime()
		hour = time_current[3] #ȡ��hour
		my_phone = self.loginFetion()
		try:
			for user in self.users:
				user_hour = string.atoi(user.hour)
				if user_hour == hour: #��������,����1Сʱrunһ�Σ����ÿ��ʱ�εĿͻ���ֻ�ᱻ����һ��
					msg = self.generateMsg(user)
					self.sendSMS(my_phone, msg, user.phoneNum)
					self.updateUser(cdb, user)
		except Exception, e:
			self.py_log.log(str(e), self.py_log.get_file_name(), self.py_log.get_line())
		self.setUser(cdb)
		cdb.close()
		my_phone.logout()
			
#example	
if __name__ == '__main__':
	chm = CHabitMain()
	chm.habitRun()
