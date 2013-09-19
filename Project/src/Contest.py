#!/usr/bin/env python
#coding=gb2312

'''
@<author value = "������" />
@<date value = 2012/2/27 />
'''

import sys, urllib2, re, time
import string

from PyDB import *
from lib.BeautifulSoup import BeautifulSoup
from lib.fetion import *
from PyLog import CLog
'''
CParticipant�ࣺ������Ա��
@��Ա����
id������ID
name����������
nick�������ǳ�
phoneNum���û�����
ojs���û�ϲ���ı���
@����
isLikeContest���ж��û��Ƿ�ϲ���˱���
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
CContest�ࣺ������
@��Ա����
name����������
oj����������ƽ̨
time��������ʼʱ��
@����
getTimeStruct������string���͵�time�����Ӧtime_struct���͵�ʱ������
contestMsg�����콫Ҫ���ͳ�ȥ�ı������Ѷ���
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
CContestMain��
@��Ա
contestURL��������Ϣ��ȡҳ��
contests��ʵʱץȡ�ı�����Ϣ��
particitants�����е��û�Ⱥ
hour_interval����ǰ����Сʱ����
@����
getContests�����߻�ȡ������Ϣ
getParticitants����DB��ȡ��������Ϣ
getFileContest����DB��ȡ�Ѵ洢������Ϣ
checkFileContest�����DB�еı�����Ϣ�Ƿ���ڣ����ڵ�remove��
setFileName�����±�����ϢDB
notTimeToBegin���жϱ����ǲ��ǵڶ������
sendSMS����������Ϣ���͸���Ӧ�Ĳ�����
contestRun: ִ���ܵ��ȣ��ϴ��O(m * n)���Ӷ�����ö�ٲ����ߺ�
�����Ƿ�ƥ�䣬m��n�ֱ�Ϊѡ�������ͱ�������
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
		#����Ϊ��������̨��ӡ�շ�������		
		res = urllib2.urlopen(self.contest_url)
		page = res.read().decode('GBK').encode('utf-8') #����������gbk�⿪��Ȼ����utf-8�����python�����õĸ�ʽ
		print page.decode('utf-8').encode('gbk')
		soup = BeautifulSoup(page)
		
		#soup.table����soup�еĵ�һ��table
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
	# ������Ϣ���ݿ�Ψһ�����
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
	# contest����鵱ǰ�����Ƿ���δ��һ�쿪ʼ
	def notTimeToBegin(self, contest):
		# ��õ�ǰʱ��
		time_begin = time.localtime() 
		# ���hourInterval֮���ʱ�䣬Ĭ����24Сʱ
		time_end = time.localtime(time.time() + self.hour_interval * 60 * 60) 
		time_contest = contest.getTimeStruct()
		time_to_begin = time_contest >= time_begin and time_contest <= time_end
		return not time_to_begin
	def contestOutofTime(self, contest):
		return contest.getTimeStruct() < time.localtime()
	#������Ϣ���ݿ�Ψһд���
	def setFileContest(self):
		f = open(self.contest_file_name, 'w')
		for contest in self.file_contests:
			f.write(contest.name + '|' + contest.oj + '|' + contest.start_time + '\n')
		f.close()
	def checkFileContest(self):
		for contest in self.file_contests[:]:
			if self.contestOutofTime(contest):
				self.file_contests.remove(contest)
				
	# contest: Ҫ���ͳ��ı���
	# particitant����ϢҪ���͸��Ĳ���ѡ��
	def sendSMS(self, my_phone, contest, particitant):
		msg = contest.contestMsg()
		return my_phone.send_sms(msg, particitant.phoneNum)
	def contestRun(self):
		login_ok = False
		phone = PyFetion('15801178340', 'acmsenjing123', "TCP", debug="FILE")
		try:
			login_ok = phone.login(FetionHidden) 
		except Exception, e:
			self.py_log.log("���ŵ�½ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
			pass #��¼ʧ�ܣ����涼��������	
		if login_ok:
			self.py_log.log("���ŵ�½�ɹ�", self.py_log.get_file_name(), self.py_log.get_line())
		else:
			self.py_log.log("���ŵ�½ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
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
							self.py_log.log("����ӵ�£����͸� " + particitant.nick + " ���������ӳ� ",\
										self.py_log.get_file_name(), self.py_log.get_line())
						self.file_contests.append(contest)
						
		self.checkFileContest()
		self.setFileContest()
		phone.logout() 
if __name__ == "__main__":
	ccm = CContestMain(24 * 2, 'http://contests.acmicpc.info/contests.json') # 24Сʱ֮�ڵı�����������
	ccm.contestRun()