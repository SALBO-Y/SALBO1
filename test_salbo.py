import sys
import win32com.client
import requests


## 접속 확인
instCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
print(instCpCybos.IsConnect)



## 공시뉴스 초단위 불러오기
class perpetualTimer():
    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = Timer(self.t, self.handle_function)
        
    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()
        self.thread.cancel()
    
    def start(self):
        self.thread.start()
    
    def cancel(self):
        self.thread.cancel()
        

## 메인화면
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SABLO_NEWS_BOT")
        self.setGeometry(300, 300, 1200, 700)
        self.setTable()
        self.current_timer = ""
        self.start_timer()
        
        ### URL 찾기
        self.apiUrl = ""
        
        self.thread_cnt = 0
        self.last_title = ""
    





## 매수주문
class 