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
checkIn = False

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
                    if not is_ball:
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

    elif bot.task == "following":
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        logger.info("follow is start")
        if is_ball:
            bot.task2ball()
            # center_ball = cam.ball_is_center(bc)
            # if center_ball:
            #     logger.info("following task 볼 탐지 성공")
            #     for i in range(3):
            #         bot.go()
            # else:
            #     if cam.ball_left(bc):
            #         bot.left_10()
            #     else:
            #         bot.right_10()
        else:
            bot.left_10()

    elif bot.task == "walk":
        logger.info("walk is start")
        h, b, f = cam.read()
        h, b, f = cam.read()  # 두 번 읽어 안정적인 프레임 확보
        is_ball, bc = cam.detect_ball()
        time.sleep(0.2)  # 안정화 대기
        # 재확인
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        if is_ball:
            if checkIn:
                bot.task2check()
            else:
                bot.task2flag()
        else:
            bot.go()

    elif bot.task == "flag":
        logger.info("Flag detection and alignment started")
        time.sleep(0.3)  # 안정화 대기 시간 조정
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()

        if is_flag:
            bot.head_center()
            time.sleep(0.2)
            
            if searched:
                # 깃발 발견 후 회전 동작 최적화
                if not head_lefted:
                    # 왼쪽에서 발견했을 때의 회전
                    logger.info("Rotating from left side detection")
                    for _ in range(2):
                        bot.left_70()
                        time.sleep(0.15)  # 회전 안정화 시간 증가
                    bot.body_right_90()
                    time.sleep(0.4)  # 90도 회전 후 안정화 시간 증가
                    for _ in range(5):
                        bot.left_70()
                        time.sleep(0.15)
                else:
                    # 오른쪽에서 발견했을 때의 회전
                    logger.info("Rotating from right side detection")
                    for _ in range(2):
                        bot.right_70()
                        time.sleep(0.15)
                    bot.body_left_90()
                    time.sleep(0.4)
                    for _ in range(5):
                        bot.right_70()
                        time.sleep(0.15)
                
                searched = False
                head_left = False
                time.sleep(0.3)  # 회전 완료 후 안정화

            # 깃발 중앙 정렬 개선
            is_flag_center = cam.flag_is_center(fc)
            alignment_attempts = 0  # 정렬 시도 횟수 제한
            
            while not is_flag_center and alignment_attempts < 5:
                h, b, f = cam.read()
                is_flag, fc = cam.detect_flag()
                
                if not is_flag:
                    break
                    
                is_flag_center = cam.flag_is_center(fc)
                if not is_flag_center:
                    if not cam.flag_left(fc):
                        logger.info("Adjusting right")
                        bot.body_right_10()
                    else:
                        logger.info("Adjusting left")
                        bot.body_left_10()
                    time.sleep(0.2)
                    
                alignment_attempts += 1
                
            if is_flag_center or alignment_attempts >= 5:
                time.sleep(0.4)  # 최종 안정화
                logger.info("Flag centered, transitioning to ready state")
                bot.task2ready()
                
        else:  # 깃발 탐색 로직 개선
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                logger.info("Searching for flag")
                if head_lefted:
                    bot.head_right_middle()
                    time.sleep(0.3)
                else:
                    bot.head_left_middle()
                    time.sleep(0.3)
                    
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
                
                time.sleep(0.3)
                h, b, f = cam.read()
                is_flag, fc = cam.detect_flag()

    elif bot.task == "ready":
        logger.info("Putting preparation started")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        is_flag, fc = cam.detect_flag()

        if not is_ball:
            logger.info("Ball not found, switching to ball detection")
            bot.task2ball()
            continue

        if not is_flag:
            logger.info("Flag lost during preparation, returning to flag detection")
            bot.task2flag()
            continue

        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
        
        # 퍼팅 준비 상수
        TARGET_DISTANCE = 21
        TOLERANCE = 2
        MIN_DISTANCE = TARGET_DISTANCE - TOLERANCE
        MAX_DISTANCE = TARGET_DISTANCE + TOLERANCE
        ALIGNMENT_TOLERANCE = 5

        # 거리 측정 및 조정
        bot.head_down_35()
        time.sleep(0.3)
        
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        is_flag, fc = cam.detect_flag()
        
        if is_ball and is_flag:
            current_distance = cam.calculate_ball_distance()
            logger.info(f"Current distance from ball: {current_distance}cm")

            # 거리 미세 조정
            distance_adjustment_attempts = 0
            while abs(current_distance - TARGET_DISTANCE) > TOLERANCE and distance_adjustment_attempts < 3:
                if current_distance < TARGET_DISTANCE:
                    steps = max(1, int((TARGET_DISTANCE - current_distance) / 2))
                    logger.info(f"Moving backward {steps} steps")
                    for _ in range(steps):
                        bot.step_backward()
                        time.sleep(0.2)
                else:
                    steps = max(1, int((current_distance - TARGET_DISTANCE) / 2))
                    logger.info(f"Moving forward {steps} steps")
                    for _ in range(steps):
                        bot.go_little()
                        time.sleep(0.2)
                        
                time.sleep(0.3)
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                if is_ball:
                    current_distance = cam.calculate_ball_distance()
                    logger.info(f"Updated distance: {current_distance}cm")
                distance_adjustment_attempts += 1

        # 퍼팅 위치 정렬
        if (is_hitable_X and is_hitable_Y):
            if hit:
                time.sleep(0.3)
                bot.task2hit()
            else:
                # 수평 정렬 전 초기 위치 확보
                bot.head_center()
                time.sleep(0.3)

                # 퍼팅 방향에 따른 정렬
                alignment_direction = "right" if hit_right else "left"
                logger.info(f"Preparing for {alignment_direction} putting")

                # 수평 정렬 수행
                alignment_success = False
                alignment_attempts = 0
                
                while not alignment_success and alignment_attempts < 3:
                    bot.head_down_35()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    is_flag, fc = cam.detect_flag()
                    
                    if is_ball and is_flag:
                        y_diff = bc[1] - fc[1]
                        logger.info(f"Alignment difference: {y_diff} pixels")
                        
                        if abs(y_diff) <= ALIGNMENT_TOLERANCE:
                            alignment_success = True
                            break
                            
                        adjustment_steps = 0
                        while abs(y_diff) > ALIGNMENT_TOLERANCE and adjustment_steps < 5:
                            if y_diff > 0:
                                bot.left_5()
                            else:
                                bot.right_5()
                            time.sleep(0.2)
                            
                            h, b, f = cam.read()
                            is_ball, bc = cam.detect_ball()
                            is_flag, fc = cam.detect_flag()
                            if is_ball and is_flag:
                                y_diff = bc[1] - fc[1]
                                logger.info(f"Updated alignment: {y_diff} pixels")
                            adjustment_steps += 1
                    
                    alignment_attempts += 1

                # 90도 회전 및 최종 위치 조정
                if hit_right:
                    logger.info("Executing right putting position")
                    for _ in range(5):
                        bot.left_20()
                        time.sleep(0.2)
                    bot.body_right_90()
                    time.sleep(0.4)
                    for _ in range(3):
                        bot.left_70()
                        time.sleep(0.2)
                else:
                    logger.info("Executing left putting position")
                    for _ in range(5):
                        bot.right_20()
                        time.sleep(0.2)
                    bot.body_left_90()
                    time.sleep(0.4)
                    for _ in range(3):
                        bot.right_70()
                        time.sleep(0.2)

                # 최종 위치 확인 및 미세 조정
                bot.head_down_35()
                time.sleep(0.3)
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                
                if is_ball:
                    final_distance = cam.calculate_ball_distance()
                    if MIN_DISTANCE <= final_distance <= MAX_DISTANCE:
                        logger.info(f"Final position achieved. Distance: {final_distance}cm")
                        hit = True
                    else:
                        logger.info(f"Final position needs adjustment. Distance: {final_distance}cm")
                
                else:
                    # X-Y 축 미세 조정
                    if not is_hitable_X:
                        bot.ready_x(x)
                        time.sleep(0.2)
                    if not is_hitable_Y:
                        bot.ready_y(y)
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
            time.sleep(1)
 
            bot.head_up()
            time.sleep(1)

            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            time.sleep(1)  # 안정화 대기

            while True:  # 무한 루프 시작
                h, b, f = cam.read()
                h, b, f = cam.read()
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()  # 공 검출 시도

                if is_ball and not cam.ball_left(bc):  # 공이 검출되면
                    checkIn = True
                    bot.task2following()  # 한번 공을 친 후, following 테스크로 이동
                    break  # 루프 종료

                bot.body_left_10()  # 공이 검출되지 않으면 왼쪽으로 회전

        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()

    elif bot.task == "check":
        hc = cam.detect_holcup()
        is_ball, bc = cam.detect_ball()
        if hc and is_ball:
            if calculate.calculateDistance(bc, hc) < 100:
                bot.end()
                break

        bot.task2flag()
