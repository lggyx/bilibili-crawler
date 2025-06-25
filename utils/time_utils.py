from datetime import datetime

def get_time_str():
    # 生成格式为 20240625_153045_123456 的时间字符串
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")



