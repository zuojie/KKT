#!/usr/bin/env python
#coding=gb2312

'''
@<author value = "彭作杰" />
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
CGoods类：
@属性
name：商品名字
book：商品类别，图形影像类或者百货类
min_price：用户购买此商品的期望价位
'''
class CGoods(object):
	def __init__(self, name, is_book, min_price):
		self.name = name
		self.is_book = is_book
		self.min_price = min_price
'''
CCustomer类
@属性
urls：顾客购物的网店地址列表【demo指定只有一个langlang.cc】
goods：用户要购买的商品
phoneNum：用户的电话号码
'''
class CCustomer:
	def __init__(self, id, goods, phoneNum, urls = "http://langlang.cc/"):
		self.id = id
		self.goods = goods
		self.phoneNum = phoneNum
		self.urls = urls

'''
CInfo类：发送给用户信息的主体部分
@属性
goods_name：商品名字
merch_name：商品在哪里出售
merprice：商品目前售价
'''
class CInfo(object):
	def __init__(self, name, merch, price):
		self.goods_name = name
		self.merch_name = merch
		self.merprice = price
'''
CMall类
@属性
mall_url：网店url
kwd：用户检索关键字
book：表示用户检索物品类型：图书影视 / 其他
@方法
__init_：初始化函数参数-去哪家店：mall_url，买什么：kwd，商品类别：book
getInitURL：获取用户输入检索词后返回的检索结果页面URL
getResURL: 获取检索结果页面url之后，
返回页面中商品匹配度最高的结果页面URL
getRes：根据最终匹配度最高的页面，提取商品信息，写入DB
'''
class CMall(object):
	def __init__(self, kwd, is_book, min_price, \
				mall_url = "http://langlang.cc/"):
		self.kwd = kwd
		self.is_book = is_book
		self.min_price = min_price
		#self.min_price = '￥' + min_price + '元'
		self.mall_url = mall_url
		self.py_log = CLog()
	def getRes(self, url):
		page = urllib2.urlopen(url).read().\
		decode('GBK').encode('utf-8')
		
		ret_info = []
		
		soup = BeautifulSoup(page)
		#获取最终检索页面的商品列表
		deal_table = soup.find('table', {'class': 'deals'})
		#first, 价格最低，假如不符合用户要求，那么下面的也不可能符合用户
		#要求，可直接返回
		min_price = deal_table.findAll('tr', {'class': 'first'}, limit = 1)[0]
		try:
			goods_name = str(min_price.h3.contents[0].string)
		except Exception, e:
			self.py_log.log("获取商品名称失败", self.py_log.get_file_name(), self.py_log.get_line())
			goods_name = "NULL"
		try:
			merch_name = str(min_price.findAll('div', {'class': 'trustArea'})[1].contents[0].string)
		except Exception, e:
			merch_name = "NULL"
		try:
			merprice = min_price.findAll('span', {'class': 'merprice'})[0].contents[0].string
		except IndexError:
			merprice = "NULL"
		#判断是否小于用户要求价格
		#if merprice < self.min_price
		#由于python比较字符串默认从左至右逐位比较，长度不足在右侧补0，导致2 > 10这样的成立
		#所以手动将字符串在左侧补齐，或者直接先对比长度，长度大的肯定是贵的
		#我们采取第三种靠谱的，转化成浮点数然后比较，注意比较的地方有两处
		#如果要改请同步
		if string.atof(merprice[1:-1]) > string.atof(self.min_price):
			return	False#最低价格仍然高于用户期望，果断不玩了
		#否则符合用户预期，存储待发送商品信息
		#ret_info.append(CInfo(goods_name.encode('gb2312'), merch_name.encode('gb2312'), str(merprice)))
		ret_info.append(CInfo(goods_name, merch_name, str(merprice)))
		'''
		print goods_name.decode('utf-8').encode('gbk')
		print merch_name.decode('utf-8').encode('gbk')
		print merprice
		'''
		#检查别的商家是否符合价格要求
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
			# 检查存货
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
				#print '高了'
				return ret_info#出现价格高于用户期望的商品后，直接结束枚举
			#下面的是可以发送给用户的信息
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
			#输出是否有货的图片链接
			#print is_left.strip()
			#print '-'.join(state)
			#发送完毕后将用户订制信息从数据库中清除，以免重复发送
		return ret_info
	def getResURL(self, url):
		page = urllib2.urlopen(url).read().decode('GBK').encode('utf-8')
		soup = BeautifulSoup(page)
		try:
			if self.is_book:
				search_div = soup.findAll('div', {'name': '__link_sale'})[0] #第一种DOM-TREE对应的搜索方式[针对图书影视类]
			elif not self.is_book:
				search_div = soup.findAll('div', {'class': 'goumai_anniu'})[0] #第二种DOM-Tree对应的搜索方式[针对百货类]
			else:
				search_div = "NULL"
		except Exception, e:
			self.py_log.log("获取商品信息失败", self.py_log.get_file_name(), self.py_log.get_line())
			return ""
		res_url = search_div.findAll('a')[0]['href'].strip()
		return res_url
	def getInitURL(self):
		response = mechanize.urlopen(self.mall_url)
		forms = mechanize.ParseResponse(response, backwards_compat=False)
		form = forms[0]
		#print form
		form["kwd"] = str(self.kwd)
		#form["kwd"] = "具体数学"#"Nokia E71"

		# form.click() returns a mechanize.Request object
		# (see HTMLForm.click.__doc__ if you want to use only the forms support, and
		# not the rest of mechanize)
		#print urlopen(form.click()).read()
		request2 = form.click()
		try:
			response2 = mechanize.urlopen(request2)
		except mechanize.HTTPError, response2:
			self.py_log.log("提交表单后接收服务器返回的URL失败", self.py_log.get_file_name(),\
						self.py_log.get_line())
			return
		url = response2.geturl()
		response2.close()
		#print "init url " + url
		return url
	
