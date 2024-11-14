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

# only in par4
is_par4_sec = False

while True:
    if bot.task == "ball":
        if checkIn:
            bot.head_up()
        time.sleep(1)
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
                for _ in range(4):  # 최대 3번 시도
                    if cam.ball_left(bc):
                        if checkIn:
                            bot.body_left_10()
                        else:
                            bot.left_10()
                    else:
                        if checkIn:
                            bot.body_right_10()
                        else:
                            bot.right_10()
                    time.sleep(0.1)
                    h, b, f = cam.read()
                    is_ball, bc = cam.detect_ball()
                    if not is_ball:
                        break
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
        for _ in range(3):
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
                break
            else:
                bot.go()
        if is_ball: continue
        bot.task2ball()

    elif bot.task == "flag":
        logger.info("flag is start")
        time.sleep(0.2)  # 안정화 대기 시간
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
                    bot.body_right_90()
                    time.sleep(0.3)
                    for _ in range(5):
                        bot.left_70()
                        time.sleep(0.1)
                else:
                    for _ in range(3):
                        bot.right_70()
                        logger.info(f"ROBOT 돌기 (10도 작은 회전)")
                        bot.body_right_10()
                        time.sleep(0.1)
                    bot.body_left_90()
                    time.sleep(0.3)
                    for _ in range(5):
                        bot.right_70()
                        time.sleep(0.1)
                searched = False
                head_left = False
            time.sleep(1)

            is_flag_center = cam.flag_is_center(fc)
            if not is_flag_center:
                if not cam.flag_left(fc):
                    bot.body_right_10()
                    if checkIn: bot.right_10()
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
                    if checkIn: bot.left_5()
                    time.sleep(0.2)
                    h, b, f = cam.read()
                    bool_result, coordinate = cam.detect_flag()
                    # if not cam.flag_is_center(coordinate):
                    #     # for _ in range(3):
                    #     #     bot.right_20()
                    #     #     time.sleep(0.1)
                    #     bot.right_20()
            else:
                time.sleep(0.2)  # 최종 안정화
                bot.task2ready()
        else:  # 깃발이 시야에 없을 때 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                # 머리 회전 각도를 단계적으로 증가
                if head_lefted:
                    # bot.head_right_max()
                    # time.sleep(0.3)  # 회전 후 안정화 대기
                    bot.head_right_middle()  # 중간 각도로 추가 확인
                    time.sleep(.2)
                    h, b, f = cam.read()  # 프레임 재획득
                    is_flag, fc = cam.detect_flag()  # 깃발 재탐지
                    # if not is_flag:
                    if not is_flag:
                        bot.head_right_max()
                        time.sleep(0.1)
                else:
                    # bot.head_left_max()
                    # time.sleep(0.3)  # 회전 후 안정화 대기
                    bot.head_left_middle()  # 중간 각도로 추가 확인
                    time.sleep(.2)
                    h, b, f = cam.read()  # 프레임 재획득
                    is_flag, fc = cam.detect_flag()  # 깃발 재탐지
                    # if not is_flag:
                    if not is_flag:
                        bot.head_left_max()
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

        if not is_ball:
            bot.task2ball()
            continue

        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)

        # 최적의 퍼팅 거리 설정 (센티미터 단위)
        TARGET_DISTANCE = 25   # 목표 거리
        TOLERANCE = 3        # 허용 오차 범위
        MIN_DISTANCE = TARGET_DISTANCE - TOLERANCE  # 최소 허용 거리 (19cm)
        MAX_DISTANCE = TARGET_DISTANCE + TOLERANCE  # 최대 허용 거리 (23cm)

        # 공과의 거리 확인을 위해 고개를 아래로
        bot.head_down_35()
        time.sleep(0.3)

        # 거리 측정 및 위치 조정
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if is_ball:
            current_distance = cam.calculate_ball_distance()
            logger.info(f"Current distance from ball: {current_distance}cm")

            # 거리 조정
            if abs(current_distance - TARGET_DISTANCE) > TOLERANCE:
                if current_distance < TARGET_DISTANCE:
                    # 거리가 부족하면 뒤로 이동
                    logger.info(f"Distance too short, moving backward. Current: {current_distance}cm, Target: {TARGET_DISTANCE}cm")
                    steps_back = int((TARGET_DISTANCE - current_distance) / 2)  # 2cm 단위로 후진
                    # for _ in range(steps_back):
                    bot.step_backward()
                    time.sleep(0.2)

                elif current_distance > TARGET_DISTANCE:
                    # 거리가 너무 멀면 앞으로 이동
                    logger.info(f"Distance too far, moving forward. Current: {current_distance}cm, Target: {TARGET_DISTANCE}cm")
                    steps_forward = int((current_distance - TARGET_DISTANCE) / 2)  # 2cm 단위로 전진
                    # for _ in range(steps_forward):
                    bot.go_little()
                    time.sleep(0.2)

            else:
                # X-Y 위치 미세 조정
                if (is_hitable_X):
                    if hit:
                        time.sleep(0.3)
                        bot.task2hit()
                        hit = False
                    else:
                        # 퍼팅 준비를 위한 위치 조정
                        bot.head_center()
                        # time.sleep(0.3)

                        if hit_right:
                            # 오른쪽 퍼팅을 위한 위치 조정
                            for _ in range(5):
                                bot.left_20()
                                time.sleep(0.2)
                            bot.body_right_90()
                            # bot.body_right_30()
                            time.sleep(0.4)
                            for _ in range(3):
                                bot.left_70()
                                time.sleep(0.2)
                        else:
                            # 왼쪽 퍼팅을 위한 위치 조정
                            for _ in range(5):
                                bot.right_20()
                                time.sleep(0.2)
                            bot.body_left_90()
                            # bot.body_left_30()
                            time.sleep(0.4)
                            for _ in range(3):
                                bot.right_70()
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
        # distance = cam.flag_distance(bot.head_angle())
        # time.sleep(0.3)
        # 거리 기반 파워 조절
        # if 0 <= distance <= 50:
        #     power = 8
        # elif 50 < distance <= 100:
        #     power = 15
        # elif 100 < distance <= 150:
        #     power = 20
        # elif 150 < distance <= 200:
        #     power = 25
        # else:
        #     power = 30


        bot.hit(not checkIn, is_par4_sec)
        time.sleep(1)
        if not checkIn:
            bot.head_up()
            time.sleep(1)
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            time.sleep(1)  # 안정화 대기
        else:
            bot.head_center()
            bot.head_up()
        while True:  # 무한 루프 시작
            h, b, f = cam.read()
            h, b, f = cam.read()
            h, b, f = cam.read()
            is_ball, bc = cam.detect_ball()  # 공 검출 시도
            if is_ball:  # 공이 검출되면
                if is_ball and not cam.ball_left(bc):  # 공이 검출되면
                    checkIn = True
                    bot.task2following()  # 한번 공을 친 후, following 테스크로 이동
                    if is_par4_sec:
                        break
                    is_par4_sec = True
                    break  # 루프 종료
            bot.body_left_20()  # 공이 검출되지 않으면 왼쪽으로 회전

        # else:
        #     if is_turning == 0 or abs(time.time() - is_turning) > 1:
        #         if head_lefted:
        #             bot.head_right_max()
        #         else:
        #             bot.head_left_max()
        #         head_lefted = not head_lefted
                # is_turning = time.time()

    elif bot.task == "check":
        hc = cam.detect_holcup()
        is_ball, bc = cam.detect_ball()
        if hc and is_ball:
            if calculate.calculateDistance(bc, hc)[0] < 100:
                bot.end()
                logger.info("Gool")
                break

        bot.task2flag()