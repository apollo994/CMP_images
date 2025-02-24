#!/usr/bin/env python3
#Fabio Zanarello, Sanger Institute, 2020

import os
import sys
import glob
import argparse
from collections import defaultdict
from PIL import Image
import random


from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


def get_target_size(exp, fold, pos, train_target, validation_target):

    train_pos_len = len(glob.glob(f'{exp}/{fold}/train/{pos}/*.jpg'))
    train_neg_len = len(glob.glob(f'{exp}/{fold}/train/Not_{pos}/*.jpg'))

    train_max_size = max([train_pos_len, train_neg_len])

    if train_target < train_max_size:
        train_target_updated = train_max_size
    else:
        train_target_updated = train_target


    validation_pos_len = len(glob.glob(f'{exp}/{fold}/validation/{pos}/*.jpg'))
    validation_neg_len = len(glob.glob(f'{exp}/{fold}/validation/Not_{pos}/*.jpg'))

    validation_max_size = max([validation_pos_len, validation_neg_len])

    if validation_target < validation_max_size:
        validation_target_updated = validation_max_size
    else:
        validation_target_updated = validation_target


    return train_target_updated, validation_target_updated

def increase_sample(target_folder, target_size, datagen):
    dirs = [x[0] for x in os.walk(target_folder)]
    dirs = dirs[1:]

    for dir in dirs:

        imgs = glob.glob(dir+'/*.jpg')
        n_file = len(imgs)
        n_to_add = target_size - n_file
        print ()
        print (f'{n_file} images in {dir}')
        print (f'will bring this number to {target_size}')

        for i in range(round(n_to_add/2)):
            rand = random.sample(imgs,1)
            im = Image.open(rand[0])
            im= im.resize((150, 150), Image.ANTIALIAS)
            x = img_to_array(im)
            x = x.reshape((1,) + x.shape)
            i = 0
            for batch in datagen.flow(x, batch_size=1, save_to_dir=dir, save_prefix='aug', save_format='jpeg'):
                i += 1
                if i > 1:
                    break

        print (f'{n_to_add} new images added to {dir}')


def main():
    parser = argparse.ArgumentParser(description='My nice tool.')
    parser.add_argument('--train', default= 1000 , type=int, help='target size for training')
    parser.add_argument('--valid', default= 200 , type=int, help='target size for vaidation')
    parser.add_argument('--exp', metavar='EXP', help='name of the experiment')
    parser.add_argument('--v', metavar='V', default= False, help='augment also validation')
    parser.add_argument('--pos', metavar='POS', help='positive label')

    args = parser.parse_args()

    datagen = ImageDataGenerator(
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='reflect')

    folds = [dI for dI in os.listdir(args.exp) if os.path.isdir(os.path.join(args.exp,dI))]
    folds = [f for f in folds if f[0]=='f']
    folds = sorted(folds)




    for fold in folds:

        train_target, validation_target = get_target_size(args.exp, fold, args.pos, args.train, args.valid)

        increase_sample(f'{args.exp}/{fold}/train/', train_target, datagen)
        if args.v:
            increase_sample(f'{args.exp}/{fold}/validation/', validation_target, datagen)







if __name__ == "__main__":
  main()
