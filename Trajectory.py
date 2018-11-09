'''
This is a program to find the trajectory from a series of images.

Author: Tony He

Date: Nov.3, 2018
'''
from PIL import Image
import numpy as np
import os,sys
import logging as lg
import pandas as pd
import copy as cp

def ConvertGray2Bilevel(infile, rate, b_file_out):
	'''
	The function to convert gray-scale to bi-level image.
	Parameters:
	infile-the input file directory
	rate-the rate to convert gray-scale image to bi-level.
	b_file_out-binary value for outputting bi-level image file.
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
	This is the function to find out the object in bi-level image
	Input parameters:
	biimg_mat- The matrix contains bi-level image.
	'''
	out_mat=[[0]*2 for i in range(2)]
	currow=0
	for rowi in range(len(biimg_mat)):
		for coli in range(len(biimag_mat[0])):
			if biimag_mat[rowi][coli]>0:
				if currow<=1:
					out_mat[currow]=[rowi,coli]
					currow+=1
				else:
					out_mat.append([rowi,coli])
					currow+=1
	return out_mat

def GetObjectByCCL(biimg_mat):
	'''
	This function will check out all objects in image by using
	connected-component labeling algorithm.
	Input parameter(s):
	biimg_mat- it is a matrix which contains a bi-level image.
	'''
	nbh=[] # neighbor temporary list
	labels=[[0]*len(biimg_mat[0]) for i in range(len(biimg_mat))]
	lbl_eql={} # labels' mapping dictionary
	lbl_id=1 # current label ID
	cur_px_lbl=0 # the label of current pixel
	nbh_lbls=[] # labels of current neighbor
	nbh_tmp_lbl=0 # the temporary label of current pixel neighbor

	tmp_lu=0 # left-up neighbor label
	tmp_cu=0 # center-up neighbor label
	tmp_ru=0 # right-up neighbor label
	tmp_lc=0 # left-center neighbor label

	# first pass
	# loop of pixels in bi-level images
	lg.info('Start the loop of the first pass.')
	for rowi in range(len(biimg_mat)):
		for coli in range(len(biimg_mat[0])):
			if rowi==388 and coli==138:
				tstbreak=1

			if biimg_mat[rowi][coli]>0: #whether current pixel is foreground
				lg.debug('Pixel is in row %d, column %d',rowi,coli)
				lg.debug('Pixel value is %d',biimg_mat[rowi][coli])
				lg.debug("Pixel's label is %d",labels[rowi][coli])
				lg.debug('Label ID is %d',lbl_id)	
				lg.debug('Foreground pixel and start to check its neighbors.')
				# Check current neighbors.
				
				nbh.clear()
				if rowi>0 and rowi<len(biimg_mat) and coli>0 and coli <len(biimg_mat[0]): # pixel is not on the boundary of image
				# In fact, it does need to four pixels:up-left,up-center,up-right and left-center.
					lg.debug('Center area pixels')
					tmp_lu=labels[rowi-1][coli-1] #left-up neighbor
					tmp_cu=labels[rowi][coli-1] #center-up neighbor
					tmp_ru=labels[rowi+1][coli-1] #right-up neighbor
					tmp_lc=labels[rowi][coli-1] #left-center neighbor
					lg.debug("LU,CU,RU and LE neighbors' labels are %d, %d, %d, %d.",tmp_lu,tmp_cu,tmp_ru,tmp_lc)
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
						lg.debug('tmp_lu>0')
					if tmp_cu>0:
						nbh_lbls.append(tmp_cu)
						lbl_eql=RenewneighborEquivalance(lbl_eql,tmp_lu,tmp_cu)
						lg.debug('tmp_cu>0')
					if tmp_ru>0:
						nbh_lbls.append(tmp_ru)
						lbl_eql=RenewneighborEquivalance(lbl_eql,tmp_cu,tmp_lu)
						lg.debug('tmp_ru>0')
					if tmp_lc>0:
						nbh_lbls.append(tmp_lc)
						lbl_eql=RenewneighborEquivalance(lbl_eql,tmp_ru,tmp_lc)
						lg.debug('tmp_lc>0')
									
				elif rowi>0 and coli==0:#pixel lies on the left boundary of image
				# this mode just need check two neighbors
					lg.debug('Left boundary pixels')
					tmp_lu=labels[rowi-1][coli-1] #left-up neighbor
					tmp_cu=labels[rowi][coli-1] #center-up neighbor
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
						lg.debug('tmp_lu>0')
					if tmp_cu>0:
						nbh_lbls.append(tmp_cu)
						lbl_eql=RenewneighborEquivalance(lbl_eql,tmp_lu,tmp_cu)
						lg.debug('tmp_cu>0')
									
				elif rowi>0 and coli==len(biimg_mat[0]):#pixel is on the right boundary of image
				# this mode just need check three neighbors
					lg.debug('Right boundary pixels')
					tmp_lu=labels[rowi-1][coli-1] #left-up neighbor
					tmp_cu=labels[rowi][coli-1] #center-up neighbor
					tmp_lc=labels[rowi][coli-1] #left-center neighbor
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
						lg.debug('tmp_lu>0')
					if tmp_cu>0:
						nbh_lbls.append(tmp_cu)
						lbl_eql=RenewneighborEquivalance(lbl_eql,tmp_lu,tmp_cu)
						lg.debug('tmp_cu>0')
					if tmp_lc>0:
						nbh_lbls.append(tmp_lc)
						lbl_eql=RenewneighborEquivalance(lbl_eql,tmp_cu,tmp_lc)
						lg.debug('tmp_lc>0')
						
				# labeled the pixel
				if nbh_lbls:
					lg.debug('nbh_lbls is not empty.')
					labels[rowi][coli]=min(nbh_lbls)
				else:
					lg.debug('nbh_lbls is empty.')
					labels[rowi][coli]=lbl_id
					lbl_id+=1

	
	# second pass
	lg.info('Start the second pass.')
	for m_obj in lbl_eql:
		minlbl=min(lbl_eql[m_obj])
		lbl_eql[m_obj]=minlbl
		
	for rowi in range(len(biimg_mat)):
		for coli in range(len(biimg_mat[0])):
			if labels[rowi][coli]>0:
				labels[rowi][coli]=lbl_eql[labels[rowi][coli]]
	
	return labels
	

def RenewneighborEquivalance(LEDict,lbl1,lbl2):
	if lbl1>0:
		if not(lbl1 in LEDict):
			LEDict[lbl1]=[lbl1]
		if lbl2>0 and not(lbl2 in LEDict[lbl1]):
			LEDict[lbl1].append(lbl2)
	
	if lbl2>0:
		if not(lbl2 in LEDict):
			LEDict[lbl2]=[lbl2]
		if lbl1>0 and not(lbl1 in LEDict[lbl2]):
			LEDict[lbl2].append(lbl1)
	return LEDict
	
if __name__=='__main__':
	LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
	lg.basicConfig(filename='tr.log', level=lg.DEBUG, format=LOG_FORMAT)
	biimg=[]
	labels=[]
	biimg=ConvertGray2Bilevel('snap0.bmp',0.95,False)
	labels=GetObjectByCCL(biimg)
	df=pd.DataFrame(labels)
	df.to_csv('labels.txt')
