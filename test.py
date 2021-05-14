import os
import numpy as np
import random
import cv2
import glob
import shutil
from tqdm import tqdm

def composite_foreground2background(foreground, background, size_thresh=0.7):
    '''
    Composite foreground to background follow the equation below:
        I = alpha*Foreground + (1-alpha)*background
    Tricks: 
        Foreground will be put on the central area of background randomly
    Param: 
        foreground: foreground 4 channel image (RGBA) 
        background: background 3 channel image
        size_thresh: threshold for making foreground image smaller than the shorter side of background image
    Return: 
        composite_image: 3 channel image with foreground, dtype = np.uint8
        composite_mask: 1 channel mask, dtype = np.uint8
    '''
    foreground_height, foreground_width, _ = foreground.shape
    background_height, background_width, _ = background.shape

    edge_thresh = 0.1   # threshold for placing foreground in the central area of background image

    # resize foreground to proper size which foreground size should smaller than background size
    if foreground_width >= size_thresh*background_width and foreground_height < size_thresh*background_height:
        resize_scale = (size_thresh*background_width)/foreground_width
    elif foreground_width < size_thresh*background_width and foreground_height >= size_thresh*background_height:
        resize_scale = (size_thresh*background_height)/foreground_height
    elif foreground_width >= size_thresh*background_width and foreground_height >= size_thresh*background_height:
        resize_scale = min((size_thresh*background_width)/foreground_width,(size_thresh*background_height)/foreground_height)
    else: 
        resize_scale = 1
    if resize_scale != 1:
        foreground = cv2.resize(foreground, (int(resize_scale*foreground_width), int(resize_scale*foreground_height)), interpolation = cv2.INTER_AREA)
    
    foreground_height, foreground_width, _ = foreground.shape
    foreground_new = np.zeros((background_height, background_width,4))
    # generate random composite position
    position = [random.randint(int(edge_thresh*background_height), background_height - foreground_height - int(edge_thresh*background_height)), 
                random.randint(int(edge_thresh*background_width), background_width - foreground_width - int(edge_thresh*background_width))] 
    
    foreground_mask = foreground[:,:,3]/255.    # Normalize
    foreground_mask4compsite = np.array([foreground[:,:,0]*foreground_mask, 
                                            foreground[:,:,1]*foreground_mask,
                                            foreground[:,:,2]*foreground_mask,
                                            foreground[:,:,3]]).transpose((1,2,0))
    foreground_new[position[0]:position[0] + foreground_height, position[1]:position[1] + foreground_width] = foreground_mask4compsite
    
    background_mask = foreground_new[:,:,3].astype(np.uint8)
    background_mask4composite = 1 - cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)/255 # 1 channel to 3 channels
    background_new = background * background_mask4composite
    # composite foreground with background
    composite_image = background_new + foreground_new[:,:,:3]
    composite_mask = background_mask
    
    return composite_image, composite_mask

def prune_foreground(foreground):
    '''
    Prune foreground by removing regions where alpha == 0 
    Param:
        foreground: 4 channel png (RGBA)
    Return:
        foreground_new: prune foreground, dtype = uint8
    '''
    foreground_mask = foreground[:,:,3]
    pos_list = np.where(foreground_mask>0)
    # crop image where Alpha > 0
    foreground_new = foreground[min(pos_list[0]):max(pos_list[0]) + 1, min(pos_list[1]):max(pos_list[1]) + 1]

    return foreground_new

def refresh_folder(folder_path):
    '''
    Create folder if not exist 
    Clean all files in folder if exist
    '''
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)

def load_foreground(file_path):
    '''
    Load and pre-process image from given file path
    Foreground should be 4 channel image (RGBA)
    '''
    foreground = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if foreground.shape[2] == 4:
        foreground = prune_foreground(foreground)
        flag = True
    else:
        print(file_path.split(os.sep)[-1], ' Invalid foreground. Will skip the composition of this foreground.')
        foreground = None
        flag = False

    return foreground, flag

def load_background(file_path):
    '''
    Load background image
    Background should be 3 channel image
    '''
    background = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    if background.shape[2] == 3:
        background = background
        flag = True
    else:
        print(file_path.split(os.sep)[-1], ' Invalid background. Will skip this background.')
        background = None
        flag = False

    return background, flag


def generate_random_background():


if __name__ == '__main__':

    foreground, flag = load_foreground('1.png')
    background, flag = load_background('train_data/DUTS/DUTS-TR/HRSOD_train/00000.jpg')

    composite_image, composite_mask = composite_foreground2background(foreground, background,size_thresh=0.8)
    cv2.imwrite(os.path.join('matte.jpg'), composite_image)
    # cv2.imwrite(os.path.join(save_mask_dir, foreground_name + str(i) + '.png'), composite_mask)
    print('Complete Generating Dateset \n','!!Enjoy Coding!!')
'''
flip whole dataset
'''
# data_dir = os.path.join(os.getcwd(), 'train_data' + os.sep)
# image_dir = os.path.join(data_dir, 'DUTS', 'DUTS-TR', 'HRSOD_train' + os.sep)
# tra_label_dir = os.path.join(data_dir, 'DUTS', 'DUTS-TR', 'HRSOD_train_mask' + os.sep)

# img_name_list = glob.glob(image_dir + '*')
# mask_name_list = glob.glob(tra_label_dir + '*')

# print("---")
# print("train images: ", len(img_name_list))
# print("train labels: ", len(mask_name_list))
# print("---")

# for i_img, img_path in enumerate(img_name_list):
#     img = cv2.imread(img_path)
#     img_name = img_name_list[i_img].split(os.sep)[-1].split('.')[0]
#     print('flip image:',img_name)
#     flipped_img = cv2.flip(img, 1)
#     flipped_img_name = '1' + img_name
#     cv2.imwrite(os.path.join(image_dir, flipped_img_name + '.jpg'), flipped_img)
#     # print(flipped_img_name)


# for i_img, img_path in enumerate(mask_name_list):
#     img = cv2.imread(img_path)
#     img_name = img_name_list[i_img].split(os.sep)[-1].split('.')[0]
#     print('flip mask: ',img_name)
#     flipped_img = cv2.flip(img, 1)
#     flipped_img_name = '1' + img_name 
#     cv2.imwrite(os.path.join(tra_label_dir, flipped_img_name + '.png'),flipped_img)
#     # print(flipped_img_name)