'''
接口总结：用户只需提供购买商品的网店地址，
检索的商品名称，商品类别【图书影视类 or not】，期望价格即可
'''	

'''
CMallMain类:
@成员变量
customers：持有一批顾客对象，取自DB；CMallMain类任务是
依次将各个顾客送入顾客指定的商场查看需要购买的商品价格是否符合顾客预期
@方法
getCustomers: 从DB中获取一批顾客；顾客数据由且仅由前端写入DB
loginFetion：登陆飞信
sendSMS: 将符合用户预期的信息发送出去
removeUser：从数据库中移除已经得到所需信息的用户
mallRun：执行总的调度,针对每个顾客都要构造出一个CMall对象
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
		#customers.append(CCustomer(CGoods("具体数学", True, 11310.0), "15801178340"))
		#customers.append(CCustomer(CGoods("Nokia E71", False, 12999.0), "15801178340"))
		#customers.append(CCustomer(CGoods("sony ericsson MK16i", False, 12999.0), "15801178340"))
		#customers.append(CCustomer(CGoods("让数字说话", True, 11310.0), "15801178340"))
		#customers.append(CCustomer(CGoods("狗屁", True, 11310.0), "15801178340"))
		
		return customers
	def removeUser(self, cdb, customer):
		try:
			cect = cdb.getConnect()
			cur = cect.cursor()
			sql = 'delete from user_info_customerinfo where id = %s' #sql语句只认识%s
			cur.execute(sql, (customer.id))
			cect.commit()
		except Exception, e:
			cect.rollback()
			self.py_log.log("数据库删除失败，发生回滚", __file__, self.py_log.get_line())
			sys.exit(1)
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
				self.py_log.log("sorry，符合商品名的商品未找到", self.py_log.get_file_name(), self.py_log.get_line())
				msg = "sorry，符合商品名的商品未找到".decode('gbk').encode('utf-8')
				sendOK = self.sendSMS(my_phone, msg, customer)
				self.removeUser(cdb, customer)
				if sendOK: #用户已得到订制信息，删除此用户
					self.py_log.log("send to " + customer.phoneNum.encode('gbk') + " successfully!")
				else:
					self.py_log.log('网络拥堵，发送给 ' + customer.phoneNum.encode('gbk') + ' 的信息将会稍有延迟 ')
				continue
			if res_url =="":
				self.py_log.log("sorry，同时符合商品名和商品属性的商品未找到", self.py_log.get_file_name(), self.py_log.get_line())
				msg = "sorry，同时符合商品名和商品属性的商品未找到".decode('gbk').encode('utf-8')
				sendOK = self.sendSMS(my_phone, msg, customer)
				sendOK = False
				self.removeUser(cdb, customer)
				if sendOK: #用户已得到订制信息，删除此用户
					self.py_log.log("send to " + customer.phoneNum.encode('gbk') + " successfully!")
				else:
					self.py_log.log("网络拥堵，发送给" + customer.phoneNum.encode('gbk') + "的信息将会稍有延迟")
				continue
			ret_info = cmall.getRes(res_url)
			if ret_info != False:
				for info in ret_info:
					#print 'find it ' + info.goods_name.decode('utf-8').encode('gbk') + ' ' + info.merprice.decode('utf-8').encode('gbk')
					#发送信息
					msg = '[Surprise!] ' + info.goods_name + ' at ' + info.merch_name + ' sell ' + info.merprice
					sendOK = self.sendSMS(my_phone, msg, customer)
					self.removeUser(cdb, customer)
					if sendOK: #用户已得到订制信息，删除此用户
						self.py_log.log("send to " + customer.phoneNum.encode('gbk') + " successfully!")
					else:
						self.py_log.log("网络拥堵，发送给" + customer.phoneNum.encode('gbk') + "的信息将会稍有延迟")
						
		cdb.close()
		my_phone.logout()
			
#example	
if __name__ == '__main__':
	cmm = CMallMain()
	cmm.mallRun()