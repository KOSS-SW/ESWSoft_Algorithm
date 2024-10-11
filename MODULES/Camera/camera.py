import cv2, time
import numpy as np
from math import tan
import logging

class Cam:
    W_View_size =  640  #320  #640
    H_View_size = int(W_View_size / 1.333)
    CENTER = W_View_size//2 + 100
    CENTERH = H_View_size//2
    FPS = 40
    ERROR = 10
    DEBUG = False
    MIN_AREA = [30,50]
    HIT_SPOT = (426,439)

    hsv_Lower_boll = (0, 108, 163)
    hsv_Upper_boll = (255, 176, 255) 
    hsv_Lower_flag = (164, 60, 60)
    hsv_Upper_flag = (255, 105, 151)

    def __init__(self, debug=False):
        self.logger = logging.getLogger("[Camera]")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # log를 console에 출력
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        #log를 파일에 출력
        file_handler = logging.FileHandler("./logs/cam.log")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.last_read = 0
        self.camera = cv2.VideoCapture(0)
        #self.camera = cv2.VideoCapture("./test.mp4")
        self.camera.set(3, Cam.W_View_size)
        self.camera.set(4, Cam.H_View_size)
        self.camera.set(5, Cam.FPS)
        Cam.DEBUG = debug
        time.sleep(0.5)
        tes, frame = self.camera.read()
        # 녹화 설정
        # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        # self.video = cv2.VideoWriter("./videoLogs/" + str(time.strftime('%Y-%m-%d %H:%M:%S')) + ".avi", fourcc, 20.0, (Cam.W_View_size, Cam.H_View_size))
        ("cam is initialized")

    def read(self):
        # try:
            for i in range(3):
                self.camera.grab()
                ret, self.frame =  self.camera.read()
                #self.video.write(self.frame)
            t = time.time()
            # print(t - self.last_read)
            self.last_read = t
            cv2.waitKey(100//Cam.FPS)
            if Cam.DEBUG:
                h,b,f = self.__process()
                cv2.line(self.frame, (Cam.CENTER,0), (Cam.CENTER,Cam.H_View_size), 5)
                cv2.line(self.frame, (Cam.CENTER+Cam.ERROR,0), (Cam.CENTER+Cam.ERROR,Cam.H_View_size), 5)
                cv2.line(self.frame, (Cam.CENTER-Cam.ERROR,0), (Cam.CENTER-Cam.ERROR,Cam.H_View_size), 5)
                cv2.line(self.frame, (0, Cam.CENTERH - Cam.ERROR * 5), (Cam.W_View_size, Cam.CENTERH - Cam.ERROR * 5), 5)
                
    
                cv2.imshow('mini CTS5 - Video', self.frame )
                cv2.imshow('mini CTS5 - Mask_boll', b)
                cv2.imshow('mini CTS5 - Mask_flag', f)
                cv2.waitKey(33)
                return h,b,f
            return self.__process()
        # except Exception as e:
        #     print(e)
        #     return (np.zeros((self.W_View_size, self.H_View_size, 3))) * 3
        
    def __process(self):
        hsv = cv2.cvtColor(cv2.medianBlur(self.frame,3), cv2.COLOR_BGR2YUV)  # HSV => YUV
        self.mask_boll = cv2.inRange(hsv, Cam.hsv_Lower_boll, Cam.hsv_Upper_boll)
        self.mask_flag = cv2.inRange(hsv, Cam.hsv_Lower_flag, Cam.hsv_Upper_flag)
        return hsv, self.mask_boll, self.mask_flag
    
    def detect_ball(self, mask_boll=0):
        if type(mask_boll) == int:
            mask_boll = self.mask_boll
        cnts_boll = cv2.findContours(mask_boll.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if len(cnts_boll) <= 0:
            return False, None
        c = max(cnts_boll, key=cv2.contourArea)
        ((X,Y),radius) = cv2.minEnclosingCircle(c)
        Area = cv2.contourArea(c) / Cam.MIN_AREA[0]
        if Area > 255:
            Area = 255
        if Area > Cam.MIN_AREA[0]:
            return True, (int(X), int(Y))
        return False, None
    
    def ball_is_center(self, bc):
        self.logger.info(bc[0], Cam.CENTER, abs(bc[0]-Cam.CENTER) < Cam.ERROR)
        return abs(bc[0]-Cam.CENTER) < Cam.ERROR
    
    def ball_is_center_far(self, bc):
        return abs(bc[0]-Cam.CENTER) < Cam.ERROR * 2
    
    def ball_is_center_h(self, bc):
        return bc[1] > Cam.CENTERH - Cam.ERROR * 5
    
    def ball_left(self, bc):
        return bc[0] < Cam.CENTER
    
    def ball_hitable(self, bc):
        dis = [abs(bc[0] - Cam.HIT_SPOT[0]), abs(bc[1] - Cam.HIT_SPOT[1])]
        if all(filter(lambda x: x < Cam.ERROR, dis)):
           return True, 0, 0
        else:
            return False, dis

    def flag_distance(self, angle):
        # 현재 목 각도
        angle -= 100
        return 11 * (1/tan(angle))


    def detect_flag(self):
        y_indices, x_indices = np.where(self.mask_flag == 255)
        flag_detected = False
        # 흰색 픽셀의 y좌표 중에서 가장 큰 값(최하단의 y좌표)을 찾습니다.
        if len(y_indices) > 0: # 마스크에 흰색 픽셀이 있는 경우
            # 최 하단점을 찾습니다
            bottom_y = np.max(y_indices)
            flag_center = (x_indices[y_indices == bottom_y][0],bottom_y)
            flag_detected = True
            return flag_detected, flag_center
        return flag_detected, None
    
    def detect_holecup(frame):
        # HSV 색공간으로 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 노란색 범위 설정 (HSV)
        lower_yellow = (30-10, 100, 100)
        upper_yellow = (30+10, 255, 255)
        
        # 노란색 마스크 생성
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # 노이즈 제거를 위한 모폴로지 연산
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 가장 큰 컨투어 찾기
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 새로운 마스크 생성 (가장 큰 영역만 포함)
            result_mask = np.zeros(mask.shape, np.uint8)
            cv2.drawContours(result_mask, [largest_contour], 0, 255, -1)
            
            # 결과 이미지 생성
            result = cv2.bitwise_and(frame, frame, mask=result_mask)
            return result, result_mask
        
        return frame, mask

    def flag_is_center(self, fc):
        return abs(fc[0]-Cam.CENTER) < Cam.ERROR
    
    def flag_left(self, fc):
        return fc[0] < Cam.CENTER - 100