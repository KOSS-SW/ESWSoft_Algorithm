import numpy as np

def calculateDistance(ball_center, flag_center):
    global distance, midpoint
    if ball_center and flag_center:        
        # Calculate the distance
        distance = np.linalg.norm(np.array(ball_center) - np.array(flag_center))
        # Calculate the midpoint for displaying the distance
        midpoint = ((ball_center[0] + flag_center[0]) // 2, (ball_center[1] + flag_center[1]) // 2)
        return distance, midpoint
    else:
        return -1, 0
    
    