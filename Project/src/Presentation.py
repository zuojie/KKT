#!/user/bin/env python
#coding=gbk

'''
@<author value = "������" />
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
CUser���û���
@��Ա����
phoneNum���û��绰
addr���û�ѡ���ע�����������
'''
class CUser(object):
	def __init__(self, phoneNum, addr):
		self.phoneNum = phoneNum
		self.addr = addr
'''
CPresentation�ࣺ��������
@��Ա����
pcity����������������
pinc�����������Ĺ�˾
pschool������������ѧУ
pdate������������
paddr������������ַ
@��Ա����
getTimeStruct������string���͵�time�����Ӧtime_struct���͵�ʱ������
contestMsg�����콫Ҫ���ͳ�ȥ�����������Ѷ���
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
		self.pdate == other.pdate #�������⵼�µ�ַ����������,��˲��������������ҽ����ж�
		#assert(ret)
		return False
	def getTimeStruct(self):
		regex = '\d{4}(\\.\d{2}){2}' #ƥ�����ƣ�2012.03.13
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
		if monthL < monthR: #��ǰʱ�䳬��������ʱ��
			return True
		elif monthL == monthR and dayL < dayR:
			return True
		return False
	def getPresentationMsg(self):
		return self.pinc + ' @ ' + self.pschool + ' ' +\
			self.paddr + ' will hold presentation at ' + self.pdate
'''
CPresentationMain�ࣺ
@��Ա����
city_dict��������url��׺ӳ��map���ݴ˹�����Ϣ��ȡҳ���url
presentations��ץȡ����������Ϣ��
file_presentations:���ش洢�Ѿ����͵���������Ϣ
users�����е��û�Ⱥ
@��Ա����
getPresentation�����߻�ȡ��������Ϣ
getUsers����db��ȡ�û���Ϣ
getRes����ȡָ��url����������Ϣ
getFilePresentation����db��ȡ�Ѵ洢��������Ϣ
checkFilePresentation���ж�db����������Ϣ�Ƿ����
setFilePresentation������db�еı�����Ϣ
sendSMS��������������Ϣ���û�
mainRun���ܵ��ȷ���
'''
class CPresentationMain(object):
	def __init__(self, presentation_file_name = r'I:\2012BS\Project\src\presentation\presentation.arvin'):
		self.city_dict = {'����':'1', '���':'2', '�ӱ�':'3', '���ɹ�':'4',\
						'ɽ��':'5', '�Ϻ�':'6', '����':'7', '����':'8',\
						'�㽭':'9', 'ɽ��':'10', '����':'11', '����':'12',\
						'�㶫':'13', '����':'14', '����':'15', '����':'16',\
						'����':'17', '����':'18', '������':'19', '����':'20',\
						'����':'21', '����':'22', '����':'23', '����':'24',\
						'�ຣ':'25', '�½�':'26', '����':'27', '�Ĵ�':'28',\
						'����':'29', '����':'30', '����':'31', '���':'32',\
						'����':'33', '̨��':'34'}
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
			self.py_log.log("��ȡָ��url������ʧ�� ", self.py_log.get_file_name(), self.py_log.get_line())
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
	# ��������Ϣ���ݿ��Ψһ���
	def getFilePresentation(self):
		try:
			f = codecs.open(self.presentation_file_name, 'r', 'gbk')
			#f = open(self.presentation_file_name, 'r')
		except IOError: # �����ڴ��ļ�����ô�½�һ��
			#print 'IOError'
			f = open(self.presentation_file_name, 'w')
			f.close
			f = open(self.presentation_file_name, 'r')
		data = f.read().split('\n')
		f.close()
		for i in data:
			if i != '':
				j = i.split('|') #��������Ϣ����|�ָ���
				self.file_presentations.append(CPresentation(j[0], j[1], j[2], j[3], j[4]))
	def setFilePresentation(self):
		f = codecs.open(self.presentation_file_name, 'w', 'gbk')
		#f = open(self.presentation_file_name, 'w')
		file_code = 'gbk'
		for prent in self.file_presentations:
			if prent != '':
				'''
				#�������ֱ��뷽ʽ����ÿ��д���ļ���ÿ����Ϣ����дһ�����У�����
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
		for i in range(1, 35): #ȡ��34[1-34]��ʡ�ݵ�δ���������Ƹ��Ϣ
			url = base_url + str(i) + '.html'
			#print url
			try:
				page = self.getRes(url) 
				soup = BeautifulSoup(page)
			except: #url��ʧ��
				continue
			#ȡ�����еĵ���ʱ
			try: #��ǰ���п���δ��һ��ʱ��û����������Ϣ
				countdowns = soup.findAll('div', {'class': 'list_topic'})
				y_m_d2, y_m_d3 = '', ''; #��¼�ڶ���͵����������������
				first, second = -1, -1 #�ڶ���͵��������������ֵ�����ΪcampusTalk��table�±�.��λ���Ǻ͵���ʱ���ֵ�div���ִ�һ��λ��
				# ��Ϊ��0����ΪcampusTalk��table�Ǳ����������ӵ�1����ʼ�������������Ϣ�����day��ʼ��Ϊ1
				day = 1 
				for countdown in countdowns:
					cd = string.atoi(countdown.contents[0].contents[2].string)
					if cd > 2: #����ʱ����2��������ᣬ�ݲ�����
						break
					elif cd == 1: #�ڶ���Ҫ���е������᡾����ʱʣ1�졿
						first = day
						y_m_d2 = countdown.contents[1].string
					elif cd == 2: #������Ҫ���е������᡾����ʱʣ2�졿
						second = day
						y_m_d3 = countdown.contents[1].string
					day = day + 1
				# first�ǵ�2����Ϣ��second�ǵ��������Ϣ������Ϊ-1����ʾ����û��������
				if first != -1:
					tables = soup.findAll('table', {'class':'campusTalk'})[first]
					trs = tables.findAll('tr')
					for tr in trs:
						tds = tr.findAll('td')
						city = tds[0].a.string.strip()
						school = tds[1].a.string.strip()
						addr = tds[2].string.strip()
						inc = tds[3].a.string.strip()
						try: # ��Щ������δ������忪ʼʱ��[H-M-S]
							pdate = y_m_d2 + ' ' + tds[4].string
						except Exception, e:
							pdate = y_m_d2 #��ôֻ��¼�����ռ���
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
				self.py_log.log('��' + str(i) + '������δ��һ��ʱ��û����������Ϣ', self.py_log.get_file_name(), self.py_log.get_line())
	def sendSMS(self, my_phone, presentation, user):
		msg = presentation.getPresentationMsg().encode('utf-8')
		# print chardet.detect(msg) #����
		return my_phone.send_sms(msg, user.phoneNum)
	def mainRun(self):
		login_ok = False
		phone = PyFetion('15801178340', 'passwd', "TCP", debug="FILE")
		try:
			login_ok = phone.login(FetionHidden) 
		except Exception, e:
			self.py_log.log("���ŵ�½ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
			pass #��¼ʧ�ܣ����涼��������	
		if login_ok:
			self.py_log.log("���ŵ�½�ɹ�", self.py_log.get_file_name(), self.py_log.get_line())
		else:
			self.py_log.log("���ŵ�½ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
		
		self.getUsers()
		self.getPresentation()
		self.getFilePresentation()
		self.checkFilePresentation()
		set_presentations = []
		for user in self.users:
			for prent in self.presentations:
				if prent != '':
					if user.addr == prent.pcity:#�����û�ѡ��ĳ���Ԥ��
						if prent in self.file_presentations: # ���͹�����Ϣ
							continue
						#print 'user city ' + user.addr + ' prent pcity ' + prent.pcity
						set_presentations.append(prent) # ���͹����ݴ��ڼ����У��û�����д�뱾���ļ�
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
