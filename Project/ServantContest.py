#!/usr/bin/env python 
#coding=gb2312

'''
@<author value = "������" />
@<date value = 2012/3/1 />
'''

import win32serviceutil 
import win32service 
import win32event
import time
import sys, os, string
import MySQLdb

from src.ContestJson import *

# ��Ϣ�����˷����࣬����Runһ��
class MainServiceContest(win32serviceutil.ServiceFramework):
	_svc_name_ = "MainServiceContest" 
	_svc_display_name_ = "MainService-Contest" 
	def __init__(self, args): 
		win32serviceutil.ServiceFramework.__init__(self, args) 
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		# ����ʼ
	def SvcStop(self): 
		# �ȸ���SCMֹͣ������� 
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
		# �����¼� 
		win32event.SetEvent(self.hWaitStop) 
		# �������
	def SvcDoRun(self): 
		# Set an amount of time to wait (in milliseconds) between runs
		# run once per hour
		#self.timeout = 1000 * 60 * 60 #unit ms
		self.timeout = 2 * 60 * 60 * 1000 # 2 hour per round
		fetioner = CContestMain(24 * 1) # 24Сʱ֮�ڵı�����������
		while 1:
			#��ʱ�����������
			rc = win32event.WaitForSingleObject(self.hWaitStop,self.timeout)
			# Check to see if self.hWaitStop happened
			if rc == win32event.WAIT_OBJECT_0:
				# Stop signal encountered
				break
			else:
				# ��timeoutΪ�������
				begin = time.clock()
				try:
					res = fetioner.contestRun()
				except Exception, e:
					#added by arvin peng
					fetioner.Log('[Error] ' + str(e), PyDebug().line())
					continue
					
				# ����ʱ��
				timeCost = time.clock() - begin 
				#added by arvin peng
				if res:
					fetioner.Log('fetioner run ok ' + str(timeCost) + ' secs', PyDebug().line())
				else:
					fetioner.Log('fetioner run fail ' + str(timeCost) + ' secs', PyDebug().line())
					
if __name__=='__main__': 
	win32serviceutil.HandleCommandLine(MainServiceContest)