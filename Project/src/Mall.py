#!/usr/bin/env python
#coding=gb2312

'''
@<author value = "������" />
@<date value = 2012/2/26 />
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
CGoods�ࣺ
@����
name����Ʒ����
book����Ʒ���ͼ��Ӱ������߰ٻ���
min_price���û��������Ʒ��������λ
'''
class CGoods(object):
	def __init__(self, name, is_book, min_price):
		self.name = name
		self.is_book = is_book
		self.min_price = min_price
'''
CCustomer��
@����
urls���˿͹���������ַ�б�demoָ��ֻ��һ��langlang.cc��
goods���û�Ҫ�������Ʒ
phoneNum���û��ĵ绰����
'''
class CCustomer:
	def __init__(self, id, goods, phoneNum, urls = "http://langlang.cc/"):
		self.id = id
		self.goods = goods
		self.phoneNum = phoneNum
		self.urls = urls

'''
CInfo�ࣺ���͸��û���Ϣ�����岿��
@����
goods_name����Ʒ����
merch_name����Ʒ���������
merprice����ƷĿǰ�ۼ�
'''
class CInfo(object):
	def __init__(self, name, merch, price):
		self.goods_name = name
		self.merch_name = merch
		self.merprice = price
'''
CMall��
@����
mall_url������url
kwd���û������ؼ���
book����ʾ�û�������Ʒ���ͣ�ͼ��Ӱ�� / ����
@����
__init_����ʼ����������-ȥ�ļҵ꣺mall_url����ʲô��kwd����Ʒ���book
getInitURL����ȡ�û���������ʺ󷵻صļ������ҳ��URL
getResURL: ��ȡ�������ҳ��url֮��
����ҳ������Ʒƥ�����ߵĽ��ҳ��URL
getRes����������ƥ�����ߵ�ҳ�棬��ȡ��Ʒ��Ϣ��д��DB
'''
class CMall(object):
	def __init__(self, kwd, is_book, min_price, \
				mall_url = "http://langlang.cc/"):
		self.kwd = kwd
		self.is_book = is_book
		self.min_price = min_price
		#self.min_price = '��' + min_price + 'Ԫ'
		self.mall_url = mall_url
		self.py_log = CLog()
	def getRes(self, url):
		page = urllib2.urlopen(url).read().\
		decode('GBK').encode('utf-8')
		
		ret_info = []
		
		soup = BeautifulSoup(page)
		#��ȡ���ռ���ҳ�����Ʒ�б�
		deal_table = soup.find('table', {'class': 'deals'})
		#first, �۸���ͣ����粻�����û�Ҫ����ô�����Ҳ�����ܷ����û�
		#Ҫ�󣬿�ֱ�ӷ���
		min_price = deal_table.findAll('tr', {'class': 'first'}, limit = 1)[0]
		try:
			goods_name = str(min_price.h3.contents[0].string)
		except Exception, e:
			self.py_log.log("��ȡ��Ʒ����ʧ��", self.py_log.get_file_name(), self.py_log.get_line())
			goods_name = "NULL"
		try:
			merch_name = str(min_price.findAll('div', {'class': 'trustArea'})[1].contents[0].string)
		except Exception, e:
			merch_name = "NULL"
		try:
			merprice = min_price.findAll('span', {'class': 'merprice'})[0].contents[0].string
		except IndexError:
			merprice = "NULL"
		#�ж��Ƿ�С���û�Ҫ��۸�
		#if merprice < self.min_price
		#����python�Ƚ��ַ���Ĭ�ϴ���������λ�Ƚϣ����Ȳ������Ҳಹ0������2 > 10�����ĳ���
		#�����ֶ����ַ�������ಹ�룬����ֱ���ȶԱȳ��ȣ����ȴ�Ŀ϶��ǹ��
		#���ǲ�ȡ�����ֿ��׵ģ�ת���ɸ�����Ȼ��Ƚϣ�ע��Ƚϵĵط�������
		#���Ҫ����ͬ��
		if string.atof(merprice[1:-1]) > string.atof(self.min_price):
			return	False#��ͼ۸���Ȼ�����û����������ϲ�����
		#��������û�Ԥ�ڣ��洢��������Ʒ��Ϣ
		#ret_info.append(CInfo(goods_name.encode('gb2312'), merch_name.encode('gb2312'), str(merprice)))
		ret_info.append(CInfo(goods_name, merch_name, str(merprice)))
		'''
		print goods_name.decode('utf-8').encode('gbk')
		print merch_name.decode('utf-8').encode('gbk')
		print merprice
		'''
		#������̼��Ƿ���ϼ۸�Ҫ��
		deal_lists = deal_table.findAll('tr', {'class': 'imgCell'}, limit = 8)
		for deal_list in deal_lists:
			state = []
			try:
				goods_name = str(deal_list.h3.contents[0].string)
			except Exception, e:
				goods_name = "NULL"
			try:
				merch_name = str(deal_list.findAll('div', {'class': 'trustArea'})[1].contents[0].string)
			except Exception, e:
				merch_name = "NULL"
			try:
				merprice = deal_list.findAll('span', {'class': 'price'})[0].contents[0].string
			except IndexError, ir:
				self.py_log.log(str(ir), self.py_log.get_file_name(), self.py_log.get_line())
				#merprice = "NULL"
				
			'''
			# �����
			is_left = "NULL"
			images = deal_list.findAll('img')
			for img in images:
				is_left = img['src']
				if img['src'].find('quehuo') != -1:
					is_left = 'false'#False
					break
				elif img['src'].find('goumai') != -1:
					is_left = 'true'#True
					break
			is_left = deal_list.first('img')['src']		
			is_left = is_left.split('/')[-1].split('.')[-2]
			is_left = re.sub('*', '', str(deal_list.findAll('td')[4].string))
			except Exception, e:
				is_left = e #"NULL"
			'''
			#print merprice
			if string.atof(merprice[1:-1]) > string.atof(self.min_price):
				#print '����'
				return ret_info#���ּ۸�����û���������Ʒ��ֱ�ӽ���ö��
			#������ǿ��Է��͸��û�����Ϣ
			#state.append(goods_name)
			#state.append(merch_name)
			#state.append(merprice)
			#state.append(is_left)
			#ret_info.append(CInfo(goods_name.encode('gb2312'), merch_name.encode('gb2312'), str(merprice)))
			ret_info.append(CInfo(goods_name, merch_name, str(merprice)))
			
			'''
			print goods_name.decode('utf-8').encode('gbk')
			print merch_name.decode('utf-8').encode('gbk')
			print merprice#.decode('utf-8').encode('gbk')
			'''
			#����Ƿ��л���ͼƬ����
			#print is_left.strip()
			#print '-'.join(state)
			#������Ϻ��û�������Ϣ�����ݿ�������������ظ�����
		return ret_info
	def getResURL(self, url):
		page = urllib2.urlopen(url).read().decode('GBK').encode('utf-8')
		soup = BeautifulSoup(page)
		try:
			if self.is_book:
				search_div = soup.findAll('div', {'name': '__link_sale'})[0] #��һ��DOM-TREE��Ӧ��������ʽ[���ͼ��Ӱ����]
			elif not self.is_book:
				search_div = soup.findAll('div', {'class': 'goumai_anniu'})[0] #�ڶ���DOM-Tree��Ӧ��������ʽ[��԰ٻ���]
			else:
				search_div = "NULL"
		except Exception, e:
			self.py_log.log("��ȡ��Ʒ��Ϣʧ��", self.py_log.get_file_name(), self.py_log.get_line())
			return ""
		res_url = search_div.findAll('a')[0]['href'].strip()
		return res_url
	def getInitURL(self):
		response = mechanize.urlopen(self.mall_url)
		forms = mechanize.ParseResponse(response, backwards_compat=False)
		form = forms[0]
		#print form
		form["kwd"] = str(self.kwd)
		#form["kwd"] = "������ѧ"#"Nokia E71"

		# form.click() returns a mechanize.Request object
		# (see HTMLForm.click.__doc__ if you want to use only the forms support, and
		# not the rest of mechanize)
		#print urlopen(form.click()).read()
		request2 = form.click()
		try:
			response2 = mechanize.urlopen(request2)
		except mechanize.HTTPError, response2:
			self.py_log.log("�ύ������շ��������ص�URLʧ��", self.py_log.get_file_name(),\
						self.py_log.get_line())
			return
		url = response2.geturl()
		response2.close()
		#print "init url " + url
		return url
	
