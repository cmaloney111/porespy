import scipy as sp
import scipy.ndimage as spim

class ChordLengthDistribution(object):
       
    def xdir(self,image,spacing=10,trim_edges=True):
        r'''
        '''
        temp = self._distribution(image=image,spacing=spacing,trim_edges=trim_edges)
        return temp

    def ydir(self,image,spacing=10,trim_edges=True):
        r'''
        '''
        image = sp.transpose(image,[1,0,2])
        temp = self._distribution(image=image,spacing=spacing,trim_edges=trim_edges)
        return temp
        
    def zdir(self,image,spacing=10,trim_edges=True):
        r'''
        '''
        image = sp.transpose(image,[2,1,0])
        temp = self._distribution(image=image,spacing=spacing,trim_edges=trim_edges)
        return temp
        
    def ndir(self,image,spacing=10,rotation=0,trim_edges=True):
        r'''
        '''
        image = spim.rotate(image,axes=[1,2],angle=rotation)
        temp = self._distribution(image=image,spacing=spacing,trim_edges=trim_edges)
        return temp
        
    def _apply_chords(self,img,spacing=10,trim_edges=True):
        r'''
        '''
        # Clean up input image
        img = sp.atleast_3d(img)
        # Extract size metrics from input image
        [Lx, Ly, Lz] = sp.shape(img)
        start = sp.array(sp.floor(spacing/2),dtype=int)
        Y = sp.arange(start,Ly,spacing)
        Z = sp.arange(start,Lz,spacing)
        temp = sp.zeros([Lx,Ly,Lz],dtype=int)
        # Generate 2D mask of chords in X-dir
        maskX = sp.zeros([Lx,Ly,1],dtype=bool)
        maskX[:,Y,:] = 1
        # Apply chord mask to specified layers (Z-dir) of input image
        temp[:,:,Z] = img[:,:,Z]*maskX
        if trim_edges:
            temp[[0,-1],:,:] = 1 
            temp[:,[0,-1],:] = 1
            spim.label(temp)
            ind = sp.where(temp==temp[0,0,0])
            temp[ind] = 0
            
        return sp.array(temp,dtype=int)
        
    def _distribution(self,image,spacing,rotation=0,trim_edges=True):
        r'''
        '''
        # Clean up input image
        img = sp.array(image,ndmin=3,dtype=int)
        # Extract size metrics from input image
        [Lx, Ly, Lz] = sp.shape(img)
        start = sp.array(sp.floor(spacing/2),dtype=int)
        Y = sp.arange(start,Ly,spacing)
        Z = sp.arange(start,Lz,spacing)
        [y,z] = sp.meshgrid(Y,Z,indexing='ij')
        y = y.flatten()
        z = z.flatten()
        bins = sp.zeros(sp.amax(sp.shape(img))+1,dtype=int)
        for yi,zi in zip(y,z):
            a = self._find_blocks(img[:,yi,zi],trim_edges=trim_edges)
            bins[a['length']] += 1
        return bins
        
    def _find_blocks(self,array,trim_edges=False):
        array = sp.clip(array,a_min=0,a_max=1)
        temp = sp.pad(array,pad_width=1,mode='constant',constant_values=0)
        end_pts = sp.where(sp.ediff1d(temp)==-1)[0] # Find 1->0 transitions
        end_pts -= 1  # To adjust for 0 padding
        seg_len = sp.cumsum(array)[end_pts]
        seg_len[1:] = seg_len[1:] - seg_len[:-1]
        start_pts = end_pts - seg_len + 1
        a = dict()
        a['start'] = start_pts
        a['end'] = end_pts
        a['length'] = seg_len
        if trim_edges:
            if (a['start'].size > 0) and (a['start'][0] == 0):
                [a.update({item:a[item][1:]}) for item in a]
            if (a['end'].size > 0) and (a['end'][-1] == sp.size(array)-1):
                [a.update({item:a[item][:-1]}) for item in a]
        return a