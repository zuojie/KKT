#!/usr/bin/env python
#coding=gb2312

'''
@<author value = "彭作杰" />
@<date value = 2012/2/27 />
'''

import sys, urllib2, re, time
import string

from PyDB import *
from lib.BeautifulSoup import BeautifulSoup
from lib.fetion import *
from PyLog import CLog
'''
CParticipant类：比赛人员类
@成员变量
id：比赛ID
name：比赛姓名
nick：比赛昵称
phoneNum：用户号码
ojs：用户喜欢的比赛
@方法
isLikeContest：判断用户是否喜欢此比赛
'''
class CParticipant(object):
	def __init__(self, id, name, nick, phoneNum, ojs):
		self.id = id
		self.name = name
		self.nick = nick
		self.phoneNum = phoneNum
		self.ojs = ojs
		self.py_log = CLog()
	def isLikeContest(self, contest):
		#print 'like ojs'
		if self.ojs == 'all':
			return True
		for oj in self.ojs:
			if contest.oj == oj:
				return True
		return False
'''
CContest类：比赛类
@成员变量
name：竞赛名字
oj：竞赛发布平台
time：竞赛开始时间
@方法
getTimeStruct：根据string类型的time获得相应time_struct类型的时间数据
contestMsg：构造将要发送出去的比赛提醒短信
'''
class CContest(object):
	def __init__(self, name, oj, start_time):
		self.name = name
		self.oj = oj
		self.start_time = start_time
		self.py_log = CLog()
	def __eq__(self, other):
		return self.name == other.name and \
		self.oj == other.oj and \
		self.start_time == other.start_time
	def getTimeStruct(self):
		return time.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
	def contestMsg(self):
		return self.name + ' @ ' + self.oj + ' will begin at ' +\
		self.start_time + ' ! '
