# encoding: utf-8
###############################################################################
# name      : idxubyte.py
# author    : carl_zys@163.com
# created   : 2017-12-10
# purpose   : idx1_ubyte file decode/encode 
# copyright : copyright (c) zhuyunsheng carl_zys@163.com all rights received  
################################################################################
"""
THE IDX FILE FORMAT

the IDX file format is a simple format for vectors and multidimensional matrices of various numerical types.
The basic format is

magic number 
size in dimension 0 
size in dimension 1 
size in dimension 2 
..... 
size in dimension N 
data

The magic number is an integer (MSB first). The first 2 bytes are always 0.

The third byte codes the type of the data: 
0x08: unsigned byte 
0x09: signed byte 
0x0B: short (2 bytes) 
0x0C: int (4 bytes) 
0x0D: float (4 bytes) 
0x0E: double (8 bytes)

The 4-th byte codes the number of dimensions of the vector/matrix: 1 for vectors, 2 for matrices....

The sizes in each dimension are 4-byte integers (MSB first, high endian, like in most non-Intel processors).

The data is stored like in a C array, i.e. the index in the last dimension changes the fastest. 
"""
import gzip
from struct import unpack_from,calcsize
import numpy as np
import matplotlib.pyplot as plt

def ungzip(gz):
        with gzip.open(gz) as f:
            if f:
                return f.read()
            else:return None
class idx3_ubyte(object):    
    def decode(self,idx1_ubype_file=None):
        fc = ungzip(idx1_ubype_file)
        print ( unpack_from('>iiii',fc,0 ) )
        offset = 0
        fmt_header = '>iiii'
        magicnum, imgcnt, rows, cols = unpack_from(fmt_header, fc, offset)
        picsize = rows * cols
        print ( 'magicnum:%d, images: %d , picsize: %d' % (magicnum, imgcnt, picsize) )
        
        offset += calcsize(fmt_header)
        fmt_image = '>' + str(picsize) + 'B'
        images = np.empty((imgcnt, rows, cols))
        for i in range(imgcnt):
            images[i] = np.array(unpack_from(fmt_image, fc, offset)).reshape((rows, cols))
            offset += calcsize(fmt_image)
        return images


class idx1_ubyte(object):
    def decode(self,idx1_ubyte_file):        
        bin_data = ungzip(idx1_ubyte_file)
        offset = 0
        fmt_header = '>ii'
        magicnum, imgcnt = unpack_from(fmt_header, bin_data, offset)
        offset += calcsize(fmt_header)
        fmt_image = '>B'
        labels = np.empty(imgcnt)
        for i in range(imgcnt):
            labels[i] = unpack_from(fmt_image, bin_data, offset)[0]
            offset += calcsize(fmt_image)
        return labels            
        
    def encode(self,):
        pass
    

if __name__ == "__main__":
    idx1 = idx1_ubyte()
    #labels = idx1.decode('MNIST_data/t10k-labels-idx1-ubyte.gz')
    labels = idx1.decode('MNIST_data/train-labels-idx1-ubyte.gz')
    idx3 = idx3_ubyte()
    images = idx3.decode('MNIST_data/train-images-idx3-ubyte.gz')    
    for i in range(10):
        print ( labels[i] )
        plt.imshow( images[i],cmap='gray' ) 
        plt.show()
    
    