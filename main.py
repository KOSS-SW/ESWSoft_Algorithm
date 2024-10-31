# -*- coding: utf-8 -*-

from MODULES.Camera.camera import Cam
from MODULES.Camera import calculate
from MODULES.Motion.robot import Bot

import logging
import time

logger = logging.getLogger("[mainLogger]")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# log를 console에 출력
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# log를 파일에 출력
file_handler = logging.FileHandler("./logs/my.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("main intializing")
cam = Cam(True)
bot = Bot()
logger.info("bot True")

# 상태 변수 정의
head_lefted = False  
is_turning = 0  
searched = False  
walk_count = 3  
head_left = 0  
head_right = 0  
flag_pass = False  
hit = False  
hit_right = True 

while True:
    if bot.task == "ball":
        logger.info("ball is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        
        if is_ball:
            bot.head_center()
            if searched:
                # 더 정확한 회전 각도 조정
                if head_lefted:
                    bot.body_left_30()
                    time.sleep(0.2)  # 안정화 대기
                else:
                    bot.body_right_30()
                    time.sleep(0.2)  # 안정화 대기
                searched = False
            
            is_ball_center = cam.ball_is_center(bc)
            if not is_ball_center:
                # 미세 조정을 위한 반복 확인
                for _ in range(3):  # 최대 3번 시도
                    if cam.ball_left(bc):
                        bot.left_10()
                    else:
                        bot.right_10()
                    time.sleep(0.1)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    if cam.ball_is_center(bc):
                        break
            else:
                bot.task2walk()
        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
                
    elif bot.task == "walk":
        logger.info("walk is start")
        h, b, f = cam.read()
        h, b, f = cam.read()  # 두 번 읽어 안정적인 프레임 확보
        is_ball, bc = cam.detect_ball()
        
        if is_ball:
            is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
            if is_hitable_X == is_hitable_Y == True:
                time.sleep(0.2)  # 안정화 대기
                # 재확인
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                if is_ball:
                    is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
                    if is_hitable_X == is_hitable_Y == True:
                        bot.task2flag()
                    else:
                        continue
            else:
                logger.info(f"x,y = [{x}, {y}]")
                if not is_hitable_X:
                    bot.ready_x(x)
                if not is_hitable_Y:
                    bot.ready_y(y)
                time.sleep(0.2)
        else:
            bot.go()
            
    elif bot.task == "flag":
        logger.info("flag is start")
        time.sleep(1)  # 안정화 대기 시간
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()

        if is_flag:
            bot.head_center()
            if searched:
                # 회전 동작 최적화
                if not head_lefted:
                    for _ in range(3):  # 70도 회전을 3번으로 나눔
                        bot.left_70()
                        time.sleep(0.1)
                    bot.body_right_45()
                    time.sleep(0.3)
                    bot.body_right_45()
                    time.sleep(0.3)
                    for _ in range(5):
                        bot.left_70()
                        time.sleep(0.1)
                else:
                    for _ in range(3):
                        bot.right_70()
                        time.sleep(0.1)
                    bot.body_left_45()
                    time.sleep(0.3)
                    bot.body_left_45()
                    time.sleep(0.3)
                    for _ in range(5):
                        bot.right_70()
                        time.sleep(0.1)
                searched = False
                head_left = False

            is_flag_center = cam.flag_is_center(fc)
            if not is_flag_center:
                if not cam.flag_left(fc):
                    bot.body_right_20()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    if not cam.flag_is_center(coordinate):
                        for _ in range(3):
                            bot.left_20()
                            time.sleep(0.1)
                        bot.left_10()
                else:
                    bot.body_left_20()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    if not cam.flag_is_center(coordinate):
                        for _ in range(3):
                            bot.right_20()
                            time.sleep(0.1)
                        bot.right_10()
            else:
                time.sleep(0.3)  # 최종 안정화
                bot.task2ready()
        else:  # 깃발이 시야에 없을 때 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                # 머리 회전 각도를 단계적으로 증가
                if head_lefted:
                    bot.head_right_max()
                    time.sleep(0.3)  # 회전 후 안정화 대기
                    h, b, f = cam.read()  # 프레임 재획득
                    is_flag, fc = cam.detect_flag()  # 깃발 재탐지
                    if not is_flag:
                        bot.head_right_45()  # 중간 각도로 추가 확인
                else:
                    bot.head_left_max()
                    time.sleep(0.3)  # 회전 후 안정화 대기
                    h, b, f = cam.read()  # 프레임 재획득
                    is_flag, fc = cam.detect_flag()  # 깃발 재탐지
                    if not is_flag:
                        bot.head_left_45()  # 중간 각도로 추가 확인
                
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
                
                # 프레임 재획득 및 깃발 재탐지
                time.sleep(0.2)
                h, b, f = cam.read()
                is_flag, fc = cam.detect_flag()

    elif bot.task == "ready":
        logger.info("ready is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        
        if not is_ball:
            bot.task2ball()
            continue
            
        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
        # 공과 로봇 발 사이의 거리를 계산
        ball_distance = cam.calculate_ball_distance()  # 이 함수는 Camera 클래스에 구현되어 있어야 함
        
        if is_hitable_X and is_hitable_Y and ball_distance >= 11.0:  # 거리가 11cm 이상인지 확인
            if hit:
                time.sleep(0.3)
                bot.task2hit()
            else:
                if hit_right:
                    for _ in range(3):
                        bot.left_20()
                        time.sleep(0.1)
                    bot.body_right_45()
                    time.sleep(0.3)
                    bot.body_right_45()
                    time.sleep(0.3)
                    for _ in range(3):
                        bot.left_70()
                        time.sleep(0.1)
                    for _ in range(4):
                        bot.left_20()
                        time.sleep(0.1)
                else:
                    for _ in range(3):
                        bot.right_20()
                        time.sleep(0.1)
                    bot.body_left_45()
                    time.sleep(0.3)
                    bot.body_left_45()
                    time.sleep(0.3)
                    for _ in range(3):
                        bot.right_70()
                        time.sleep(0.1)
                    for _ in range(4):
                        bot.right_20()
                        time.sleep(0.1)
                hit = True
        else:
            if not is_hitable_X:
                bot.ready_x(x)
                time.sleep(0.1)
            if not is_hitable_Y:
                bot.ready_y(y)
                time.sleep(0.1)
            if ball_distance < 11.0:  # 거리가 11cm 미만이면 뒤로 이동
                bot.step_backward()
                time.sleep(0.2)


    elif bot.task == "hit":
        logger.info("hit is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        
        # 타격 전 마지막으로 거리 확인
        if is_ball:
            ball_distance = cam.calculate_ball_distance()
            if ball_distance < 11.0:  # 거리가 너무 가까우면 타격하지 않고 ready 상태로 돌아감
                bot.task2ready()
                continue
                
        is_flag, fc = cam.detect_flag()
        
        if is_flag:
            distance = cam.flag_distance(bot.head_angle())
            time.sleep(0.3)

            # 거리 기반 파워 조절
            if 0 <= distance <= 50:
                power = 8
            elif 50 < distance <= 100:
                power = 15
            elif 100 < distance <= 150:
                power = 20
            elif 150 < distance <= 200:
                power = 25
            else:
                power = 30

            bot.hit(power)
            time.sleep(0.5)
            bot.task2ball()
        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
