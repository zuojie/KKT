#!/usr/bin/env python 
#coding=gb2312

'''
@<author value = "彭作杰" />
@<date value = 2012/3/1 />
'''

import win32serviceutil 
import win32service 
import win32event
import time
import sys, os, string
import MySQLdb

from src.Habit import *

# 信息机器人服务类，定期Run一次
class MainServiceHabit(win32serviceutil.ServiceFramework):
	_svc_name_ = "MainServiceHabit" 
	_svc_display_name_ = "MainService-Habit" 
	def __init__(self, args): 
		win32serviceutil.ServiceFramework.__init__(self, args) 
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		# 服务开始
	def SvcStop(self): 
		# 先告诉SCM停止这个过程 
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
		# 设置事件 
		win32event.SetEvent(self.hWaitStop) 
		# 服务结束
	def SvcDoRun(self): 
		# Set an amount of time to wait (in milliseconds) between runs
		# run once per hour
		#self.timeout = 1000 * 60 * 60 #unit ms
		self.timeout = 24 * 60 * 60 * 1000 # 24 hours per round
		fetioner = CHabitMain()
		while 1:
			#定时器，像监听器
			rc = win32event.WaitForSingleObject(self.hWaitStop,self.timeout)
			# Check to see if self.hWaitStop happened
			if rc == win32event.WAIT_OBJECT_0:
				# Stop signal encountered
				break
			else:
				# 以timeout为间隔运行
				begin = time.clock()
				try:
					res = fetioner.habitRun()
				except Exception, e:
					#added by arvin peng
					fetioner.Log('[Error] ' + str(e), PyDebug().line())
					continue
					
				# 计算时耗
				timeCost = time.clock() - begin 
				#added by arvin peng
				if res:
					fetioner.Log('fetioner run ok ' + str(timeCost) + ' secs', PyDebug().line())
				else:
					fetioner.Log('fetioner run fail ' + str(timeCost) + ' secs', PyDebug().line())
					
if __name__=='__main__': 
	win32serviceutil.HandleCommandLine(MainServiceHabit)