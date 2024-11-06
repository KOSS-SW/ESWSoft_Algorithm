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
        center_ball = cam.ball_is_center(bc)
        if center_ball:
            logger.info("following task 볼 탐지 성공")
            for i in range(3):
                bot.go()
        else:
            if cam.ball_left(bc):
                bot.left_10()
            else:
                bot.right_10()

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
        logger.info("flag is start")
        time.sleep(1)  # 안정화 대기 시간
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag()

        if is_flag:
            bot.head_center()
            if searched:
                # 회전 동작 최적화
                if not head_lefted:
                    for _ in range(2):  # 70도 회전을 3번으로 나눔
                        bot.left_70()
                        time.sleep(0.1)
                    bot.body_right_90()
                    time.sleep(0.3)
                    for _ in range(5):
                        bot.left_70()
                        time.sleep(0.1)
                else:
                    for _ in range(2):
                        bot.right_70()
                        logger.info(f"테스트 돌기 10도 작은 회전 ㅋㅋTV")
                        bot.body_right_10()
                        time.sleep(0.1)
                    bot.body_left_90()
                    time.sleep(0.3)
                    for _ in range(5):
                        bot.right_70()
                        time.sleep(0.1)
                searched = False
                head_left = False

            is_flag_center = cam.flag_is_center(fc)
            if not is_flag_center:
                if not cam.flag_left(fc):
                    bot.body_right_10()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    # if not cam.flag_is_center(coordinate):
                    #     # for _ in range(3):
                    #     #     bot.left_20()
                    #     #     time.sleep(0.1)
                    #     bot.left_5()
                else:
                    bot.body_left_10()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    # if not cam.flag_is_center(coordinate):
                    #     # for _ in range(3):
                    #     #     bot.right_20()
                    #     #     time.sleep(0.1)
                    #     bot.right_20()
            else:
                time.sleep(0.3)  # 최종 안정화
                bot.task2ready()
        else:  # 깃발이 시야에 없을 때 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                # 머리 회전 각도를 단계적으로 증가
                if head_lefted:
                    # bot.head_right_max()
                    # time.sleep(0.3)  # 회전 후 안정화 대기
                    h, b, f = cam.read()  # 프레임 재획득
                    is_flag, fc = cam.detect_flag()  # 깃발 재탐지
                    # if not is_flag:
                    bot.head_right_middle()  # 중간 각도로 추가 확인
                else:
                    # bot.head_left_max()
                    # time.sleep(0.3)  # 회전 후 안정화 대기
                    h, b, f = cam.read()  # 프레임 재획득
                    is_flag, fc = cam.detect_flag()  # 깃발 재탐지
                    # if not is_flag:
                    bot.head_left_middle()  # 중간 각도로 추가 확인
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True

                # 프레임 재획득 및 깃발 재탐지
                time.sleep(0.2)
                h, b, f = cam.read()
                is_flag, fc = cam.detect_flag()

    elif bot.task == "ready":
        logger.info("Putting preparation started")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        is_flag, fc = cam.detect_flag()  # 깃발 감지 추가

        if not is_ball:
            bot.task2ball()
            continue

        if not is_flag:
            bot.task2flag()
            continue

        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
        
        # 최적의 퍼팅 거리 설정 (센티미터 단위)
        TARGET_DISTANCE = 21   # 목표 거리
        TOLERANCE = 2         # 허용 오차 범위
        MIN_DISTANCE = TARGET_DISTANCE - TOLERANCE  # 최소 허용 거리 (19cm)
        MAX_DISTANCE = TARGET_DISTANCE + TOLERANCE  # 최대 허용 거리 (23cm)
        ALIGNMENT_TOLERANCE = 5  # 수평 정렬 허용 오차 (픽셀)

        # 공과의 거리 확인을 위해 고개를 아래로
        bot.head_down_35()
        time.sleep(0.3)

        # 거리 측정 및 위치 조정
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        is_flag, fc = cam.detect_flag()
        
        if is_ball and is_flag:
            current_distance = cam.calculate_ball_distance()
            logger.info(f"Current distance from ball: {current_distance}cm")

            # 거리 조정
            if abs(current_distance - TARGET_DISTANCE) > TOLERANCE:
                if current_distance < TARGET_DISTANCE:
                    logger.info(f"Distance too short, moving backward. Current: {current_distance}cm, Target: {TARGET_DISTANCE}cm")
                    steps_back = int((TARGET_DISTANCE - current_distance) / 2)
                    for _ in range(steps_back):
                        bot.step_backward()
                        time.sleep(0.2)
                
                elif current_distance > TARGET_DISTANCE:
                    logger.info(f"Distance too far, moving forward. Current: {current_distance}cm, Target: {TARGET_DISTANCE}cm")
                    steps_forward = int((current_distance - TARGET_DISTANCE) / 2)
                    for _ in range(steps_forward):
                        bot.go_little()
                        time.sleep(0.2)

        # X-Y 위치 미세 조정
        if (is_hitable_X and is_hitable_Y):
            if hit:
                time.sleep(0.3)
                bot.task2hit()
            else:
                # 퍼팅 준비를 위한 위치 조정
                bot.head_center()
                time.sleep(0.3)

                if hit_right:
                    # 수평 정렬 체크 및 조정
                    bot.head_down_35()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    is_flag, fc = cam.detect_flag()
                    
                    if is_ball and is_flag:
                        # 공과 깃발의 Y좌표 차이 계산 (수평 정렬)
                        y_diff = bc[1] - fc[1]  # Y좌표 차이
                        logger.info(f"Horizontal alignment difference: {y_diff} pixels")
                        
                        # 수평 정렬 조정
                        while abs(y_diff) > ALIGNMENT_TOLERANCE:
                            if y_diff > 0:  # 공이 깃발보다 아래에 있음
                                bot.left_5()
                                time.sleep(0.2)
                            else:  # 공이 깃발보다 위에 있음
                                bot.right_5()
                                time.sleep(0.2)
                            
                            # 위치 재확인
                            h, b, f = cam.read()
                            is_ball, bc = cam.detect_ball()
                            is_flag, fc = cam.detect_flag()
                            if is_ball and is_flag:
                                y_diff = bc[1] - fc[1]
                                logger.info(f"Updated alignment difference: {y_diff} pixels")
                            else:
                                break

                    # 오른쪽 퍼팅을 위한 위치 조정
                    for _ in range(5):
                        bot.left_20()
                        time.sleep(0.2)
                    bot.body_right_90()
                    time.sleep(0.4)
                    for _ in range(3):
                        bot.left_70()
                        time.sleep(0.2)
                    
                    # 최종 수평 정렬 확인
                    bot.head_center()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    is_flag, fc = cam.detect_flag()
                    if is_ball and is_flag:
                        y_diff = bc[1] - fc[1]
                        if abs(y_diff) > ALIGNMENT_TOLERANCE:
                            logger.info("Final alignment adjustment needed")
                            if y_diff > 0:
                                bot.left_5()
                            else:
                                bot.right_5()
                            time.sleep(0.2)

                else:
                    # 수평 정렬 체크 및 조정 (왼쪽 퍼팅)
                    bot.head_down_35()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    is_flag, fc = cam.detect_flag()
                    
                    if is_ball and is_flag:
                        y_diff = bc[1] - fc[1]
                        logger.info(f"Horizontal alignment difference: {y_diff} pixels")
                        
                        while abs(y_diff) > ALIGNMENT_TOLERANCE:
                            if y_diff > 0:  # 공이 깃발보다 아래에 있음
                                bot.left_5()
                                time.sleep(0.2)
                            else:  # 공이 깃발보다 위에 있음
                                bot.right_5()
                                time.sleep(0.2)
                            
                            h, b, f = cam.read()
                            is_ball, bc = cam.detect_ball()
                            is_flag, fc = cam.detect_flag()
                            if is_ball and is_flag:
                                y_diff = bc[1] - fc[1]
                                logger.info(f"Updated alignment difference: {y_diff} pixels")
                            else:
                                break

                    # 왼쪽 퍼팅을 위한 위치 조정
                    for _ in range(5):
                        bot.right_20()
                        time.sleep(0.2)
                    bot.body_left_90()
                    time.sleep(0.4)
                    for _ in range(3):
                        bot.right_70()
                        time.sleep(0.2)
                    
                    # 최종 수평 정렬 확인
                    bot.head_center()
                    time.sleep(0.3)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    is_flag, fc = cam.detect_flag()
                    if is_ball and is_flag:
                        y_diff = bc[1] - fc[1]
                        if abs(y_diff) > ALIGNMENT_TOLERANCE:
                            logger.info("Final alignment adjustment needed")
                            if y_diff > 0:
                                bot.left_5()
                            else:
                                bot.right_5()
                            time.sleep(0.2)
                        
                        # 최종 위치 확인
                        bot.head_down_35()
                        time.sleep(0.3)
                        h, b, f = cam.read()
                        is_ball, bc = cam.detect_ball()
                        if is_ball:
                            hit = True
                            #     logger.info(f"Ready to hit. Final distance: {final_distance}cm")
                            # else:
                            #     logger.info(f"Distance adjustment needed. Current distance: {final_distance}cm")
                    else:
                        # X-Y 축 미세 조정
                        if not is_hitable_X:
                            bot.ready_x(x)
                            time.sleep(0.2)
                        # if not is_hitable_Y:
                        #     bot.ready_y(x)
                        #     time.sleep(0.2)

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

                if is_ball:  # 공이 검출되면
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
