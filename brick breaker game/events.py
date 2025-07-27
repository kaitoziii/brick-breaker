import random

def trigger_special_event():
    # Misalnya 1 dari 10 chance muncul power-up
    if random.randint(1, 10) == 1:
        return random.choice(["multi_ball", "big_paddle", "score_boost"])
    return None
