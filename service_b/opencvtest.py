import cv2
import numpy as np
import io
f=open('2.avi','rb')

def check_image(img_stream, cv2_img_flag=0):
    img_stream.seek(0)
    img_array = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    try:
        if type(cv2.imdecode(img_array, cv2_img_flag)).__name__ == 'NoneType':
            return False
        return True
    except:
        return False

def check_video(video_stream,cv2_video_flag=0):
    video_stream.seek(0)
    img_array = np.asarray(bytearray(video_stream.read()), dtype=np.uint8)
    try:
        print(cv2.imdecode(img_array,cv2_video_flag))
    except:
        raise Exception
        return False

