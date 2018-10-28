### Extract stereoscopic frame

Extract audio for both videos
'ffmpeg -i VIDEO_PATH AUDIO_PATH'

Find offset between two videos
'python audio_sync_helper.py --master_audio=MASTER_AUDIO_PATH --slave_audio=SLAVE_AUDIO_PATH --stop_at=TIME_LIMIT'

Extract N frames from video
'ffmpeg -ss HH:MM:SS.MMM -i VIDEO_PATH -vframes N IMAGE_NAME-%04d.jpg'

