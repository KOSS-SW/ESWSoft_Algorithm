from MODULES.Camera.camera import Cam
from MODULES.Camera import calculate
from MODULES.Motion.robot import Bot

import logging
import time
import sys

startTime = time.time()

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
set90 = 0
par4 = False

logger.info("main intializing")
bot = Bot()
cam = Cam(True)
logger.info("bot True")

if __name__ == "__main__":
    print(sys.argv)
    if 'par4' in sys.argv:
        par4 = True
        print("par4 is True")
    if 'down' in sys.argv:
        # bot.head_down_65()
        bot.head_down_35()
        # time.sleep(.3)


while True:
    if bot.task == "ball":
        time.sleep(.3)
        logger.info("ball is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if is_ball:
            bot.head_center()
            if searched:
                # 더 정확한 회전 각도 조정
                if head_lefted:
                    bot.body_left_30()
                    # time.sleep(0.2)  # 안정화 대기
                else:
                    bot.body_right_30()
                    # time.sleep(0.2)  # 안정화 대기
                searched = False

            is_ball_center = cam.ball_is_center(bc)
            if not is_ball_center:
                # 미세 조정을 위한 반복 확인
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
                # time.sleep(0.1)
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                if not is_ball:
                    continue
                if cam.ball_is_center(bc):
                    bot.task2walk()
            else:
                bot.task2walk()
        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_middle()
                    time.sleep(0.2)
                    cam.read()
                    is_ball, bc = cam.detect_ball()
                    if not is_ball:
                        bot.head_right_max()
                else:
                    bot.head_left_middle()
                    time.sleep(0.2)
                    cam.read()
                    is_ball, bc = cam.detect_ball()
                    if not is_ball:
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
        else:
            bot.head_down_35()

    elif bot.task == "walk":
        logger.info("walk is start")
        h, b, f = cam.read()
        for _ in range(6):
            h, b, f = cam.read()  # 두 번 읽어 안정적인 프레임 확보
            is_ball, bc = cam.detect_ball()
            time.sleep(0.1)  # 안정화 대기
            # 재확인
            h, b, f = cam.read()
            is_ball, bc = cam.detect_ball()
            if is_ball:
                is_ball_center = cam.ball_is_center_h(bc)
                if is_ball_center:
                    if bot.hitting >= (2 if not par4 else 3):
                        bot.task2check()
                        break
                    else:
                        while True:
                            if cam.ball_is_center(bc):
                                break
                            else:
                                if cam.ball_left(bc):
                                    bot.left_5()
                                else:
                                    bot.right_5()
                            cam.read()
                            is_ball, bc = cam.detect_ball()
                        bot.task2flag()
                        break
            bot.go()
        if is_ball: continue
        bot.task2ball()

    elif bot.task == "flag":
        logger.info("flag is start")
        time.sleep(0.2)  # 안정화 대기 시간
        h, b, f = cam.read()
        is_flag, fc = cam.detect_flag(True, bot.hitting == 0)
        logger.debug(f"is_flag in flag: {is_flag}, {fc}")

        if is_flag:
            bot.head_center()
            time.sleep(1)
            logger.debug("turning 90")
            if searched:
                # 회전 동작 최적화
                if not head_lefted:
                    bot.body_right_90()
                searched = False
                head_left = False
            else:
                if (cam.flag_turnable(fc)) or bot.hitting < 1:
                    head_left = False
                    bot.body_right_90()
            bot.task2ready()
            continue
        else:  # 깃발이 시야에 없을 때 탐색
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                # 머리 회전 각도를 단계적으로 증가
                if head_lefted:
                    bot.head_right_middle()  # 중간 각도로 추가 확인
                    time.sleep(0.2)
                    cam.read()
                    is_flag, fc = cam.detect_flag()
                    if not is_flag:
                        bot.head_right_max()
                else:
                    bot.head_left_middle()  # 중간 각도로 추가 확인
                    time.sleep(0.2)
                    cam.read()
                    is_flag, fc = cam.detect_flag()
                    if not is_flag:
                        bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
                searched = True
                time.sleep(.5)

    elif bot.task == "ready":
        logger.info("Putting preparation started")
        if set90 in [1,3]:
            bot.head_down_75()
            ## 90도 맞추기 위해 고개 돌리면 깃발이 안보이는 문제 발생
            bot.head_left_max()
            time.sleep(1)
            h, b, f = cam.read()
            is_flag, fc = cam.detect_flag()
            ##깃발 90도 확인 및 재조정
            logger.info("set 90")
            while True:
                time.sleep(.07)
                cam.read()
                is_flag, fc = cam.detect_flag()
                if not is_flag:
                    bot.body_right_10()
                    bot.body_right_10()
                    continue
                if cam.flag_is_center(fc):
                    break
                if cam.flag_left(fc):
                    bot.body_left_5()
                else:
                    bot.body_right_5()
            logger.info("set 90 done")
            set90 += 1
            bot.head_down_35()
            time.sleep(1.5)
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
                    time.sleep(0.3)

                elif current_distance > TARGET_DISTANCE:
                    # 거리가 너무 멀면 앞으로 이동
                    logger.info(f"Distance too far, moving forward. Current: {current_distance}cm, Target: {TARGET_DISTANCE}cm")
                    steps_forward = int((current_distance - TARGET_DISTANCE) / 2)  # 2cm 단위로 전진
                    # for _ in range(steps_forward):
                    bot.go_little()
                    time.sleep(0.3)

            else:
                # X-Y 위치 미세 조정
                if (is_hitable_X):
                    # 퍼팅 준비를 위한 위치 조정
                    if set90 >= 4:
                        bot.head_center()
                        bot.task2hit()
                        set90 = 0
                        hit = False
                        continue
                    else:
                        set90 += 1
                else:
                    # X-Y 축 미세 조정
                    if not is_hitable_X:
                        bot.ready_x(x)
                        time.sleep(.1)

    elif bot.task == "hit":
        logger.info("hit is start")
        bot.hit(not checkIn, par4)
        head_lefted = False
        time.sleep(1)
        bot.head_down_35()
        cam.read()
        is_ball, bc = cam.detect_ball()
        if is_ball:
            bot.task2walk()
            continue

        if not checkIn:
            bot.head_center()
            bot.head_down_80()
            time.sleep(.5)
            bot.body_left_10()
            # bot.body_left_10()

            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            bot.left_70()
            if par4:
                for _ in range(3):
                    bot.left_70()
                    bot.left_70()
                    bot.left_70()
                    bot.left_70()
                    bot.left_70()
                    # bot.left_70()
                bot.body_left_10()
                bot.body_left_10()
            else:
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()

            time.sleep(1)  # 안정화 대기
        else:
            bot.head_center()
            bot.head_down_75()
            if par4 and bot.hitting == 2:
                bot.body_left_10()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.body_left_10()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                bot.left_70()
                # bot.body_left_45()
                # bot.body_left_10()
        

        while True:  # 무한 루프 시작
            h, b, f = cam.read()
            is_ball, bc = cam.detect_ball()  # 공 검출 시도
            if is_ball:  # 공이 검출되면
                if is_ball and not cam.ball_left(bc):  # 공이 검출되면
                    checkIn = True
                    bot.task2following()  # 한번 공을 친 후, following 테스크로 이동
                    break  # 루프 종료
            bot.body_left_10()  # 공이 검출되지 않으면 왼쪽으로 회전
        continue
    elif bot.task == "check":
        hc = cam.detect_holcup(True)
        is_ball, bc = cam.detect_ball()
        if hc and is_ball:
            if calculate.calculateDistance(bc, hc)[0] < 100:
                bot.end()
                logger.info("Goal")
                break

        bot.task2flag()

print((time.time() - startTime))