'''
�ӿ��ܽ᣺�û�ֻ���ṩ������Ʒ�������ַ��
��������Ʒ���ƣ���Ʒ���ͼ��Ӱ���� or not���������۸񼴿�
'''	

'''
CMallMain��:
@��Ա����
customers������һ���˿Ͷ���ȡ��DB��CMallMain��������
���ν������˿�����˿�ָ�����̳��鿴��Ҫ�������Ʒ�۸��Ƿ���Ϲ˿�Ԥ��
@����
getCustomers: ��DB�л�ȡһ���˿ͣ��˿��������ҽ���ǰ��д��DB
loginFetion����½����
sendSMS: �������û�Ԥ�ڵ���Ϣ���ͳ�ȥ
removeUser�������ݿ����Ƴ��Ѿ��õ�������Ϣ���û�
mallRun��ִ���ܵĵ���,���ÿ���˿Ͷ�Ҫ�����һ��CMall����
'''
class CMallMain:
	def __init__(self):
		self.py_log = CLog()
	def getCustomers(self, cdb):
		customers = []
		cdb = CDB()
		cect = cdb.getConnect()
		cur = cect.cursor()
		sql = 'select * from user_info_customerinfo'
		cur.execute(sql)
		res = cur.fetchall()
		for i in res:
			if i<> '':
				#print str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + ' ' + str(i[3]) + ' ' + i[4]
				customers.append(CCustomer(str(i[0]), CGoods(i[1].encode('gb2312'), i[2], str(i[3])), i[4]))
		#customers.append(CCustomer(CGoods("������ѧ", True, 11310.0), "15801178340"))
		#customers.append(CCustomer(CGoods("Nokia E71", False, 12999.0), "15801178340"))
		#customers.append(CCustomer(CGoods("sony ericsson MK16i", False, 12999.0), "15801178340"))
		#customers.append(CCustomer(CGoods("������˵��", True, 11310.0), "15801178340"))
		#customers.append(CCustomer(CGoods("��ƨ", True, 11310.0), "15801178340"))
		
		return customers
	def removeUser(self, cdb, customer):
		try:
			cect = cdb.getConnect()
			cur = cect.cursor()
			sql = 'delete from user_info_customerinfo where id = %s' #sql���ֻ��ʶ%s
			cur.execute(sql, (customer.id))
			cect.commit()
		except Exception, e:
			cect.rollback()
			self.py_log.log("���ݿ�ɾ��ʧ�ܣ������ع�", __file__, self.py_log.get_line())
			sys.exit(1)
	def loginFetion(self):
		is_login = False
		phone = PyFetion('15801178340', 'acmsenjing123', "TCP", debug="FILE")
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
	def sendSMS(self, phone, msg, customer):
		#print chardet.detect(msg)
		return phone.send_sms(msg, customer.phoneNum)
	def mallRun(self):
		cdb = CDB()
		customers = self.getCustomers(cdb)
		my_phone = self.loginFetion()
		for customer in customers:
			cmall = CMall(customer.goods.name, customer.goods.is_book,\
							customer.goods.min_price, customer.urls)
			res_url = ""
			try:
				res_url = cmall.getResURL(cmall.getInitURL())
			except Exception, e:
				self.py_log.log("sorry��������Ʒ������Ʒδ�ҵ�", self.py_log.get_file_name(), self.py_log.get_line())
				msg = "sorry��������Ʒ������Ʒδ�ҵ�".decode('gbk').encode('utf-8')
				sendOK = self.sendSMS(my_phone, msg, customer)
				self.removeUser(cdb, customer)
				if sendOK: #�û��ѵõ�������Ϣ��ɾ�����û�
					self.py_log.log("send to " + customer.phoneNum.encode('gbk') + " successfully!")
				else:
					self.py_log.log('����ӵ�£����͸� ' + customer.phoneNum.encode('gbk') + ' ����Ϣ���������ӳ� ')
				continue
			if res_url =="":
				self.py_log.log("sorry��ͬʱ������Ʒ������Ʒ���Ե���Ʒδ�ҵ�", self.py_log.get_file_name(), self.py_log.get_line())
				msg = "sorry��ͬʱ������Ʒ������Ʒ���Ե���Ʒδ�ҵ�".decode('gbk').encode('utf-8')
				sendOK = self.sendSMS(my_phone, msg, customer)
				sendOK = False
				self.removeUser(cdb, customer)
				if sendOK: #�û��ѵõ�������Ϣ��ɾ�����û�
					self.py_log.log("send to " + customer.phoneNum.encode('gbk') + " successfully!")
				else:
					self.py_log.log("����ӵ�£����͸�" + customer.phoneNum.encode('gbk') + "����Ϣ���������ӳ�")
				continue
			ret_info = cmall.getRes(res_url)
			if ret_info != False:
				for info in ret_info:
					#print 'find it ' + info.goods_name.decode('utf-8').encode('gbk') + ' ' + info.merprice.decode('utf-8').encode('gbk')
					#������Ϣ
					msg = '[Surprise!] ' + info.goods_name + ' at ' + info.merch_name + ' sell ' + info.merprice
					sendOK = self.sendSMS(my_phone, msg, customer)
					self.removeUser(cdb, customer)
					if sendOK: #�û��ѵõ�������Ϣ��ɾ�����û�
						self.py_log.log("send to " + customer.phoneNum.encode('gbk') + " successfully!")
					else:
						self.py_log.log("����ӵ�£����͸�" + customer.phoneNum.encode('gbk') + "����Ϣ���������ӳ�")
						
		cdb.close()
		my_phone.logout()
			
#example	
if __name__ == '__main__':
	cmm = CMallMain()
	cmm.mallRun()