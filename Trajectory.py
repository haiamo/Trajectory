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
			if biimg_mat[rowi][coli]>0: #whether current pixel is foreground
				lg.debug('Pixel is in [%d, %d]',rowi,coli)
				lg.debug('Pixel value is %d',biimg_mat[rowi][coli])
				lg.info('Foreground pixel and start to check its neighbors.')
				# Check current neighbors.
				
				nbh_lbls.clear()
				if rowi>0 and coli>0 and coli <len(biimg_mat[0]): #center area w/o up-boundary
				# In fact, it does need to four pixels:up-left,up-center,up-right and left-center.
					lg.debug('Center area w/o up-boundary pixels')
					tmp_lu=labels[rowi-1][coli-1] #left-up neighbor
					tmp_cu=labels[rowi-1][coli] #center-up neighbor
					tmp_ru=labels[rowi-1][coli+1] #right-up neighbor
					tmp_lc=labels[rowi][coli-1] #left-center neighbor
					lg.debug("LU,CU,RU and LC neighbors' labels are %d, %d, %d, %d.",tmp_lu,tmp_cu,tmp_ru,tmp_lc)
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
					if tmp_cu>0:
						if not(tmp_cu in nbh_lbls):
							nbh_lbls.append(tmp_cu)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_lu,tmp_cu)
					if tmp_ru>0:
						if not(tmp_ru in nbh_lbls):
							nbh_lbls.append(tmp_ru)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_ru,tmp_cu)
					if tmp_lc>0:
						if not(tmp_lc in nbh_lbls):
							nbh_lbls.append(tmp_lc)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_cu,tmp_lc)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_lu,tmp_lc)
									
				elif rowi>0 and coli==0:#left boundary w/o left-up corner
				# this mode just need check two neighbors
					lg.debug('Left boundary w/o left-up pixel')
					tmp_lu=labels[rowi-1][coli-1] #left-up neighbor
					tmp_cu=labels[rowi-1][coli] #center-up neighbor
					lg.debug("LU and CU neighbors' labels are %d, %d.",tmp_lu,tmp_cu)
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
					if tmp_cu>0:
						if not(tmp_cu in nbh_lbls):
							nbh_lbls.append(tmp_cu)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_lu,tmp_cu)
									
				elif rowi>0 and coli==len(biimg_mat[0]):#right boundary w/o right-up corner
				# this mode just need check three neighbors
					lg.debug('Right boundary w/o right-up pixels')
					tmp_lu=labels[rowi-1][coli-1] #left-up neighbor
					tmp_cu=labels[rowi-1][coli] #center-up neighbor
					tmp_lc=labels[rowi][coli-1] #left-center neighbor
					lg.debug("LU, CU and LC neighbors' labels are %d, %d.",tmp_lu,tmp_cu,tmp_lc)
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
					if tmp_cu>0:
						if not(tmp_cu in nbh_lbls):
							nbh_lbls.append(tmp_cu)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_lu,tmp_cu)
					if tmp_lc>0:
						if not(tmp_lc in nbh_lbls):
							nbh_lbls.append(tmp_lc)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_cu,tmp_lc)
						lbl_eql=RenewNeighborEquivalance(lbl_eql,tmp_lu,tmp_lc)
				
				elif rowi==0 and coli>0:#up boundary w/o left-up corner
				# this mode just need check one neighbor
					lg.debug('up boundary w/o left-up corner')
					tmp_lu=labels[rowi][coli-1] #left neighbor
					lg.debug("Left neighbor label is %d.",tmp_lu)
					if tmp_lu>0:
						nbh_lbls.append(tmp_lu)
						
				# labeled the pixel
				lg.debug('Label ID is %d',lbl_id)
				if nbh_lbls:
					lg.debug('nbh_lbls is not empty.')
					labels[rowi][coli]=min(nbh_lbls)
				else:
					lg.debug('nbh_lbls is empty.')
					labels[rowi][coli]=lbl_id
					lbl_eql[lbl_id]=[lbl_id]
					lbl_id+=1
				lg.debug('Label ID is %d, after assigning it to pixel label.',lbl_id)
				lg.debug("Pixel's label is %d",labels[rowi][coli])
	
	# renew label equivalance
	'''
	for kk in lbl_eql:
		eqlist=lbl_eql.get(kk)
		for vi in eqlist:
	'''		
	# second pass
	lg.info('Start the second pass.')
	origin_l_equ=cp.deepcopy(lbl_eql)
	for kk in lbl_eql:
		minlbl=min(lbl_eql[kk])
		lbl_eql[kk]=minlbl
		
	for rowi in range(len(labels)):
		for coli in range(len(labels[0])):
			cur_px_lbl=labels[rowi][coli]
			if cur_px_lbl>0 and cur_px_lbl in lbl_eql:
				labels[rowi][coli]=lbl_eql.get(cur_px_lbl)
	
	return labels,origin_l_equ,lbl_eql
	

def RenewNeighborEquivalance(LEDict,lbl1,lbl2):
	try:
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
	except TypeError:
		print('lbl1 and lbl2 are',lbl1,' ',lbl2)
	return LEDict
	
if __name__=='__main__':
	LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
	lg.basicConfig(filename='tr.log', level=lg.DEBUG, format=LOG_FORMAT)
	
	biimg=[]
	'''
	labels=[]
	biimg=ConvertGray2Bilevel('snap0.bmp',0.95,False)
	'''
	from xlrd import *
	xfile=open_workbook('tstbiimg.xlsx')

	biimg=[]
	for s in xfile.sheets():
		for rowi in range(s.nrows):
			r_vals=[]
			for coli in range(s.ncols):
				r_vals.append(s.cell(rowi,coli).value)
			biimg.append(r_vals)
	labels,ori_l_equ,label_equ=GetObjectByCCL(biimg)
	df=pd.DataFrame(labels)
	df.to_csv('labels.txt')
