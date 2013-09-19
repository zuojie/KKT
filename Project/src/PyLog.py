#!/usr/bin/env python
#coding=gb2312

'''
@<author value = 彭作杰 />
@<date value = 2012/2/26 />
'''

import inspect
import sys, time

'''
CLog类
@成员属性
@成员方法
'''
class CLog(object):
	def __init__(self, log_file = r"I:\2012BS\Project\index.log"):
		self.log_file = log_file
	def get_line(self):
		try:
			raise Exception
		except:
			return str(sys.exc_info()[2].tb_frame.f_back.f_lineno) + ' line'
	def get_file_name(self):
		file_name = inspect.currentframe().f_code.co_filename #得到的是路径 + 文件名
		return file_name.split('\\')[-1]  #只要文件名
	def log(self, log_info, file_name = "NULL", file_line = "-1"):
		log_time = time.ctime(time.time())
		try:
			file = open(self.log_file, 'a')
			'''
			print log_time + ' ' + file_name + ' ' + \
						file_line + ': ' + log_info
			'''
			file.write(log_time + ' ' + file_name + ' ' + \
						file_line + ': ' + log_info + '\n')
			file.close()
			return True
		except Exception, e:
			return False
#example
if __name__ == '__main__':
	py_log = CLog()
	py_log.log("test", py_log.get_file_name(), py_log.get_line())