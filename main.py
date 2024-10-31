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
                if cam.flag_left(fc):
                    # bot.body_right_20()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    if not cam.flag_is_center(coordinate):
                        # for _ in range(3):
                        #     bot.left_20()
                        #     time.sleep(0.1)
                        bot.left_10()
                else:
                    # bot.body_left_20()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    if not cam.flag_is_center(coordinate):
                        # for _ in range(3):
                        #     bot.right_20()
                        #     time.sleep(0.1)
                        bot.right_20()
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

       # 공이 안 보이면 뒤로 가면서 찾기 시도
       if not is_ball:
           logger.info("ball not visible, stepping back")
           bot.back()
           time.sleep(0.2)

           h, b, f = cam.read()
           is_ball, bc = cam.detect_ball()

           if not is_ball:
               logger.info("ball still not visible, stepping back again")
               bot.back()
               time.sleep(0.2)

               h, b, f = cam.read()
               is_ball, bc = cam.detect_ball()

               if not is_ball:
                   logger.info("cannot find ball, switching to ball finding mode")
                   bot.task2ball()
                   continue

       is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
       ball_distance = cam.calculate_ball_distance()

       if (
           is_hitable_X and is_hitable_Y and ball_distance >= 11.0
       ):
           if hit:
               # 머리를 아래로 내려서 공 확인
               bot.head_down()  # 머리를 아래로 내리는 메소드 필요
               time.sleep(0.3)  # 안정화 대기
               
               # 거리 재확인
               h, b, f = cam.read()
               is_ball, bc = cam.detect_ball()
               if is_ball:
                   final_distance = cam.calculate_ball_distance()
                   logger.info(f"Final distance before hit: {final_distance}cm")
                   
                   if final_distance < 11.0:  # 너무 가까우면
                       logger.info("Too close before hit, stepping back")
                       bot.back()
                       time.sleep(0.2)
                   elif final_distance > 13.0:  # 너무 멀면
                       logger.info("Too far before hit, stepping forward")
                       bot.go()
                       time.sleep(0.2)
               
               bot.head_center()  # 머리 다시 중앙으로
               time.sleep(0.3)
               bot.task2hit()
           else:
               # 회전 전 안전거리 확보
               safe_distance = 15.0  # 회전을 위한 안전거리
               
               # 안전거리보다 가까우면 충분한 거리까지 후진
               while ball_distance < safe_distance:
                   logger.info(f"Ball too close ({ball_distance}cm), backing up")
                   bot.back()
                   time.sleep(0.2)
                   
                   # 후진 후 거리 재확인
                   h, b, f = cam.read()
                   is_ball, bc = cam.detect_ball()
                   if is_ball:
                       ball_distance = cam.calculate_ball_distance()
                   else:
                       break  # 공이 안 보이면 충분히 멀어진 것으로 간주
               
               time.sleep(0.3)  # 안정화 대기
               
               # 안전거리 확보 후 회전 시작
               if hit_right:
                   # 회전을 더 작은 단위로 나누고 각 회전마다 거리 체크
                   for _ in range(3):
                       bot.left_20()
                       time.sleep(0.1)
                       # 회전 중 거리 체크
                       h, b, f = cam.read()
                       is_ball, bc = cam.detect_ball()
                       if is_ball:
                           current_distance = cam.calculate_ball_distance()
                           if current_distance < safe_distance:
                               bot.back()
                               time.sleep(0.2)
                   
                   bot.body_right_45()
                   time.sleep(0.3)
                   # 거리 재확인
                   h, b, f = cam.read()
                   is_ball, bc = cam.detect_ball()
                   if is_ball and cam.calculate_ball_distance() < safe_distance:
                       bot.back()
                       time.sleep(0.2)
                   
                   bot.body_right_45()
                   time.sleep(0.3)
                   
                   for _ in range(3):
                       bot.left_70()
                       time.sleep(0.1)
                       # 회전 중 거리 체크
                       h, b, f = cam.read()
                       is_ball, bc = cam.detect_ball()
                       if is_ball and cam.calculate_ball_distance() < safe_distance:
                           bot.back()
                           time.sleep(0.2)
                   
                   for _ in range(4):
                       bot.left_20()
                       time.sleep(0.1)
                       # 회전 중 거리 체크
                       h, b, f = cam.read()
                       is_ball, bc = cam.detect_ball()
                       if is_ball and cam.calculate_ball_distance() < safe_distance:
                           bot.back()
                           time.sleep(0.2)
               else:
                   # 왼쪽 회전도 동일한 패턴으로 수정
                   for _ in range(3):
                       bot.right_20()
                       time.sleep(0.1)
                       h, b, f = cam.read()
                       is_ball, bc = cam.detect_ball()
                       if is_ball and cam.calculate_ball_distance() < safe_distance:
                           bot.back()
                           time.sleep(0.2)
                   
                   bot.body_left_45()
                   time.sleep(0.3)
                   h, b, f = cam.read()
                   is_ball, bc = cam.detect_ball()
                   if is_ball and cam.calculate_ball_distance() < safe_distance:
                       bot.back()
                       time.sleep(0.2)
                   
                   bot.body_left_45()
                   time.sleep(0.3)
                   
                   for _ in range(3):
                       bot.right_70()
                       time.sleep(0.1)
                       h, b, f = cam.read()
                       is_ball, bc = cam.detect_ball()
                       if is_ball and cam.calculate_ball_distance() < safe_distance:
                           bot.back()
                           time.sleep(0.2)
                   
                   for _ in range(4):
                       bot.right_20()
                       time.sleep(0.1)
                       h, b, f = cam.read()
                       is_ball, bc = cam.detect_ball()
                       if is_ball and cam.calculate_ball_distance() < safe_distance:
                           bot.back()
                           time.sleep(0.2)
                           
               hit = True
       else:
           if not is_hitable_X:
               bot.ready_x(x)
               time.sleep(0.1)
           if not is_hitable_Y:
               bot.ready_y(y)
               time.sleep(0.1)
           if ball_distance < 11.0:
               bot.back()
               time.sleep(0.2)


    elif bot.task == "hit":
        logger.info("hit is start")
        h, b, f = cam.read()
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