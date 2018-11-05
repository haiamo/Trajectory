'''
This is a program to find the trajectory from a series of images.

Author: Tony He

Date: Nov.3, 2018
'''
from PIL import Image
import numpy as np
import os,sys

def ConvertGray2Bilevel(infile, rate, b_file_out):
    '''
    The function to convert gray-scale to bilevel image.
    Parameters:
    infile-the input file dirctory
    rate-the rate to convert gray-scale image to bilevel.
    b_file_out-binary value for outputing bilevel image file.
    '''
    in_img=Image.open(infile)
    img_mat=np.array(in_img)
    biimg_mat=255*(img_mat>np.max(img_mat)*rate)
    out_biimg=Image.fromarray(biimg_mat)
    
    if b_file_out:
        outfile='bi'+os.path.splitext(infile)[0]+'_'+str(int(mr*100))+'.bmp'
        out_biimg=out_biimg.convert('L')
        out_biimg.save(outfile,'BMP')
    
    return biimg_mat

def GetPCAFromBiImg(biimg_mat):
    '''
    This is the function to find out the object in bilevel image
    Input parameters:
    biimg_mat- The matrix contains bilevel image.
    '''
    out_mat=[[0]*2 for i in range(2)]
    currow=0
    for rowi in range(len(biimg_mat)):
        for coli in range(len(biimg_mat[0])):
            if biimg_mat[rowi][coli]>0:
                if currow<=1:
                    out_mat[currow]=[rowi,coli]
                    currow+=1
                else:
                    out_mat.append([rowi,coli])
                    currow+=1
    return out_mat

if __name__=='__main__':
    m_biimg=ConvertGray2Bilevel('snap0.bmp',0.9,False)
    m_pcadata=GetPCAFromBiImg(m_biimg)
