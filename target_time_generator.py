from datetime import datetime, timedelta
import random


def generate_target_times(start_time, end_time, interval, retry_count):
    
    print("start generate_target_times")
    
    if interval != 0:
        target_times = generate_interver(start_time, end_time, interval, retry_count)
    else:
        target_times = generate_random(start_time, end_time, interval, retry_count)
                
    return target_times



def generate_interver(start_time, end_time, interval, retry_count):
    target_times = []
    
    min_minutes = interval * retry_count if interval != 0 else retry_count
    difference = (end_time - start_time)
    
    next_time = start_time
    
    
    if difference < timedelta(minutes=min_minutes):
        raise ValueError("The difference between end time and start time must be at least "+ str(min_minutes) +" minutes.")

    for _ in range(retry_count):
        target_time = next_time

        if target_time >= end_time:
            print("The target time that exceeds the end time will be ignored. Please adjust the end time or interval.")
            return target_times
        else:
            target_times.append(target_time)
            next_time = target_time + timedelta(minutes=interval)
            
    return target_times
            
            
            
def generate_random(start_time, end_time, interval, retry_count):
    target_times = []
    
    min_minutes = interval * retry_count if interval != 0 else retry_count
    difference = (end_time - start_time)
    
    prev_time = start_time
    
    if difference < timedelta(minutes=min_minutes):
        raise ValueError("When using random for interval without specifying, end_time and start_time must have a minimum difference of retry_count + 1 minutes.")
    
    for iter_cnt in range(1, retry_count + 1):
        
        time_difference = (end_time - timedelta(minutes=retry_count + 1 - iter_cnt)) - prev_time
        minutes_difference = int(time_difference.total_seconds() / 60)
        
        random_minutes = random.randint(1, minutes_difference)
        
        target_time = prev_time + timedelta(minutes=random_minutes)
        
        if target_time >= end_time:
            print("The target time that exceeds the end time will be ignored. Please adjust the end time or interval.")
            return target_times
        else:
            target_times.append(target_time)
            prev_time = target_time
            
    return target_times