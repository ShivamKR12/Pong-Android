# config.py

DIFFICULTY_SETTINGS = {
    "EASY": {
        "ball_x": 2.0,       
        "ball_y": 2.0,       
        "ai_speed": 2.0,     
        "ai_tolerance": 25,  # Sloppy tracking    
        "speed_inc": 0.2,  # Slowly speeds up on paddle hits
        "max_speed": 6.0,
        "instant_drag": False
    },
    "NORMAL": {
        "ball_x": 3.0,       
        "ball_y": 3.0,       
        "ai_speed": 3.5,     
        "ai_tolerance": 12,  # Decent tracking    
        "speed_inc": 0.4,  # Moderately speeds up on paddle hits
        "max_speed": 9.0,
        "instant_drag": True
    },
    "HARD": {
        "ball_x": 4.5,       
        "ball_y": 4.5,       
        "ai_speed": 6.0,    
        "ai_tolerance": 4,   # Laser-sharp tracking   
        "speed_inc": 0.6,  # Quickly accelerates on paddle hits
        "max_speed": 12.0,   
        "instant_drag": True
    }
}

USER_SETTINGS = {
    "win_score": 5,
    "scale_factor": 0.5
}
