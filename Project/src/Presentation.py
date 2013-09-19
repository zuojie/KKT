#!/user/bin/env python
#coding=gbk

'''
@<author value = "彭作杰" />
@<date value = 2012/3/10 />
'''
import sys, urllib2, re, time
import string
import codecs
import chardet

from PyDB import *
from lib.BeautifulSoup import BeautifulSoup
from lib.fetion import *
from PyLog import CLog

'''
CUser：用户类
@成员变量
phoneNum：用户电话
addr：用户选择关注的宣讲会城市
'''
class CUser(object):
	def __init__(self, phoneNum, addr):
		self.phoneNum = phoneNum
		self.addr = addr
'''
CPresentation类：宣讲会类
@成员变量
pcity：宣讲会所属城市
pinc：进行宣讲的公司
pschool：宣讲会所在学校
pdate：宣讲会日期
paddr：宣讲会具体地址
@成员方法
getTimeStruct：根据string类型的time获得相应time_struct类型的时间数据
contestMsg：构造将要发送出去的宣讲会提醒短信
'''
class CPresentation(object):
	def __init__(self, pcity, pinc, pschool, pdate, paddr):
		self.pcity = pcity
		self.pinc = pinc
		self.pschool = pschool
		self.pdate = pdate
		self.paddr = paddr
		self.py_log = CLog()
	def __eq__(self, other):
		return self.pcity == other.pcity and\
		self.pinc == other.pinc and\
		self.pschool == other.pschool and\
		self.pdate == other.pdate #编码问题导致地址判重有问题,因此不对宣讲会具体教室进行判断
		#assert(ret)
		return False
	def getTimeStruct(self):
		regex = '\d{4}(\\.\d{2}){2}' #匹配类似：2012.03.13
		match = re.search(regex, self.pdate) 
		return match.group()
		#return time.strptime(self.pdate, '%Y.%m.%d')
	def isOutOfTime(self):
		time_current = time.localtime()
		time_prent = self.getTimeStruct()
		#year = time_current[0]
		monthR = time_current[1]
		dayR = time_current[2]
		#print time_prent
		monthL = string.atoi(time_prent[5:7])
		dayL = string.atoi(time_prent[8:10])
		
		#print string.atoi(str(monthL)) + string.atoi(str(dayL))
		if monthL < monthR: #当前时间超过宣讲会时间
			return True
		elif monthL == monthR and dayL < dayR:
			return True
		return False
	def getPresentationMsg(self):
		return self.pinc + ' @ ' + self.pschool + ' ' +\
			self.paddr + ' will hold presentation at ' + self.pdate
