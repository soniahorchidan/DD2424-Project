import numpy as np
import os
import sys
import cv2
from scipy import misc
from sklearn.neighbors import NearestNeighbors
import numpy as np
from manipulate_data import convert_rgb_to_lab


def decode(encoding):
	cord = np.load("pts_in_hull.npy")
	temperature = 0.34
	encoding[encoding!=0] = np.exp(np.log(encoding[encoding!=0])/temperature)
	encoding = encoding/np.sum(encoding,axis=2)[:,:,np.newaxis]

	a_layer = np.sum(encoding * cord[:,0],axis=2)
	b_layer = np.sum(encoding * cord[:,1],axis=2)
	a_layer = (a_layer + 90) / 190 * 256
	b_layer = (b_layer + 110) / 220 * 256
	
	return a_layer, b_layer


def softencoding(a_channel, b_channel):

	cord = np.load("pts_in_hull.npy")
	prob = np.load("prior_probs.npy")
	
	#Create weights
	alpha = 1
	gamma = 0.5

	uni_probs = np.zeros_like(prob)
	uni_probs[prob!=0] = 1.
	uni_probs = uni_probs/np.sum(uni_probs)

	prior_mix = (1-gamma)*prob + gamma*uni_probs

	prior_factor = prior_mix**-alpha
	prior_factor = prior_factor/np.sum(prob*prior_factor) 

	nbrs = NearestNeighbors(n_neighbors=5, algorithm='ball_tree').fit(cord)

	encoding = np.zeros([16*16,313])
	a = a_channel.reshape(-1,1)
	b = b_channel.reshape(-1,1)
	X = np.column_stack((a,b))
	distances, indices = nbrs.kneighbors(X)
	sigma = 5
	wts = np.exp(-distances**2/(2*sigma**2))
	wts = wts/np.sum(wts,axis=1)[:,np.newaxis]

	encoding[np.arange(0,16*16)[:,np.newaxis],indices] = wts ## * prior_factor[indices[:,0],np.newaxis]
	encoding = encoding.reshape(16,16,313)
	return encoding