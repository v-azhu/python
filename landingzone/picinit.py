# -*- coding: utf-8 -*-
import os
import shutil
import time
from PIL import Image
from PIL.ExifTags import TAGS
# 照片自动按时间归类小程序，对于给定的目录，扫描其下的所有图片，取它的相机时间或修改时间，然后把它放在输出目录的图片时间戳YYYYMM所在的目录。
# az 2018-11-27
def ispic(f=None):
    pictype=['.jpg','.jpeg','.png','.bmp','.gif']
    if os.path.splitext(f)[-1].lower() in pictype:
        return True
    else:
        return False
def getImgTag(f=None,t='DateTime'):
    im = Image.open(f)
    info = im._getexif()
    dt = time.strftime('%Y:%m:%d %H:%M:%S',time.localtime(os.path.getmtime(f)))
    if info:
        for tag,value in info.items(): 
            key = TAGS.get(tag,tag)
            #print (key,value)
            if key == t: 
                dt = value
                break
    return dt
def mkdirifnotexists(d=None):
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
        return True
    else:
        return False
def getfiles(d=None): 
    for i in os.walk(d):
        for j in i[2]:
            if ispic(os.path.join(i[0],j)):
                yield os.path.join(i[0],j)
def handler():
    rtdir="d:/1/"
    outdir="d:/1/"
    for f in getfiles(rtdir):
        subdir = getImgTag(f)[:7].replace(':','')
        mkdirifnotexists(outdir+subdir)
        try:
            shutil.move(f, outdir+subdir)
        except:
            pass
if __name__ == "__main__":
    #print ( getImgTag(f='D:/1/IMG_7901.JPG') )
    #print ( getImgTags(f='D:/1/IMG_7581.JPG') )
    handler()