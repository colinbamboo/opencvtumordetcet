# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 16:26:44 2021

@author: colin
"""


import pydicom as dicom
import os
import cv2
import PIL # 可選
import shutil, os
from time import sleep

folder_path = 'new'
images_path = os.listdir(folder_path)
print("images_path = ",images_path)
images_path = "".join(images_path)
ds = dicom.dcmread(os.path.join(folder_path, images_path))
pixel_array_numpy = ds.pixel_array
images_path = images_path. replace('.dcm', '.jpg') #更改副檔名
pixel_array_numpy = cv2.cvtColor(pixel_array_numpy, cv2.COLOR_RGB2BGR)
cv2.imwrite(os.path.join(folder_path, images_path), pixel_array_numpy)

#%%
import cv2
import os
import glob  #找檔案
path = (glob.glob("new/*.jpg"))
path
pic = path[0]
pic
#'convert/ESO-052(O)\\I10.jpg'
# 讀取第一章照片
im = cv2.imread(pic)
# Select ROI
r = cv2.selectROI(im)
#計算矩形座標
(x, y, w, h) = r
#查看矩形座標是否正確
imCrop = im[y: y + h, x:x + w] # 裁切圖片
print(r)
cv2.imshow("Image", imCrop) #顯示圖片
cv2.waitKey(10000)
cv2.destroyAllWindows()
checked = int(input('繼續請輸入 1：'))
if checked == 1:
    output_folder = 'ROI/'+path[0][4:8]
    # 資料夾中所有圖片自動裁切
    for i in path:
        image_read = cv2.imread(i)
        roiImg = image_read[y: y + h, x:x + w]
        cv2.imwrite(output_folder+i[8:], roiImg)
else:
    print("program shutdown")
    
#%%
path = (glob.glob("ROI/*.jpg")) #匯入所有jpg圖片路徑
print(path)
output_folder = 'bright spot/' #建立一個輸出資料夾名稱
if not os.path.exists(output_folder): os.makedirs(output_folder) #如果目錄下沒有輸出資料夾，就創建一個
#迴圈一筆筆讀取
#i每跑一次就收到一張圖片路徑
for i in path:
    img = cv2.imread(i) #讀取i路徑
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #RGB轉灰階
    blur = cv2.GaussianBlur(gray, (41,41), 0) #高斯模糊除雜訊，(41,41)為模糊程度
    #開始找最大像素點(亮點座標)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur) #能夠回傳最小、大的像素值和座標
    minVal
    # 0.0
    maxVal
    # 163.0
    minLoc
    # (0, 0)
    maxLoc
    # (529, 342)
    #判斷是否為亮點 最大值175是不斷嘗試出來的
    if maxVal >= 175:
        cv2.circle(img, maxLoc, 41, (255, 0, 0), 2) #在座標上畫一個圓
        cv2.putText(img, str(i), (400,300), cv2.FONT_HERSHEY_SIMPLEX, 1,
		(50, 168, 82), 2, cv2.LINE_AA) #cv2.putText(影像, 文字, 座標, 字型, 大小, 顏色, 線條寬度, 線條種類)
        cv2.imwrite(output_folder + i[4:], img) #儲存亮點照片
        cv2.imshow("results", img) #秀出圖片
        cv2.waitKey(1000) #圖片顯示持續時間(單位毫秒)，0為一直顯示
        cv2.destroyAllWindows()
    else:
        #儲存沒有亮點的照片
        cv2.imwrite(output_folder + i[4:], img)
#%%
path = (glob.glob("ROI/*.jpg"))
output_folder = "thresh/"
if not os.path.exists(output_folder): os.makedirs(output_folder)
for i in path:
    image = cv2.imread(i)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #將圖片轉成灰階
    blur = cv2.GaussianBlur(gray, (41,41),0) #高斯模糊
    # 腫瘤與背景分離的二值化處理
    thresh = cv2.threshold(blur, 175, 255, cv2.THRESH_BINARY)[1] #175是亮點亮度
    cv2.imwrite(output_folder + i[3:], thresh)
#%%
path = (glob.glob("thresh/*.jpg"))
f = open("area.txt", "w") #串建txt準備儲存面積數值
#f = open('檔案', '模式’)  模式”w”為新建檔案
for i in path:
    image = cv2.imread(i)
    edged = cv2.Canny(image, 175, 255) #Canny演算法，算出邊緣。175下限閥值
    #確認邊緣訊息
    (contours,_) = cv2.findContours(edged,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #cv2.RETR_EXTERNAL外部輪廓；CHAIN_APPROX_SIMPLE簡單輪廓
    print(contours)
    # findContours 查找輪廓  
    # cv2.RETR_EXTERNAL 只找出外輪廓  
    # cv2.CHAIN_APPROX_SIMPLE 壓縮水平方向，垂直方向，對角線方向的元素，只保留該方向的終點座標
    if contours != []:
        area = cv2.contourArea(contours[0]) #計算面積area
        print("面積: %.2f" %area)
        value = "%s = %.2f" %(i, area) + "\n" #我要寫入txt的格式
        f.write(value) #寫入
f.close()
#%%
path = (glob.glob("thresh/I420.jpg"))
for i in path:
    image = cv2.imread(i)
    edged = cv2.Canny(image, 175, 255) #Canny演算法，算出邊緣。175下限閥值
    #確認邊緣訊息
    (contours,_) = cv2.findContours(edged,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # cv2.RETR_EXTERNAL外部輪廓；CHAIN_APPROX_SIMPLE簡單輪廓
    cv2.drawContours(image,contours,-1,(255,0,0),3,lineType=cv2.LINE_AA)
    # cv2.drawContours(圖片,輪廓,繪製哪條輪廓(-1為全畫),顏色,粗度,輪廓線型(cv2.LINE_AA 是反鋸齒線))
    cv2.imshow("Contours",image)
    cv2.waitKey()
    cv2.destroyAllWindows()