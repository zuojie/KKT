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

'''
CUser类：
@属性
province：用户选择省份
city：用户指定城市
phoneNum：用户的电话号码
'''
class CUser:
	def __init__(self, province, city, phoneNum, name):
		self.province = province
		self.city = city
		self.phoneNum = phoneNum
		self.name = name
'''
CWeatherReportMain类：
users：用户群
'''
class CWeatherReportMain:
	def __init__(self, url = 'http://www.nmc.gov.cn/publish/forecast/'): #信息取自'中央气象台'
		self.users = []
		self.url = url
		self.py_log = CLog()
		self.province_map = {'河南':'AHA', '北京':'ABJ', '上海':'ASH', '广东':'AGD',
							'山西':'ASX', '海南':'AHI', '天津':'ATJ', '湖南':'AHN',
							'内蒙古':'ANM', '河北':'AHE'}
		self.city_map = {'茂名':'maoming', '郑州': 'zhengzhou', '上海':'shanghai', '周口':'zhoukou',\
						'北京':'beijing', '大同':'datong', '海口':'haikou', '天津':'tianjin', '长沙':'changsha',
						'东胜':'dongsheng', '廊坊':'langfang'}
	def getUsers(self, cdb):
		cdb = CDB()
		cect = cdb.getConnect()
		cur = cect.cursor()
		sql_query = 'select * from user_info_weatherreportinfo'
		try:
			cur.execute(sql_query)
			res = cur.fetchall()
			for i in res:
				if i <> '':
					print i[1] + ' ' + i[2] + ' ' + i[3] + ' ' + i[4]
					self.users.append(CUser(i[1], i[2], i[3], i[4]))
			#self.users.append(CUser('每天跑步', '作杰', "15801178340", '15'))
		except Exception, e:
			cect.rollback()
			self.py_log.log("数据库操作失败，发生回滚", self.py_log.get_file_name(), self.py_log.get_line())
	def loginFetion(self):
		is_login = False
		phone = PyFetion('15801178340', 'acmsenjing123', "TCP", debug="FILE")
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
	def parseDate(self, weather_div):
		date = weather_div.find('div', {'class': 'name'}).contents[0]
		week = weather_div.find('div', {'class': 'name'}).contents[2]
		return date + ' ' + week
	def parseWeather(self, weather):
		lis = weather('li', limit=10)
		#for li in lis:
		#	print li.string
		day = lis[0].string
		dtempurature = lis[2].next
		drain = lis[3].string
		dwind = lis[4].string
		
		night = lis[5].string
		ntempurature = lis[7].next
		nrain = lis[8].string
		nwind = lis[9].string
		'''
		print 'day ' + day.encode('gbk')
		print 'dtempurature ' + dtempurature
		print 'drain ' + drain.encode('gbk')
		print 'dwind ' + dwind.encode('gbk')
		
		print 'night ' + night.encode('gbk')
		print 'ntempurature ' + ntempurature
		print 'nrain ' + nrain.encode('gbk')
		print 'nwind ' + nwind.encode('gbk')
		'''
		return day + ': ' + dtempurature + ' ' + drain + ' '\
			+ dwind + '\n' + night + ': ' + ntempurature + ' ' + nrain + ' ' + nwind
	def sendSMS(self, my_phone, weather_info, user):
		msg1 = self.parseDate(weather_info) #明天的日期
		msg2 = self.parseWeather(weather_info) #明天的天气
		msg = '【'.decode('gbk') + user.city + '】'.decode('gbk') + msg1 + msg2
		my_phone.send_sms(msg.encode('utf-8'), user.phoneNum)
		print "send to " + user.name + ' city ' + user.city
		self.py_log.log("send to " + user.name, self.py_log.get_file_name(), self.py_log.get_line())
	def getWeatherInfo(self, my_phone):
		for user in self.users:
			url = self.url + self.province_map[user.province.encode('gbk')] + '/' + self.city_map[user.city.encode('gbk')] + '.html' #构造查询URL
			#print url
			page = urllib2.urlopen(url).read().decode('GBK').encode('utf-8')
			soup = BeautifulSoup(page)
			#print page.decode('utf-8').encode('gbk')
			city_body = soup.find('div', {'class': 'w365border city_body'})
			weather_info = city_body.findAll('div', {'class': 'weather_div'})
			self.sendSMS(my_phone, weather_info[1], user) #明天的天气
			self.sendSMS(my_phone, weather_info[2], user) # 后天的天气
	def weatherRun(self):
		cdb = CDB()
		self.getUsers(cdb)
		my_phone = self.loginFetion()
		self.getWeatherInfo(my_phone)
		cdb.close()
		my_phone.logout()
			
#example	
if __name__ == '__main__':
	cwrm = CWeatherReportMain()
	cwrm.weatherRun()