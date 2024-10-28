import serial
import time
from threading import Thread
from multiprocessing import Manager
import logging


class Bot:
    BPS = 4800 
    # 스레드 속도
    threading_Time = 5/1000.
    serial_ = serial.Serial('/dev/ttyS0', BPS, timeout=0.01)
    serial_.flush() # serial cls
    manager = Manager()
    waiting = manager.list()
    recived = manager.Queue()
    logger = logging.getLogger("[Robot]")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # log를 console에 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    stream_handler.setLevel(logging.INFO)
    #log를 파일에 출력
    file_handler = logging.FileHandler("./logs/myRobot.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    def __init__(self, isPar4=False):
        self.isPar4 = isPar4
        # 시리얼 읽기 스레드 시작
        serial_t = Thread(target=self.__RX_Receiving, args=(Bot.serial_,))
        serial_t.daemon = True
        serial_t.start()
        self.head_center()
        self.head_down_65()
        """
        다음 행동에서 할 일 목록
        ball - 공 찾기
        walk - 걸어가기
        flag - 깃발 찾기
        ready - 세부 조정
        hit - 퍼팅
        """
        self.task = ""
        self.task2ball()
        time.sleep(2)


    # 시리얼 쓰기 함수
    def __TX_data(self,one_byte):  # one_byte= 0~255
        Bot.waiting.append(one_byte)
        Bot.logger.debug(f"send serial: {one_byte}")
        Bot.serial_.write(serial.to_bytes([one_byte]))  #python3
        while len(Bot.waiting) != 0:
            time.sleep(0.3)

    # 시리얼 읽기 함수
    def __RX_Receiving(self,ser):
        receiving_exit = 1
        while True:
            if receiving_exit == 0:
                break
            time.sleep(Bot.threading_Time)
            while ser.in_waiting > 0:
                result = ser.read(1)
                RX = int(ord(result))
                Bot.logger.debug(f"recived {RX} {Bot.waiting}")
                if RX in Bot.waiting:
                    Bot.waiting.remove(RX)
                else:
                    # Bot.logger.info("unexpected key", RX, Bot.waiting)
                    Bot.recived.put(RX)

    def test_TX(self, code):
        self.__TX_data(code)

    def task2ball(self):
        self.task = "ball"
        Bot.logger.info(f"now task is {self.task}")
        self.head_down_65()
        time.sleep(0.3)
    
    def task2walk(self):
        self.task = "walk"
        Bot.logger.info(f"now task is {self.task}")
        time.sleep(0.2)
        self.head_down_35()
        time.sleep(0.2)
    
    def task2flag(self):
        self.task = "flag"
        Bot.logger.info(f"now task is {self.task}")
        time.sleep(1)
        self.head_down_65()
        time.sleep(0.3)
    
    def task2ready(self):
        self.task = "ready"
        time.sleep(1)
        self.head_down_35()
        time.sleep(0.3)
        Bot.logger.info(f"now task is {self.task}")
    
    def task2hit(self):
        self.task = "hit"
        self.head_down_65()
        Bot.logger.info(f"now task is {self.task}")
        
    def head_angle(self): # 현재 머리 각도 가져오기
        '''
        현재 머리 각도 가져오기
        '''
        self.__TX_data(38)
        time.sleep(0.0001)
        return Bot.recived.get()

    def head_left_max(self): # 머리 왼쪽 끝까지 회전
        '''
        머리 왼쪽 끝까지 회전
        '''
        self.__TX_data(17)

    def head_right_max(self): # 머리 오른쪽 끝까지 회전
        '''머리 오른쪽 끝까지 회전'''
        self.__TX_data(27)

    def head_up(self): # 머리 위로
        '''머리 위로'''
        self.__TX_data(31)

    def head_down(self): # 머리 아래로
        '''머리 아래로'''
        self.__TX_data(34)
    
    def head_down_35(self):
        '''머리 아주 아래로'''
        self.__TX_data(29)
    
    def head_down_65(self):
        '''머리 약간 아래로'''
        time.sleep(1)
        self.__TX_data(8)

    def head_center(self):
        '''머리 중앙으로'''
        self.__TX_data(21)
    
    def body_left_45(self):
        '''로봇 왼쪽으로 45도 회전 '''
        self.__TX_data(41)
        
    def body_left_30(self):
        '''로봇 왼쪽으로 45도 회전 '''
        self.__TX_data(22)
    
    def body_right_30(self):
        '''로봇 오른쪽으로 45도 회전 '''
        self.__TX_data(24)

    def body_right_45(self):
        '''로봇 오른쪽으로 45도 회전 '''
        self.__TX_data(42)

    def body_left_10(self):
        '''로봇 왼쪽으로 10도 회전 '''
        self.__TX_data(4)

    def body_left_20(self):
        '''로봇 왼쪽으로 22.5도 회전 '''
        self.__TX_data(7)
    
    def body_right_20(self):
        '''로봇 오른쪽으로 22.5도 회전 '''
        self.__TX_data(9)

    def body_right_10(self):
        '''로봇 오른쪽으로 10도 회전 '''
        self.__TX_data(6)

    def body_left_5(self):
        '''로봇 왼쪽으로 5도 회전 '''
        self.__TX_data(1)

    def body_right_5(self):
        '''로봇 오른쪽으로 5도 회전 '''
        self.__TX_data(3)

    def left_20(self):
        '''로봇 왼쪽 옆걸음 20'''
        self.__TX_data(15)

    def right_20(self):
        '''로봇 오른쪽 옆걸음 20'''
        self.__TX_data(20)

    def left_10(self):
        '''로봇 왼쪽 옆걸음 10'''
        self.__TX_data(40)

    def right_10(self):
        '''로봇 오른쪽 옆걸음 10'''
        self.__TX_data(39)

    def left_70(self):
        '''로봇 왼쪽 옆걸음 미정'''
        self.__TX_data(14)
    
    def right_70(self):
        '''로봇 오른쪽 옆걸음 미정'''
        self.__TX_data(13)

    def head_left(self):
        '''로봇 머리 왼쪽 회전'''
        self.__TX_data(36)

    def head_right(self):
        '''로봇 머리 오른쪽 회전'''
        self.__TX_data(35)

    def go(self):
        '''로봇 앞으로 전진'''
        self.__TX_data(19)
    
    def back(self):
        '''로봇 뒤로 후진'''
        self.__TX_data(10)
    
    def stop(self):
        '''로봇 정지'''
        self.__TX_data(26)

    def hit(self, right=True):
        '''퍼팅 중'''
        if right:
            self.__TX_data(2)
        else:
            self.__TX_data() # 왼쪽 샷
    