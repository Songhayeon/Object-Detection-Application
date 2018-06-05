# -*- coding: utf-8 -*-

import socketserver
import object_detection_tutorial_test
from os.path import exists

HOST = ''
PORT = 9999

class MyTcpHandler(socketserver.BaseRequestHandler):
    def getFileFromClient(self):
        print('---------- 클라이언트로부터 파일 전송받는중')
        data_transferred = 0
        data = self.request.recv(1024)
     
        if not data:
            print('---------- 서버에 존재하지 않거나 전송중 오류발생')
            return
        
        filename='FromClient'
        
        with open('download/' + filename+".jpg", 'wb') as f:
            try:
                while data:
                    #print(data)
                    f.write(data)
                    data_transferred += len(data)
                    data = self.request.recv(1024)
            except Exception as e:
                print(e)

        print('---------- 파일[%s] 수신종료. 수신량 [%d]' % (filename, data_transferred))


    def handle(self):     
        print('클라이언트 [%s]:' % self.client_address[0])

        type = self.request.recv(1024)
        
        type = type.decode()
        
        if type == 'Send\n':
            self.getFileFromClient()
            object_detection_tutorial_test.start() ##### 물체인식 시작
        else:
            self.SendFileToClient()
       
        
        
    def SendFileToClient(self):
        print('---------- 클라이언트로 결과 전송중')
        idx = object_detection_tutorial_test.getMostSimilarPic()
        data_transferred = 0
        filename="./cropped/cropped_img{}.jpg".format(idx) #파일 임의로 지정해줘서 보여지는지 확인
        if not exists(filename):  # 파일이 해당 디렉터리에 존재하지 않으면
            return  # handle()함수를 빠져 나온다.

        print('---------- 파일[%s] 전송 시작 ' % filename)
        with open(filename, 'rb') as f:
            try:
                data = f.read(1024)  # 파일을 1024바이트 읽음
                while data:  # 파일이 빈 문자열일때까지 반복
                    data_transferred += self.request.send(data)
                    data = f.read(1024)
            except Exception as e:
                print(e)

        print('---------- 전송완료[%s], 전송량[%d]' % (filename, data_transferred))


def runServer():
    print('----------   Server Start   ----------')

    try:
        server = socketserver.TCPServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('----------   Server End    ----------')


runServer()