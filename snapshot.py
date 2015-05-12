#!/usr/bin/python

'''this is a simple snapshot module (including a standalone main'''

def snapshot(file_name="snap.jpg",cam_n = 0):
    """captures one image by using webcam (v4l) cam_n to given filename (file_name)"""
    import cv2
    cam = cv2.VideoCapture(cam_n)
    key = 0
    picture = cam.read()
    while key != ord(" "):
        ret, picture = cam.read()
        cv2.imshow("Hit [SPACE] to capture", picture)
        key = cv2.waitKey(2) & 0xff
    cv2.imwrite(file_name, picture)
    cv2.destroyWindow("Hit [SPACE] to capture")
    
def main(argv):
    """parses arguments and runs snapshoot function to capture to given filename"""
    import os
    import sys
    import argparse
    parser = argparse.ArgumentParser(description='Take a Picture')
    parser.add_argument('-c', '--cam', nargs='?', type=int, help='use cam Number N defaults to 0', default=0)
    parser.add_argument('NAME', nargs='?', help='Filename defaults to snap.jpg', default="snap.jpg")
    
    cmdline_args = parser.parse_args(sys.argv[1:]) #cut the program-name off the list 
    
    picture_file=cmdline_args.NAME
    
    snapshot(picture_file,cmdline_args.cam)

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))