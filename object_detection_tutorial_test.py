# -*- coding: utf-8 -*-

import numpy as np
import serial
import os
import six.moves.urllib as urllib
import sys
import time
import tarfile
import tensorflow as tf

from PIL import Image
# import the necessary packages
from skimage.measure import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import csv

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
 
from utils import label_map_util
 
from utils import visualization_utils as vis_util
 

 
def start():
    print("1")
        # What model to download.
    MODEL_NAME = 'ssd_mobilenet_v1_coco_11_06_2017'
    MODEL_FILE = MODEL_NAME + '.tar.gz'
    print("2")
    DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
    print("3")
        # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
    print("4")
         
        # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')
         
    NUM_CLASSES = 90
         
    opener = urllib.request.URLopener()
    print("5")
#
    opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
    print("6")
 
    tar_file = tarfile.open(MODEL_FILE)
    for file in tar_file.getmembers():
        file_name = os.path.basename(file.name)
        if 'frozen_inference_graph.pb' in file_name:
            tar_file.extract(file, os.getcwd())
    print("7")
               
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    print("8")
                                
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
     
    print("9")
# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# image3.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
   # PATH_TO_TEST_IMAGES_DIR = 'test_images'
   # TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'img{}.jpg'.format(i)) for i in range(1, 3) ]
    #IMAGE_SIZE = (12, 8)
    cap = cv2.VideoCapture(1)
   # print("d@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    hitf = open("hitlist.csv",'w')
    #hitf.write('image,class,score,bb0,bb1,bb2,bb3\n')
    hitlim = 0.5
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
      
            ret=True
        #    cnt = 0
            cnt=1
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
           
        # 사용하는 아두이노에 따라 밑에 시리얼정보를 바꿔줘야함    
       #    ser = serial.Serial("/dev/tty.wchusbserial1410", 9600)
       #    ser.write('1')
            while cnt < 5:  
                 if cnt == 0:
                        image = Image.open('./download/test.jpg')
                        image_np = load_image_into_numpy_array(image)
                 else:   
                     ret,image_np = cap.read() 
            
                 cv2.imwrite('ori{}.jpg'.format(cnt),image_np, params=[cv2.IMWRITE_PNG_COMPRESSION,0])
           
                 image_np_expanded = np.expand_dims(image_np, axis=0)
             
                 (boxes, scores, classes, num) = sess.run(
                 [detection_boxes, detection_scores, detection_classes, num_detections],
                 feed_dict={image_tensor: image_np_expanded})
       
          # Write the results to hitlist - one line per hit over the 0.5
                 nprehit = scores.shape[1] # 2nd array dimension
             # print(nprehit)
                 for j in range(nprehit):
                   fname = "image"+str(cnt)
                   classid = int(classes[0][j])
                   classname = category_index[classid]["name"]
                   score = scores[0][j]
                   if (score>=hitlim):
                       sscore = str(score)
                       bbox = boxes[0][j]
                       b0 = str(bbox[0])
                       b1 = str(bbox[1])
                       b2 = str(bbox[2])
                       b3 = str(bbox[3])
                       line = ",".join([fname,classname,sscore,b0,b1,b2,b3])
                       hitf.write(line+"\n")
       
                 vis_util.visualize_boxes_and_labels_on_image_array(
                  image_np,
                  np.squeeze(boxes),
                  np.squeeze(classes).astype(np.int32),
                  np.squeeze(scores),
                  category_index,
                  use_normalized_coordinates=True,
                  line_thickness=8)
                 
                 cv2.imshow('image',cv2.resize(image_np,(600,600)))
                 cv2.imwrite('detected_image{}.jpg'.format(cnt),image_np, params=[cv2.IMWRITE_PNG_COMPRESSION,0])
                 cnt = cnt + 1
                 time.sleep(2)
                 
            # close hitlist
            hitf.flush()
            hitf.close()
            im_trim()
            start_compare()



def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)
  
def im_trim():
    f = open('hitlist.csv', 'r', encoding='utf-8')
    rdr = csv.reader(f)
    cnt = 0
    for line in rdr:
        img = Image.open('ori{}.jpg'.format(line[0][5]))  
       
        (im_width, im_height) = img.size
        #print(im_width, im_height)
        left = int(float(line[3])*im_height)
        top = int(float(line[4])*im_width)
        width = int((float(line[5])-float(line[3]))*im_height)
        height = int((float(line[6])-float(line[4]))*im_width)
        
        t1 = top
        t2 = left
        area = (t1, t2, t1+height, t2+width)

 #   print (area)
        cropped_img = img.crop(area)
        if line[0][5] == 0:
            cropped_img.save('download\Compare_ORI.jpg')
        else:
            cropped_img.save('cropped\cropped_img{}.jpg'.format(cnt))
    #cv2.imwrite('cropped_img{}.jpg'.format(cnt),cropped_img, params=[cv2.IMWRITE_PNG_COMPRESSION,0])
        cnt = cnt + 1
    f.close()    

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def compare_images(imageA, imageB, title):
	# compute the mean squared error and structural similarity
	# index for the images
	m = mse(imageA, imageB)
	s = ssim(imageA, imageB)

	# setup the figure
	fig = plt.figure(title)
#	plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))

        
	# show first image
	ax = fig.add_subplot(1, 2, 1)
	plt.imshow(imageA, cmap = plt.cm.gray)
#	plt.axis("off")

	# show the second image
	ax = fig.add_subplot(1, 2, 2)
	plt.imshow(imageB, cmap = plt.cm.gray)
	plt.axis("off")

	# show the images
#	plt.show()
	return s 

# load the images -- the original, the original + contrast,
# and the original + photoshop
idx = 0
def start_compare():
    cnt = 0
    cnt = len(os.listdir('C:/Users/hayeon/Desktop/종프2/object_detection/cropped'))
    
    img_resize_List = []
 #   img_resize_List.append(cv2.resize(cv2.imread("./download/Compare_ORI.jpg"),(480,640)))
    img_resize_List.append(cv2.resize(cv2.imread("./download/test.jpg"),(480,640)))
        
    for i in range(cnt):
        img_resize_List.append(cv2.resize(cv2.imread("./cropped/cropped_img{}.jpg".format(i)),(480,640)))
           
        
    # convert the images to grayscale
    img_gray_List = []
    for i in range(cnt+1):
        img_gray_List.append(cv2.cvtColor(img_resize_List[i], cv2.COLOR_BGR2GRAY))
    
    
    ssim_max = -1
  
    # compare the images
    for i in range(cnt):
        print(i)
        temp = compare_images(img_gray_List[0], img_gray_List[i+1], "Original vs. cropped{}".format(i+1))
        if ssim_max < temp:
            ssim_max=temp
            idx=i+1
            
  #  print("The Most Similar picture is")    
    compare_images(img_gray_List[0], img_gray_List[idx], "Compare")
    
def getMostSimilarPic():
    return idx
          
 