'''
CContestMain类
@成员
contestURL：比赛信息获取页面
contests：实时抓取的比赛信息们
particitants：持有的用户群
hour_interval：提前几个小时提醒
@方法
getContests：在线获取比赛信息
getParticitants：从DB获取参赛者信息
getFileContest：从DB获取已存储比赛信息
checkFileContest：检查DB中的比赛信息是否过期，过期的remove掉
setFileName：更新比赛信息DB
notTimeToBegin：判断比赛是不是第二天举行
sendSMS：将比赛信息发送给相应的参赛者
contestRun: 执行总调度，较搓的O(m * n)复杂度朴素枚举参赛者和
比赛是否匹配，m和n分别为选手数量和比赛数量
'''
class CContestMain(object):
	def __init__(self, hour_interval, contest_url = r"http://acm.nankai.edu.cn/recent_contests.php",\
				contest_file_name = r"I:\2012BS\Project\src\contest\contest.arvin"):
		self.contest_url = contest_url
		self.contests = []
		self.particitants = []
		self.hour_interval = hour_interval
		self.py_log = CLog()
		self.contest_file_name = contest_file_name
		self.file_contests = []
	def getContests(self):
		#added by arvin peng
		#httpHandler = urllib2.HTTPHandler(debuglevel=1)
		#httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
		#opener = urllib2.build_opener(httpHandler, httpsHandler)
		#urllib2.install_opener(opener)
		#以上为开启控制台打印收发包内容		
		res = urllib2.urlopen(self.contest_url)
		page = res.read().decode('GBK').encode('utf-8') #网络数据以gbk解开，然后以utf-8编码成python处理用的格式
		print page.decode('utf-8').encode('gbk')
		soup = BeautifulSoup(page)
		
		#soup.table返回soup中的第一张table
		contest_list = soup.table.findAll('tr', {'class': 'HC'})
		print contest_list
		for contest in contest_list:
			print 'M in'
			tds = contest.findAll('td')
			oj = re.sub(' *', '', str(tds[0].string)) 
			name = re.sub('<.*?>|&nbsp;', '', str(tds[1]))
			start_time = str(tds[2].string)
			self.contests.append(CContest(name, oj, start_time))
			
			print 'getContests : ' + name.decode('utf-8').encode('gbk') + ' '\
				+ oj.decode('utf-8').encode('gbk') + ' ' + start_time.decode('utf-8').encode('gbk')
			
	def getParticitants(self):
		cdb = CDB()
		cect = cdb.getConnect()
		cur = cect.cursor()
		sql = 'select * from participantInfo'
		cur.execute(sql)
		res = cur.fetchall()
		for i in res:
			if i <> '':
				'''
				print str(i[0]).encode('gb2312') + ' ' + \
							i[1].encode('gb2312') + ' ' + \
							i[2].encode('gb2312') + ' ' + \
							i[3].encode('gb2312') + ' ' + \
							i[4].encode('gb2312') + '\n'
				'''
				ojs = i[4].encode('gb2312').split(' ')
				print ojs
				self.particitants.append(CParticipant(str(i[0]).encode('gb2312'),\
							i[1].encode('gb2312'),\
							i[2].encode('gb2312'),\
							i[3].encode('gb2312'), ojs))#.split('|')))
		cdb.close()
	# 比赛信息数据库唯一读入口
	def getFileContest(self):
		try:
			f = open(self.contest_file_name, 'r')
		except IOError:
			f = open(self.contest_file_name, 'w')
			f.close
			f = open(self.contest_file_name, 'r')
		data = f.read().split('\n')
		f.close()
		for i in data:
			if i <> '':
				j = i.split('|')
				self.file_contests.append(CContest(j[0], j[1], j[2]))
	# contest：检查当前比赛是否在未来一天开始
	def notTimeToBegin(self, contest):
		# 获得当前时间
		time_begin = time.localtime() 
		# 获得hourInterval之后的时间，默认是24小时
		time_end = time.localtime(time.time() + self.hour_interval * 60 * 60) 
		time_contest = contest.getTimeStruct()
		time_to_begin = time_contest >= time_begin and time_contest <= time_end
		return not time_to_begin
	def contestOutofTime(self, contest):
		return contest.getTimeStruct() < time.localtime()
	#比赛信息数据库唯一写入口
	def setFileContest(self):
		f = open(self.contest_file_name, 'w')
		for contest in self.file_contests:
			f.write(contest.name + '|' + contest.oj + '|' + contest.start_time + '\n')
		f.close()
	def checkFileContest(self):
		for contest in self.file_contests[:]:
			if self.contestOutofTime(contest):
				self.file_contests.remove(contest)
				
	# contest: 要发送出的比赛
	# particitant：信息要发送给的参赛选手
	def sendSMS(self, my_phone, contest, particitant):
		msg = contest.contestMsg()
		return my_phone.send_sms(msg, particitant.phoneNum)
	def contestRun(self):
		login_ok = False
		phone = PyFetion('15801178340', 'acmsenjing123', "TCP", debug="FILE")
		try:
			login_ok = phone.login(FetionHidden) 
		except Exception, e:
			self.py_log.log("飞信登陆失败", self.py_log.get_file_name(), self.py_log.get_line())
			pass #登录失败，下面都不用做了	
		if login_ok:
			self.py_log.log("飞信登陆成功", self.py_log.get_file_name(), self.py_log.get_line())
		else:
			self.py_log.log("飞信登陆失败", self.py_log.get_file_name(), self.py_log.get_line())
		self.getParticitants()
		self.getContests()
		self.getFileContest()
		for particitant in self.particitants:
			for contest in self.contests:
				if particitant.isLikeContest(contest):
					if self.notTimeToBegin(contest):
						continue
					elif contest in self.file_contests:
						continue
					else:
						if self.sendSMS(phone, contest, particitant):
							self.py_log.log("send to " + particitant.nick + " successfully!",\
										self.py_log.get_file_name(), self.py_log.get_line())
						else:
							self.py_log.log("网络拥堵，发送给 " + particitant.nick + " 将会稍有延迟 ",\
										self.py_log.get_file_name(), self.py_log.get_line())
						self.file_contests.append(contest)
						
		self.checkFileContest()
		self.setFileContest()
		phone.logout() 
if __name__ == "__main__":
	ccm = CContestMain(24 * 2, 'http://contests.acmicpc.info/contests.json') # 24小时之内的比赛进行提醒
	ccm.contestRun()