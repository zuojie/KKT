#!/usr/bin/env python
#coding=gb2312

'''
@author: ������<author value = "������" />
@date: 2012/3/3
'''

import sys
import urllib2
import re, string
import mechanize
from lib.BeautifulSoup import BeautifulSoup
from lib.fetion import *

from PyLog import CLog
from PyDB import *

'''
CTicket�ࣺ
@����
_date��Ʊ�����ڡ�Y-M-D��
_from��������
_to��Ŀ�ĵ�
inc��Ʊ�����Ĺ�˾
property��Ʊ�����ԡ���Ʊ/��Ʊ����Ʊֻ����ؼۻ�Ʊ��
price��Ʊ�ļ۸�
'''
class CTicket(object):
	def __init__(self, _date, _from, _to, inc, property, price):
		self._date = _date
		self._from = _from
		self._to = _to
		self.inc = inc
		self.property = property
		self.price = price
'''
CCustomer��
@����
CTicket���˿�Ҫ�����Ʊ
phoneNum���˿͵绰
'''
class CCustomer(object):
	def __init__(self, ticket, phoneNum):
		self.ticket = ticket
		self.phoneNum = phoneNum

'''
CInfo�ࣺ���͸��û���Ϣ�����岿��
@����
merch_name��Ʊ���ļҹ�˾����
merprice��ƱĿǰ�ۼ�
'''
class CInfo(object):
	def __init__(self, name, merch, price):
		self.goods_name = name
		self.merch_name = merch
		self.merprice = price
'''
CTicketHall�ࣺ
@����
hall_url��Ʊ�����url
@����
getResURL����ȡ�������ҳ��url
getRes����ȡƱ������
'''
class CTicketHall(object):
	def __init__(self, hall_url):
		self.hall_url = hall_url
	def getResURL(self):
		response = mechanize.urlopen(self.hall_url)
		forms = mechanize.ParseResponse(response, backwards_compat=False)
		form = forms[0]
		#����ѡ�ť���ؼۻ�Ʊ
		form.set_value(["DealsFlight"], kind="singlelist", nr=0)
		form["fromCity"] = "����".decode('GBK').encode('utf-8')
		form["toCity"] = "֣��".decode('GBK').encode('utf-8')
		form["fromDate"] = "2012-03-05"
		form["toDate"] = "2012-03-05"
		print form
		
		req2 = form.click()
		try:
			resp2 = mechanize.urlopen(req2)
		except mechanize.HTTPError, resp2:
			pass
		#header
		for name, value in resp2.info().items():
			if name != 'date':
				print "%s: %s" % (name.title(), value)
		
		print resp2.geturl()
		#body
		#print resp2.read().decode('utf-8').encode('gbk')#.decode('GBK').encode('utf-8')
		resp2.close()
		return resp2.geturl()
	#�õ�Ʊ����Ϣ
	def getRes(self):
		url = self.getResURL()
		page = urllib2.urlopen(url).read()#.decode('GBK').encode('utf-8')
		soup = BeautifulSoup(page)
		main_wrapper = soup.findAll('div', {'class': 'main_wrapper'})[0]
		#print main_wrapper.prettify()
		clr_after = main_wrapper.findAll('div', {'class': 'clr_after'})[0]
		#print clr_after.prettify()
		items = clr_after.findAll('div', {'class': 'main'})[0]
		#print items.prettify()
		items1 = items.findAll('div', {'class': 'lowpriceList'})[0]
		print items1.prettify().decode('utf-8').encode('gbk')
		items2 = items1.findAll('div', {'id': 'hdivResultTable'})[0]
		#print items2.prettify().decode('utf-8').encode('gbk')
		
		for item in items2:
			print item
			inc = str(item.findAll('td', {'class': 'col3'})[0].contents[0].string)
			fly_time = str(item.findAll('td', {'class': 'col4'})[0].contents[0].string)
			_time = str(item.findAll('td', {'class': 'col2'})[0].contents[0].string)
			_discount = str(item.findAll('span', {'class': 'disc'})[0].contents[0].string)
			_price = str(item.findAll('span', {'class': 'pr'})[0].contents[0].string)
			
			print inc#.decode('utf-8').encode('gbk')
			print fly_time#.decode('utf-8').encode('gbk')
			print _time#.decode('utf-8').encode('gbk')
			print _discount.decode('utf-8').encode('gbk')
			print _price.decode('utf-8').encode('gbk')
		
#example
if __name__ == '__main__':
	ct = CTicketHall("http://flight.qunar.com/")
	ct.getRes()