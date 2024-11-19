import cv2, time
import numpy as np
from math import tan
import logging
import threading
if __name__ == "__main__":
    import calculate
else:
    from MODULES.Camera import calculate

class Cam:
    W_View_size = 640  #320  #640
    H_View_size = int(W_View_size / 1.333)
    CENTER = W_View_size//2
    CENTERH = H_View_size//2
    FPS = 40
    ERROR = 10
    DEBUG = False
    MIN_AREA = [5,60]
    HIT_SPOT = (426,449)

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
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        Cam.DEBUG = debug
        time.sleep(0.5)
        # 녹화 설정
        # fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        # self.video = cv2.VideoWriter("./videoLogs/" + str(time.strftime('%Y-%m-%d %H:%M:%S')) + ".avi", fourcc, 20.0, (Cam.W_View_size, Cam.H_View_size))

        self.lock = threading.Lock()
        self.current_frame = None
        self.last_frame_time = 0

        self.stop_thread = False
        self.thread = threading.Thread(target=self._reader)
        self.thread.daemon = True
        self.thread.start()
        self.read()

        self.logger.info("cam is initialized")    

    def _reader(self):
        while not self.stop_thread:
            ret, frame = self.camera.read()
            if not ret:
                break
            
            # 프레임과 시간 정보 업데이트
            with self.lock:
                self.current_frame = frame
                self.last_frame_time = time.time()

    def read(self):
        with self.lock:
            if self.current_frame is None:
                return None
            
            # 현재 프레임 복사본 반환
            self.frame = self.current_frame.copy()
        cv2.waitKey(100//Cam.FPS)
        if Cam.DEBUG:
            h,b,f = self.__process()
            self.draw_infinite_line(self.frame, (515, 381), (430, 214), (0, 255, 0), 2)
            cv2.line(self.frame, (Cam.CENTER,0), (Cam.CENTER,Cam.H_View_size), 5)
            cv2.line(self.frame, (Cam.CENTER+Cam.ERROR,0), (Cam.CENTER+Cam.ERROR,Cam.H_View_size), 5)
            cv2.line(self.frame, (Cam.CENTER-Cam.ERROR,0), (Cam.CENTER-Cam.ERROR,Cam.H_View_size), 5)
            cv2.line(self.frame, (0, Cam.CENTERH - Cam.ERROR * 10), (Cam.W_View_size, Cam.CENTERH - Cam.ERROR * 10), 5)
            ib, bc = self.detect_ball()
            isf, fc = self.detect_flag()
            cs = self.detect_holcup()
            self.logger.debug(f"circles in flag: {cs}")
            if cs :
                cv2.circle(self.frame, cs, 5, (0,0,0)) # 저장된 데이터를 이용해 원 그리기
            if ib:
                cv2.circle(self.frame, bc, 5, (0,0,0))
                if cs:
                    cv2.line(self.frame, cs,bc, 5)
                    self.logger.info(f"{calculate.calculateDistance(bc,cs)}")
            if isf:
                self.logger.debug(f"circles in flag: {self.flag_is_center(fc), self.get_y_flag_line(fc[0])-fc[1]}")
                cv2.circle(self.frame, fc, 5, (0,0,0))
            

            cv2.imshow('mini CTS5 - Video', self.frame )
            cv2.imshow('mini CTS5 - Mask_boll', self.mask_boll)
            cv2.imshow('mini CTS5 - Mask_flag', self.mask_flag)
            cv2.waitKey(33)
            return h,b,f
        return self.__process()
        # except Exception as e:
        #     print(e)
        #     return (np.zeros((self.W_View_size, self.H_View_size, 3))) * 3
        
    def __process(self):
        hsv = cv2.cvtColor(cv2.medianBlur(self.frame,3), cv2.COLOR_BGR2YUV)  # HSV => YUV
        self.mask_boll = cv2.inRange(hsv, Cam.hsv_Lower_boll, Cam.hsv_Upper_boll)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.inRange(hsv, Cam.hsv_Lower_flag, Cam.hsv_Upper_flag)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)    
        self.mask_flag = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        return hsv, self.mask_boll, self.mask_flag
    
    def draw_infinite_line(self, img, point1, point2, color, thickness):
        height, width = img.shape[:2]

        # 직선의 기울기와 y절편 계산
        if point2[0] - point1[0] != 0:  # 수직선이 아닌 경우
            m = (point2[1] - point1[1]) / (point2[0] - point1[0])
            b = point1[1] - m * point1[0]

            # 화면 왼쪽 끝과 오른쪽 끝의 y 좌표 계산
            print("m,b:: ", m,b)
            left_y = int(m * 0 + b)
            right_y = int(m * width + b)

            # 선 그리기
            cv2.line(img, (0, left_y), (width, right_y), color, thickness)
        else:  # 수직선인 경우
            cv2.line(img, (point1[0], 0), (point1[0], height), color, thickness)

    def get_y_flag_line(self, x):
        m,b = 1.964705882352941, -630.8235294117646
        return m * x + b

    
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
        self.logger.debug(f"{bc[0]}, {Cam.CENTER}")
        return abs(bc[0]-Cam.CENTER) < Cam.ERROR
    
    def ball_is_center_far(self, bc):
        return abs(bc[0]-Cam.CENTER) < Cam.ERROR * 2
    
    def ball_is_center_h(self, bc):
        return bc[1] > Cam.CENTERH - Cam.ERROR * 10
    
    def ball_left(self, bc):
        return bc[0] < Cam.CENTER
    
    def ball_hitable(self, bc):
        dis = [(bc[0] - Cam.HIT_SPOT[0]), (bc[1] - Cam.HIT_SPOT[1])]
        self.logger.debug(dis)
        z = list(map(lambda x: abs(x) < (Cam.ERROR), dis))
        self.logger.debug(z)
        return z[0], z[1], dis[0], dis[1]
        
    def flag_distance(self, angle):
        # 현재 목 각도
        angle -= 100
        return 11 * (1/tan(angle))


    def detect_flag(self):
        '''contours, _ = cv2.findContours(self.mask_flag, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 가장 큰 컨투어 찾기
        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) < Cam.MIN_AREA[1]:
                return False, None
            # 새로운 마스크 생성 (가장 큰 영역만 포함)
            result_mask = np.zeros(self.mask_flag.shape, np.uint8)
            cv2.drawContours(result_mask, [largest_contour], 0, 255, -1)
            y_indices, x_indices = np.where(result_mask == 255)
            bottom_y = np.max(y_indices)
            flag_center = (x_indices[y_indices == bottom_y][0],bottom_y)
            if self.DEBUG:
                self.logger.debug(f"flag center: {flag_center}")
                cv2.circle(self.frame, flag_center, 5, (255,255,0))
            return True, flag_center
        return False, None'''
        fc = self.detect_holcup()
        if fc:
            return True, fc
        else:
            return False, None
    
    def detect_holcup(self):
        # HSV 색공간으로 변환
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        
        # 노란색 범위 설정 (HSV)
        lower_yellow = (30-10, 100, 100)
        upper_yellow = (30+10, 255, 255)
        
        # 노란색 마스크 생성
        # mask = cv2.inRange(hsv, Cam.hsv_Lower_flag, Cam.hsv_Upper_flag)

        coords = np.column_stack(np.where(self.mask_flag > 0))

        # x 좌표의 최소값과 최대값 계산
        if coords.size > 0:
            x_center = int(np.median(coords[:, 1]))
            y_center = int(np.median(coords[:, 0]))  # y 좌표의 중앙값

            return (x_center, y_center)

        # 가우시안 블러 적용
        return False    
        
    def flag_is_center(self, fc, b=0):
        """
        fc : 깃발의 좌표 (x, y)
        """
        # return abs(fc[0]-(Cam.CENTER + b)) < Cam.ERROR
        return abs(self.get_y_flag_line(fc[0])-fc[1]) < Cam.ERROR*3
    
    def flag_left(self, fc):
        # return fc[0] < Cam.CENTER
        return (self.get_y_flag_line(fc[0])-fc[1]) < 0
    
    def calculate_ball_distance(self):
        """
        공과 로봇의 발 사이의 거리를 계산합니다.
        카메라 이미지에서 공의 위치와 픽셀 크기를 기반으로 실제 거리(cm)를 계산합니다.
        
        Returns:
            float: 공과 로봇 발 사이의 거리(cm)
        """
        _, bc = self.detect_ball()  # 공의 좌표 얻기
        if bc is None:
            return float('inf')  # 공이 감지되지 않으면 무한대 거리 반환
        
        # 공의 y좌표 (이미지 상단이 0, 하단이 최대값)
        ball_y = bc[1]
        
        # 이미지의 높이
        image_height = self.frame.shape[0]
        
        CAMERA_HEIGHT = 45  # 카메라가 지면에서 떨어진 높이 (cm)
        CAMERA_ANGLE = 45   # 카메라의 아래쪽 기울기 각도 (도)
        
        # 이미지 y좌표를 실제 거리로 변환 / 이미지의 하단이 로봇의 발 위치
        relative_y = (image_height - ball_y) / image_height
        
        # 거리 계산 (삼각법 사용)
        import math
        angle_rad = math.radians(CAMERA_ANGLE * relative_y)
        distance = CAMERA_HEIGHT * math.tan(angle_rad)
        
        return distance

if __name__ == "__main__":
    cam = Cam(True)
    while 1:
        cam.read()