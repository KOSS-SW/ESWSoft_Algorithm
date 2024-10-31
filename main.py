from MODULES.Camera.camera import Cam
from MODULES.Camera import calculate
from MODULES.Motion.robot import Bot
import logging
import time

logger = logging.getLogger("[mainLogger]")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Console logging
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# File logging
file_handler = logging.FileHandler("./logs/my.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("main initializing")
cam = Cam(True)
bot = Bot()
logger.info("bot True")

# State variables
head_lefted = False
is_turning = 0
searched = False
scan_count = 0
head_left = 0
head_right = 0
flag_pass = False
hit = False
hit_right = True
full_scan_completed = False

def perform_360_scan():
    """Perform a full 360-degree scan for the ball"""
    for _ in range(12):  # 30도씩 12번 회전 = 360도
        bot.body_right_30()
        time.sleep(0.3)
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()
        if is_ball:
            return True, bc
    return False, None

def approach_ball(bc):
    """Move towards the ball while keeping it centered"""
    while True:
        h, b, f = cam.read()
        is_ball, new_bc = cam.detect_ball()
        if not is_ball:
            return False
            
        is_ball_center = cam.ball_is_center(new_bc)
        if not is_ball_center:
            if cam.ball_left(new_bc):
                bot.left_10()
            else:
                bot.right_10()
            time.sleep(0.2)
        else:
            bot.go()
            time.sleep(0.3)
            
        # Check if we're close enough
        is_hitable_X, is_hitable_Y, _, _ = cam.ball_hitable(new_bc)
        if is_hitable_X and is_hitable_Y:
            return True
    
    return False

while True:
    if bot.task == "ball":
        logger.info("ball is start")
        h, b, f = cam.read()
        is_ball, bc = cam.detect_ball()

        if is_ball:
            if searched:  # 공을 찾은 직후
                time.sleep(0.3)
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                
                if is_ball:
                    logger.info("Ball found - approaching")
                    bot.head_center()  # 머리 중앙으로
                    if approach_ball(bc):
                        bot.task2walk()
                    else:
                        searched = False
                
            else:  # 일반적인 ball 찾기 모드
                is_ball_center = cam.ball_is_center(bc)
                if not is_ball_center:
                    for _ in range(3):
                        if cam.ball_left(bc):
                            bot.left_10()
                        else:
                            bot.right_10()
                        time.sleep(0.2)
                        h, b, f = cam.read()
                        is_ball, bc = cam.detect_ball()
                        if cam.ball_is_center(bc):
                            break
                else:
                    bot.task2walk()
        else:
            if not full_scan_completed:
                logger.info("Starting full 360 scan")
                bot.head_up()  # 머리 90도 올리기
                is_ball, bc = perform_360_scan()
                if is_ball:
                    searched = True
                    full_scan_completed = True
                    continue
                
                # Try lower head angle scan
                bot.head_center()
                time.sleep(0.3)
                is_ball, bc = perform_360_scan()
                if is_ball:
                    searched = True
                    full_scan_completed = True
                    continue
                    
                full_scan_completed = True
            
            # Regular scanning motion if 360 scan failed
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                scan_count += 1
                if scan_count % 4 == 0:  # Every 4th scan, change head angle
                    if bot.head_angle() > 45:
                        bot.head_center()
                    else:
                        bot.head_up()
                
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
        is_ball, bc = cam.detect_ball()

        if is_ball:
            is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)
            
            # Double check the position
            time.sleep(0.2)
            h, b, f = cam.read()
            is_ball, bc = cam.detect_ball()
            
            if is_ball and is_hitable_X and is_hitable_Y:
                ball_distance = cam.calculate_ball_distance()
                if 25.0 <= ball_distance <= 35.0:  # Optimal hitting distance
                    bot.task2flag()
                else:
                    if ball_distance < 25.0:
                        bot.back()
                    else:
                        bot.go()
                    time.sleep(0.2)
            else:
                if not is_hitable_X:
                    bot.ready_x(x)
                if not is_hitable_Y:
                    bot.ready_y(y)
                time.sleep(0.2)
        else:
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

        if not is_ball:
            bot.task2ball()
            continue

        is_hitable_X, is_hitable_Y, x, y = cam.ball_hitable(bc)

        # 공과 로봇 발 사이의 거리를 계산
        ball_distance = cam.calculate_ball_distance()
        logger.info(f"발과 공 사이의 거리 : {ball_distance}")

        if (
            is_hitable_X and is_hitable_Y and ball_distance >= 25.0
        ):  # 거리가 11cm 이상인지 확인
            if hit:
                bot.back()
                time.sleep(0.3)
                bot.task2hit()
            else:
                # 회전하기 전에 고개 내려서 공과의 거리 확인
                bot.head_down()  # 고개를 아래로
                time.sleep(0.2)  # 안정화 대기

                # 거리 재확인
                h, b, f = cam.read()
                is_ball, bc = cam.detect_ball()
                if is_ball:
                    check_distance = cam.calculate_ball_distance()
                    if check_distance < 25.0:  # 너무 가까우면
                        bot.back()  # 뒤로 한 발
                        time.sleep(0.2)

                bot.head_center()  # 고개 다시 중앙으로
                time.sleep(0.2)

                # 이후 회전 시작
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
            if ball_distance < 25.0:  # 거리가 11cm 미만이면 뒤로 이동
                bot.back()  # 한 걸음 후진
                time.sleep(0.2)  # 안정화 대기

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
            bot.task2ball()
        else:
            if is_turning == 0 or abs(time.time() - is_turning) > 1:
                if head_lefted:
                    bot.head_right_max()
                else:
                    bot.head_left_max()
                head_lefted = not head_lefted
                is_turning = time.time()
