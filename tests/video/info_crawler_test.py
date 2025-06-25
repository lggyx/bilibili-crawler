from config.logger import get_logger
from crawler.video.info_crawler import *
from utils.storage_utils import write_file_to_raw
from utils.time_utils import get_time_str
log=get_logger()
# log.info(get_video_info_view(None,"BV117411r7R1"))
# log.info(get_video_info_view(85440373,""))

# log.info(get_video_info_detail(170001,"",1))
# log.info(get_video_info_detail(170001,"",1))
# log.info(get_video_info_detail(None,"BV17x411w7KC",1))

log.info(get_video_info_desc(39330059,""))
log.info(get_video_info_desc(None,"BV1Bt411z799"))
write_file_to_raw("获取视频简介"+get_time_str(),get_video_info_desc(39330059,""))