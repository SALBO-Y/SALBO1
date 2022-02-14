import sys
import lib as lib
#import kiwoom as ki

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *

#import pandas as pd
from pprint import pprint
import re
import requests
from threading import Timer, Thread, Event

import json
from collections import OrderedDict

import webbrowser
from functools import partial

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

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("뉴스매매(Makeby 욱)")
        self.setGeometry(300, 300, 1200, 700)
        self.setTable()

        #self.t = perpetualTimer(1, self.startNews)
        #self.t.start()

        #timer = QTimer()
        #timer.timeout.connect(self.startNews)
        #timer.start(1000)
        self.current_timer = ""
        #self.start_timer() #로그인후 실행하도록 변경

        self.apiUrl = "API URL은 비밀"

        self.thread_cnt = 0
        self.last_title = ""

        #키움개인정보
        #self.user_id = "dev84" #테스트
        self.user_id = ""

        #print(sys.version)

        #키움증권
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        #self.kiwoom.event_connect_loop = QEventLoop()
        #self.kiwoom.event_connect_loop.exec_()
        #print(self.kiwoom)
        #ki_instance = ki.Kiwoom()

        self.btn1 = QPushButton("로그인", self)
        self.btn1.move(1000, 20)
        #btn1.clicked.connect(ki_instance.btn1_clicked)
        self.btn1.clicked.connect(self.btn1_clicked)

        btn2 = QPushButton("상태체크", self)
        btn2.move(1100, 20)
        #btn2.clicked.connect(ki_instance.btn2_clicked)
        btn2.clicked.connect(self.btn2_clicked)

        '''
        self.ed = QLineEdit()
        self.ed.move(700, 50)
        self.ed.setText("홍길동")  # 텍스트 쓰기
        text = self.ed.text()  # 텍스트 읽기
        self.ed.setPlaceholderText("이름을 입력하시오") # Watermark로 텍스트 표시
        self.ed.selectAll() # 텍스트 모두 선택
        #ed.setReadOnly(True)# 에디트는 읽기 전용으로
        #e.setEchoMode(QLineEdit.Password)# Password 스타일 에디트
        '''
        keywordLabel = QLabel("종목&키워드 매칭(종목코드:키워드1,키워드2,키워드3...)", self)
        keywordLabel.setGeometry(510, 50, 500, 50)

        self.keywordbtn = QPushButton("매칭 저장", self)
        self.keywordbtn.move(1100, 60)
        self.keywordbtn.clicked.connect(self.keywordbtn_clicked)

        self.textEdit = QTextEdit(self)
        self.textEdit.resize(670, 250)
        self.textEdit.move(510, 100)


        logLabel = QLabel("로그", self)
        logLabel.setGeometry(510, 370, 500, 50)

        self.textEdit2 = QTextEdit(self)
        self.textEdit2.resize(670, 250)
        self.textEdit2.move(510, 420)
        #self.textEdit2.setReadOnly(True)

        """""
        btn1 = QPushButton("Click me", self)
        btn1.move(20, 20)
        btn1.clicked.connect(self.btn1_clicked)
        """

    def start_timer(self):
        if self.current_timer:
            self.current_timer.stop()
            self.current_timer.deleteLater()

        self.current_timer = QTimer()
        self.current_timer.timeout.connect(self.startNews)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(1000)

    def keywordbtn_clicked(self):
        #print("저장")
        content = self.textEdit.toPlainText()
        #print(content)
        #print(self.user_id)

        post_data = {"type": "keyword_save", "stock_id": self.user_id, "content": content}
        r = requests.post(self.apiUrl, data=post_data)
        result_json = r.text #{"result":"OK"}
        #print(result_json)

        # JSON 디코딩
        dict = json.loads(result_json)
        #print("result = " + dict['result']) #OK
        if dict['result'] == "OK":
            w = QWidget()  # The QWidget widget is the base class
            w.setWindowTitle('키워드저장버튼')
            w.resize(400, 200)
            result = QMessageBox.information(w, "Information", "저장완료")

            #if result == QMessageBox.Ok:
            #   myTextbox.setText("Clicked OK on Information.")

    def btn1_clicked(self):
        #print("로그인 버튼 클릭")
        ret = self.kiwoom.dynamicCall("CommConnect()")
        if ret == 0:
            self.statusBar().showMessage("로그인 창 열기 성공")
            #self.btn1.setText('로그인 정보보기')
            #self.getLoginInfo()
        else:
            self.statusBar().showMessage("로그인 창 열기 실패")
        #print(ret)

    def btn1_clicked_logined(self):
        print("ok")

    #로그인 상태 확인
    def btn2_clicked(self):
        if self.kiwoom.dynamicCall("GetConnectState()") == 0:
            self.statusBar().showMessage("Not connected")
        else:
            self.statusBar().showMessage("Connected")

    #로그인 유저 정보 호출
    def getLoginInfo(self, type):
        #print("getLoginInfo")
        info = self.kiwoom.dynamicCall("GetLoginInfo(QString)", type)
        #print(info)
        return info

    #로그인 후 실행되는 함수
    def event_connect(self, code):
        if code == 0:
            self.statusBar().showMessage("로그인 성공")
            self.user_id = self.getLoginInfo("USER_ID")
            self.btn1.setText(self.user_id + "님 로그인중");
            #버튼 이벤트 해제해야 하는데 일단 스킵

            #종목코드:키워드 정보 가져오기
            post_data = {"type":"get_keyword", "stock_id":self.user_id}
            r = requests.post(self.apiUrl, data=post_data)
            result_json = r.text #{"result":"OK"}

            # JSON 디코딩
            dict = json.loads(result_json)
            data = dict['data']
            print("종목키워드 데이터 = " + data)
            self.textEdit.setText(data)

            self.start_timer()
        else:
            self.statusBar().showMessage("로그인 실패")

        #print("event_connect 호출됨")
        #self.event_connect_loop.exit()

    def setTable(self):
        #self.setGeometry(5,5,200,200)

        newsLabel = QLabel("실시간 뉴스", self)
        newsLabel.setGeometry(5, 5, 500, 50)

        self.tableWidget = QTableWidget(self)

        #self.tableWidget.resize(500, 500)
        self.tableWidget.setGeometry(5, 50, 500, 500)

        self.tableWidget.setRowCount(20)
        self.tableWidget.setColumnCount(3)

        #self.tableWidget.setVerticalHeaderLabels(['1','2'])
        self.tableWidget.setHorizontalHeaderLabels(['제목', '시간', '상세보기'])

        #데이터 넣기
        #self.setTableWidgetData()
        #self.startNews()

    def startNews(self):
        self.thread_cnt = self.thread_cnt + 1
        print("뉴스 쓰레드 가동(" + str(self.thread_cnt) + ")")
        
        #뉴스 쓰레드 가동(283) 에서
        #Process finished with exit code -1073740940 (0xC0000374) 에러발생
        #Process finished with exit code -1073741819 (0xC0000005)
        #Process finished with exit code -1073741819 (0xC0000005)

        #뉴스 저장하기
        #self.setNews2()

        #뉴스 가져오기
        #self.getNews()

        #뉴스 쓰레드 가동(281) 에서
        #Process finished with exit code -1073740940 (0xC0000374)
        self.getSetNews()

        #self.t = perpetualTimer(1, self.startNews)
        #self.t.start()

        #timer = QTimer()
        #timer.timeout.connect(self.startNews)
        #timer.start(1000)

        self.start_timer()

    '''
    def setTableWidgetData(self):
        self.tableWidget.setItem(0, 0, QTableWidgetItem("(0,0)"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("(0,1)"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("(1,0)"))
        self.tableWidget.setItem(1, 1, QTableWidgetItem("(1,1)"))
    '''

    """
    def btn1_clicked(self):
        QMessageBox.about(self, "message", "clicked")
    """

    #API 서버에서 뉴스크롤링 실행시키고, 바로 가져오기
    def getSetNews(self):
        post_data = {"type": "getset", "stock_id": self.user_id}
        r = requests.post(self.apiUrl, data=post_data)
        result_json = r.text #{"result":"OK"}

        # JSON 디코딩
        dict = json.loads(result_json)
        #print("getsetNews = " + dict['result'])

        #매칭된 키워드가 있으면 로그로 보여주기
        '''
        뉴스 쓰레드 가동(135)
        {'111': ['(주)', '결과']}
        '''
        if dict['log_text']:
            content = self.textEdit2.toPlainText()
            self.textEdit2.setText(dict['log_text'] + content)

        #print(dict['list'])
        cnt = 0
        #self.tableWidget.setRowCount(20)

        for row in dict['list']:
            if cnt == 0:
                if self.last_title == row['title']:
                    break
                else:
                    #print(row['title'] + " " + row['time'])
                    self.last_title = row['title']
                    #for i in range(0, 20):
                    #    self.tableWidget.setItem(i, 0, QTableWidgetItem("1"))
                    #    self.tableWidget.setItem(i, 1, QTableWidgetItem("1"))

            title = row['title'][0:30]
            self.tableWidget.setItem(cnt, 0, QTableWidgetItem(title))
            self.tableWidget.setItem(cnt, 1, QTableWidgetItem(row['time']))

            detailbtn = QPushButton("보기")
            #detailbtn.clicked.connect(lambda:self.detailbtn_clicked(row['idx']))
            detailbtn.clicked.connect(partial(self.detailbtn_clicked, row['idx']))
            self.tableWidget.setCellWidget(cnt, 2, detailbtn)
            #print(row['idx'])

            #데이터 갱신을 위해 포커스를 주자
            self.tableWidget.setCurrentCell(cnt, 0)
            self.tableWidget.setCurrentCell(cnt, 1)
            self.tableWidget.setCurrentCell(cnt, 2)
            cnt = cnt + 1

        #각 열크기 맞춤
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    #기사 상세보기 띄우기
    def detailbtn_clicked(self, idx):
        #print(idx)
        url = self.apiUrl + "?type=news_detail&idx=" + idx + "&stock_id=" + self.user_id
        webbrowser.open(url)

    #API 서버에서 뉴스크롤링 실행시키기
    def setNews2(self):
        post_data = {"type": "set", "stock_id": self.user_id}
        r = requests.post(self.apiUrl, data=post_data)
        result_json = r.text #{"result":"OK"}

        # JSON 디코딩
        dict = json.loads(result_json)
        print("setNews2 = " + dict['result'])


    #파이썬 자체에서 크롤링
    def setNews(self):
        #공시정보 가져오기
        #lib.get_financial_statements('http://dart.fss.or.kr/api/search.json?auth=5d7fe977e575fb2ec15661d0a1556f40793237f6')
        outhtml = lib.get_financial_statements('크롤링 주소는 비밀')
        #print(outhtml)
        #output = re.match(r'(?s).*<!-- List BBS Block Start -->(.*)<!-- //List BBS Block End -->.*', outhtml, re.M|re.I)
        #print(output.group(1))
        #output = re.match(r'(?s).*<div class="newListArea">(.*)</div>(.*)</div>.*', output.group(1), re.M|re.I)
        output = re.match(r'(?s).*<!-- %%LIST data%% -->(.*)<!-- %%ENDLIST data%% -->.*', outhtml, re.M | re.I)
        output_data = ''
        if output is not None:
            output_data = output.group(1)
            #print(output)
        else:
            print("젠장... 비었음...")

        #print(output_data)
        outlist = re.split('</tr>', output_data)
        #pprint(outlist)

        cnt = 0
        all_json = OrderedDict()
        for row in outlist:
            #date = lib.get_between_string(row, '<div id="date_0">', '</div>')
            #print(row)
            row_list = re.split('<td', row)
            #pprint(row_list)
            #print(row_list[2])
            #print(lib.strip_tags(row_list[3]))
            #print(row_list[3])
            date = ''
            time = ''
            title = ''
            try:
                row_json = OrderedDict()
                tmp = re.match(r'(?s).*<div id="date_.*">(.*)</div></td>.*', row_list[1])
                date = tmp.group(1)

                tmp = re.match(r'(?s).*<div id="time_.*">(.*)</div></td>.*', row_list[2])
                time = tmp.group(1)

                tmp = re.match(r'(?s).*<div id=\'title_.*\'>(.*)</div></a>.*', row_list[3])
                title = tmp.group(1)
                title = title.replace('&nbsp; ','')

                row_json['date'] = date
                row_json['time'] = time
                row_json['title'] = title

                all_json[str(cnt)] = row_json
            except:
                '''
                print("끝줄에러")
                '''

            '''
            test = ""
            test += "date = " + date + " || "
            test += "time = " + time + " || "
            test += "title = " + title + " || "
            print(str(cnt) + " = " + test)
            '''
            cnt = cnt + 1


        #pprint(all_json)
        jsonString = json.dumps(all_json)
        post_data = {'data': jsonString, "type": "news_toss", "stock_id": self.user_id}
        #print(jsonString)
        #pprint(post_data)

        #디비에 저장
        r = requests.post(self.apiUrl, data=post_data)
        result_json = r.text #{"result":"OK"}


    def getNews(self):
        post_data = {"type": "get", "stock_id": self.user_id}
        r = requests.post(self.apiUrl, data=post_data)
        result_json = r.text #{"result":"OK"}
        #print("result_json = " + result_json)

        # JSON 디코딩
        dict = json.loads(result_json)

        # Dictionary 데이타 체크
        print("getNews = " + dict['result'])

        #print(dict['list'])
        cnt = 0
        #self.tableWidget.setRowCount(20)

        for row in dict['list']:
            if cnt == 0:
                if self.last_title == row['title']:
                    break
                else:
                    #print(row['title'] + " " + row['time'])
                    self.last_title = row['title']
                    #for i in range(0, 20):
                    #    self.tableWidget.setItem(i, 0, QTableWidgetItem("1"))
                    #    self.tableWidget.setItem(i, 1, QTableWidgetItem("1"))

            title = row['title'][0:40]
            self.tableWidget.setItem(cnt, 0, QTableWidgetItem(title))
            self.tableWidget.setItem(cnt, 1, QTableWidgetItem(row['time']))

            #데이터 갱신을 위해 포커스를 주자
            self.tableWidget.setCurrentCell(cnt, 0)
            self.tableWidget.setCurrentCell(cnt, 1)
            cnt = cnt + 1

        #각 열크기 맞춤
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()