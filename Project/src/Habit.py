#!/usr/bin/env python
#coding=gb2312

'''
@<author value = "彭作杰" />
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
CUser类：
@属性
motto：顾客自我激励的话【简短精悍，控制在50字以内】
task：用户要自我监督的任务，也就是要养成的习惯【控制在100字以内】
nick：用户昵称
phoneNum：用户的电话号码
days：已经给顾客发了多少天了【共21天】
hour：用户想在每天的几点被提醒
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
CHabitMain类:
@成员变量
users：持有一批顾客对象，取自DB
@方法
getUsers: 从DB中获取一批顾客；顾客数据由且仅由前端写入DB
generateMsg：根据顾客的motto，task以及其他信息生成提醒短信
loginFetion：登陆飞信
sendSMS: 将符合用户预期的信息发送出去
updateUser：更新数据库中用户信息
setUser：向数据库中写入用户信息
habitRun：执行总的调度
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
			cur.execute(sql_lock) #加锁
			cur.execute(sql_query)
			res = cur.fetchall()
			cur.execute(sql_remove) #清空表内数据
			for i in res:
				if i <> '':
					#print str(i[0]) + ' ' + i[1] + ' ' + i[2] + ' ' + i[3] + ' ' + i[4] + ' ' + str(i[5]) + ' ' + i[6]
					self.users.append(CUser(i[0], i[1], i[2], i[3], i[4], i[6], i[5]))
			#self.users.append(CUser('每天跑步', '作杰', "15801178340", '15'))
			cur.execute(sql_unlock) #解锁
		except Exception, e:
			cect.rollback()
			print e
			self.py_log.log("数据库删除失败，发生回滚", self.py_log.get_file_name(), self.py_log.get_line())
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
					self.py_log.log("数据库删除失败，发生回滚", self.py_log.get_file_name(), self.py_log.get_line())
		cect.commit()
	def loginFetion(self):
		is_login = False
		phone = PyFetion('15801178340', 'passwd', "TCP", debug="FILE")
		try:
			is_login = phone.login(FetionHidden)
		except Exception, e:
			self.py_log.log("飞信登陆失败", self.py_log.get_file_name(), self.py_log.get_line())
			pass #登录失败，下面都不用做了
		if is_login:
			self.py_log.log("飞信登陆成功", self.py_log.get_file_name(), self.py_log.get_line())
		else:
			self.py_log.log("飞信登陆失败", self.py_log.get_file_name(), self.py_log.get_line())
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
		hour = time_current[3] #取出hour
		my_phone = self.loginFetion()
		try:
			for user in self.users:
				user_hour = string.atoi(user.hour)
				if user_hour == hour: #该提醒了,服务1小时run一次，因此每个时段的客户均只会被提醒一次
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
