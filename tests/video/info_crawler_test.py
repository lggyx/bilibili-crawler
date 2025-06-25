from src.crawler.video.info_crawler import *
from src.utils.storage_utils import write_file_to_raw
from src.utils.time_utils import get_time_str

# print(get_video_info_view(None,"BV117411r7R1"))
# print(get_video_info_view(85440373,""))

# print(get_video_info_detail(170001,"",1))
# print(get_video_info_detail(170001,"",1))
# print(get_video_info_detail(None,"BV17x411w7KC",1))

print(get_video_info_desc(39330059,""))
print(get_video_info_desc(None,"BV1Bt411z799"))
write_file_to_raw("获取视频简介"+get_time_str(),get_video_info_desc(39330059,""))