'''
CPresentationMain类：
@成员变量
city_dict：地名和url后缀映射map，据此构造信息提取页面的url
presentations：抓取的宣讲会信息们
file_presentations:本地存储已经发送的宣讲会信息
users：持有的用户群
@成员方法
getPresentation：在线获取宣讲会信息
getUsers：从db获取用户信息
getRes：获取指定url的宣讲会信息
getFilePresentation：从db获取已存储宣讲会信息
checkFilePresentation：判断db中宣讲会信息是否过期
setFilePresentation：更新db中的比赛信息
sendSMS：发送宣讲会信息给用户
mainRun：总调度方法
'''
class CPresentationMain(object):
	def __init__(self, presentation_file_name = r'I:\2012BS\Project\src\presentation\presentation.arvin'):
		self.city_dict = {'北京':'1', '天津':'2', '河北':'3', '内蒙古':'4',\
						'山西':'5', '上海':'6', '安徽':'7', '江苏':'8',\
						'浙江':'9', '山东':'10', '福建':'11', '江西':'12',\
						'广东':'13', '广西':'14', '海南':'15', '河南':'16',\
						'湖北':'17', '湖南':'18', '黑龙江':'19', '吉林':'20',\
						'辽宁':'21', '陕西':'22', '甘肃':'23', '宁夏':'24',\
						'青海':'25', '新疆':'26', '重庆':'27', '四川':'28',\
						'云南':'29', '贵州':'30', '西藏':'31', '香港':'32',\
						'澳门':'33', '台湾':'34'}
		self.presentation_file_name = presentation_file_name
		self.presentations = []
		self.file_presentations = []
		self.users = []
		self.py_log = CLog()
	def getRes(self, url):
		try:
			res = urllib2.urlopen(url)
			page = res.read().decode('GBK').encode('utf-8')
			return page
		except:
			self.py_log.log("获取指定url宣讲会失败 ", self.py_log.get_file_name(), self.py_log.get_line())
	def getUsers(self):
		cdb = CDB()
		cect = cdb.getConnect()
		cur = cect.cursor()
		sql = 'select * from user_info_presentationerinfo'
		cur.execute(sql)
		res = cur.fetchall()
		for i in res:
			if i != '':
				#print str(i[1]).encode('gbk') + ' ' + i[2].encode('gbk')
				self.users.append(CUser(i[1], i[2]))
		cdb.close()
	# 宣讲会信息数据库读唯一入口
	def getFilePresentation(self):
		try:
			f = codecs.open(self.presentation_file_name, 'r', 'gbk')
			#f = open(self.presentation_file_name, 'r')
		except IOError: # 不存在此文件，那么新建一个
			#print 'IOError'
			f = open(self.presentation_file_name, 'w')
			f.close
			f = open(self.presentation_file_name, 'r')
		data = f.read().split('\n')
		f.close()
		for i in data:
			if i != '':
				j = i.split('|') #宣讲会信息项用|分隔开
				self.file_presentations.append(CPresentation(j[0], j[1], j[2], j[3], j[4]))
	def setFilePresentation(self):
		f = codecs.open(self.presentation_file_name, 'w', 'gbk')
		#f = open(self.presentation_file_name, 'w')
		file_code = 'gbk'
		for prent in self.file_presentations:
			if prent != '':
				'''
				#下面这种编码方式导致每次写入文件，每行信息都多写一个换行，诡异
				f.write(prent.pcity.encode(file_code) + '|'\
						+ prent.pinc.encode(file_code) + '|'\
						+ prent.pschool.encode(file_code) + '|'\
						+ prent.pdate.encode(file_code) + '|'\
						+ prent.paddr.encode(file_code) + '\n')
				'''
				f.write(prent.pcity + '|'\
					+ prent.pinc + '|'\
					+ prent.pschool + '|'\
					+ prent.pdate + '|'\
					+ prent.paddr + '\n')
				
		f.close()
	def checkFilePresentation(self):
		for prent in self.file_presentations[:]:
			if prent.isOutOfTime():
				self.file_presentations.remove(prent)
	def getPresentation(self):
		base_url = 'http://my.yingjiesheng.com/xuanjianghui_province_'
		for i in range(1, 35): #取出34[1-34]个省份的未来两天的招聘信息
			url = base_url + str(i) + '.html'
			#print url
			try:
				page = self.getRes(url) 
				soup = BeautifulSoup(page)
			except: #url打开失败
				continue
			#取出所有的倒计时
			try: #当前城市可能未来一段时间没有宣讲会信息
				countdowns = soup.findAll('div', {'class': 'list_topic'})
				y_m_d2, y_m_d3 = '', ''; #记录第二天和第三天的宣讲会日期
				first, second = -1, -1 #第二天和第三天的宣讲会出现的名字为campusTalk的table下标.其位置是和倒计时出现的div保持错开一个位置
				# 因为第0个名为campusTalk的table是表格标题栏，从第1个开始才是宣讲会的信息，因此day初始化为1
				day = 1 
				for countdown in countdowns:
					cd = string.atoi(countdown.contents[0].contents[2].string)
					if cd > 2: #倒计时超过2天的宣讲会，暂不考虑
						break
					elif cd == 1: #第二天要举行的宣讲会【倒计时剩1天】
						first = day
						y_m_d2 = countdown.contents[1].string
					elif cd == 2: #第三天要举行的宣讲会【倒计时剩2天】
						second = day
						y_m_d3 = countdown.contents[1].string
					day = day + 1
				# first是第2天信息，second是第三天的信息，假如为-1，表示那天没有宣讲会
				if first != -1:
					tables = soup.findAll('table', {'class':'campusTalk'})[first]
					trs = tables.findAll('tr')
					for tr in trs:
						tds = tr.findAll('td')
						city = tds[0].a.string.strip()
						school = tds[1].a.string.strip()
						addr = tds[2].string.strip()
						inc = tds[3].a.string.strip()
						try: # 有些宣讲会未标出具体开始时间[H-M-S]
							pdate = y_m_d2 + ' ' + tds[4].string
						except Exception, e:
							pdate = y_m_d2 #那么只记录年月日即可
						self.presentations.append(CPresentation(city, inc, school, pdate, addr))
				if second != -1:
					tables = soup.findAll('table', {'class':'campusTalk'})[second]
					trs = tables.findAll('tr')
					for tr in trs:
						tds = tr.findAll('td')
						city = tds[0].a.string.strip()
						school = tds[1].a.string.strip()
						addr = tds[2].string.strip()
						inc = tds[3].a.string.strip()
						try:
							pdate = y_m_d3 + ' ' + tds[4].string
						except:
							pdate = y_m_d3
						self.presentations.append(CPresentation(city, inc, school, pdate, addr))
			except:
				self.py_log.log('第' + str(i) + '个城市未来一段时间没有宣讲会信息', self.py_log.get_file_name(), self.py_log.get_line())
	def sendSMS(self, my_phone, presentation, user):
		msg = presentation.getPresentationMsg().encode('utf-8')
		# print chardet.detect(msg) #神器
		return my_phone.send_sms(msg, user.phoneNum)
	def mainRun(self):
		login_ok = False
		phone = PyFetion('15801178340', 'passwd', "TCP", debug="FILE")
		try:
			login_ok = phone.login(FetionHidden) 
		except Exception, e:
			self.py_log.log("飞信登陆失败", self.py_log.get_file_name(), self.py_log.get_line())
			pass #登录失败，下面都不用做了	
		if login_ok:
			self.py_log.log("飞信登陆成功", self.py_log.get_file_name(), self.py_log.get_line())
		else:
			self.py_log.log("飞信登陆失败", self.py_log.get_file_name(), self.py_log.get_line())
		
		self.getUsers()
		self.getPresentation()
		self.getFilePresentation()
		self.checkFilePresentation()
		set_presentations = []
		for user in self.users:
			for prent in self.presentations:
				if prent != '':
					if user.addr == prent.pcity:#符合用户选择的城市预期
						if prent in self.file_presentations: # 发送过此信息
							continue
						#print 'user city ' + user.addr + ' prent pcity ' + prent.pcity
						set_presentations.append(prent) # 发送过的暂存在集合中，用户最后的写入本地文件
						self.sendSMS(phone, prent, user)
		#set_presentations = set(set_presentations)
		#self.file_presentations += set_presentations
		#print self.file_presentations
		#'''
		for tp in set_presentations:
			if tp != '':
				if tp in self.file_presentations:
					continue
				#print 'add ' + tp.pschool
				self.file_presentations.append(tp)
		#'''
		self.setFilePresentation()
	# example
if __name__ == '__main__':
	cpm = CPresentationMain()
	cpm.mainRun()
