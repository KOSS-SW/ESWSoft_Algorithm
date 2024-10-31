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
        is_ball, bc = cam.detect_ball()  # 공의 위치도 확인

        if is_flag:
            bot.head_center()
            if searched:
                ball_distance = cam.calculate_ball_distance() if is_ball else float('inf')
                logger.info(f"Ball distance before rotation: {ball_distance}")
                
                # 공이 너무 가까이 있으면 먼저 뒤로 이동
                if ball_distance < 15.0:  # 회전을 위한 안전거리 15cm 설정
                    logger.info("Ball too close, stepping back")
                    bot.back()
                    time.sleep(0.2)
                    # 후진 후 거리 재확인
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    ball_distance = cam.calculate_ball_distance() if is_ball else float('inf')
                    
                    # 여전히 가깝다면 한 번 더 후진
                    if ball_distance < 15.0:
                        bot.back()
                        time.sleep(0.2)
                
                # 안전거리 확보 후 회전 시작
                if not head_lefted:  # 오른쪽으로 회전할 때
                    logger.info("Rotating right")
                    for _ in range(3):  # 70도 회전을 3번으로 나눔
                        bot.left_70()
                        # 각 회전마다 공과의 거리 확인
                        h, b, f = cam.read()
                        is_ball, bc = cam.detect_ball()
                        if is_ball and cam.calculate_ball_distance() < 15.0:
                            bot.back()
                            time.sleep(0.2)
                        time.sleep(0.1)
                    
                    bot.body_right_45()
                    time.sleep(0.3)
                    bot.body_right_45()
                    time.sleep(0.3)
                    
                    for _ in range(5):
                        bot.left_70()
                        # 각 회전마다 공과의 거리 확인
                        h, b, f = cam.read()
                        is_ball, bc = cam.detect_ball()
                        if is_ball and cam.calculate_ball_distance() < 15.0:
                            bot.back()
                            time.sleep(0.2)
                        time.sleep(0.1)
                else:  # 왼쪽으로 회전할 때
                    logger.info("Rotating left")
                    for _ in range(3):
                        bot.right_70()
                        # 각 회전마다 공과의 거리 확인
                        h, b, f = cam.read()
                        is_ball, bc = cam.detect_ball()
                        if is_ball and cam.calculate_ball_distance() < 15.0:
                            bot.back()
                            time.sleep(0.2)
                        time.sleep(0.1)
                    
                    bot.body_left_45()
                    time.sleep(0.3)
                    bot.body_left_45()
                    time.sleep(0.3)
                    
                    for _ in range(5):
                        bot.right_70()
                        # 각 회전마다 공과의 거리 확인
                        h, b, f = cam.read()
                        is_ball, bc = cam.detect_ball()
                        if is_ball and cam.calculate_ball_distance() < 15.0:
                            bot.back()
                            time.sleep(0.2)
                        time.sleep(0.1)
                
                searched = False
                head_left = False

            is_flag_center = cam.flag_is_center(fc)
            if not is_flag_center:
                if not cam.flag_left(fc):
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    if not cam.flag_is_center(coordinate):
                        bot.left_10()
                else:
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    if not cam.flag_is_center(coordinate):
                        bot.right_20()
            else:
                time.sleep(0.3)  # 최종 안정화
                bot.task2ready()
        else:  # 깃발이 시야에 없을 때 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_flag, fc = cam.detect_flag()
                    if not is_flag:
                        bot.head_right_45()
                else:
                    bot.head_left_max()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_flag, fc = cam.detect_flag()
                    if not is_flag:
                        bot.head_left_45()
                
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
                
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
            bot.back()  # 한 발자국 뒤로
            time.sleep(0.2)  # 안정화 대기

            # 뒤로 간 후 다시 공 확인
            h, b, f = cam.read()
            is_ball, bc = cam.detect_ball()

            if not is_ball:  # 여전히 안 보이면 한 번 더 뒤로
                logger.info("ball still not visible, stepping back again")
                bot.back()
                time.sleep(0.2)

                # 마지막으로 공 확인
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()

                if not is_ball:  # 그래도 안 보이면 ball 찾기 상태로
                    logger.info("cannot find ball, switching to ball finding mode")
                    bot.task2ball()
                    continue

        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)

        # 공과 로봇 발 사이의 거리를 계산
        ball_distance = cam.calculate_ball_distance()

        if (
            is_hitable_X and is_hitable_Y and ball_distance >= 11.0
        ):  # 거리가 11cm 이상인지 확인
            if hit:
                time.sleep(0.3)
                bot.task2hit()
            else:
                # 먼저 안전 거리 확보를 위해 뒤로 이동
                bot.back()  # 한 발자국 뒤로
                time.sleep(0.2)  # 안정화 대기

                # 안전 거리 확보 후 회전 시작
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
                bot.back()  # 한 걸음 후진
                time.sleep(0.2)  # 안정화 대기
    elif bot.task == "hit":
        logger.info("hit is start")
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()

        if is_flag:
            distance = cam.flag_distance(bot.head_angle())
            time.sleep(0.3)  # 안정화를 위한 대기

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

            bot.hit(power)  # 설정된 파워로 타격
            time.sleep(0.5)  # 타격 후 안정화 대기
            bot.task2ball()  # 다음 공 찾기로 전환
        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
