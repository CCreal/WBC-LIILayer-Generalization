import math
import torch
import torch.nn as nn
import torch.nn.functional as F


def gaussian_filters(scale, gpu, k=3):
    std = torch.pow(2,scale)
    filtersize = torch.ceil(k*std+0.5)
    x = torch.arange(start=-filtersize.item(), end=filtersize.item()+1)
    if gpu is not None: x = x.cuda(gpu); std = std.cuda(gpu)
    x = torch.meshgrid([x,x])
    g = torch.exp(-(x[0]/std)**2/2)*torch.exp(-(x[1]/std)**2/2)
    g = g / torch.sum(g)  # Normalize
    dgdx = -x[0]/(std**3*2*math.pi)*torch.exp(-(x[0]/std)**2/2)*torch.exp(-(x[1]/std)**2/2)
    dgdx = dgdx / torch.sum(torch.abs(dgdx))  # Normalize
    dgdy = -x[1]/(std**3*2*math.pi)*torch.exp(-(x[1]/std)**2/2)*torch.exp(-(x[0]/std)**2/2)
    dgdy = dgdy / torch.sum(torch.abs(dgdy))  # Normalize
    basis_filter = torch.stack([g,dgdx,dgdy], dim=0)[:,None,:,:]

    return basis_filter


eps = 1e-5

def E_inv(E,Ex,Ey,El,Elx,Ely,Ell,Ellx,Elly):
    E = Ex**2+Ey**2+Elx**2+Ely**2+Ellx**2+Elly**2
    return E

def W_inv(E,Ex,Ey,El,Elx,Ely,Ell,Ellx,Elly):
    Wx = Ex/(E+eps)
    Wlx = Elx/(E+eps)
    Wllx = Ellx/(E+eps)
    Wy = Ey/(E+eps)
    Wly = Ely/(E+eps)
    Wlly = Elly/(E+eps)

    W = Wx**2+Wy**2+Wlx**2+Wly**2+Wllx**2+Wlly**2
    return W


inv_switcher = {
    'E': E_inv,
    'W': W_inv}

class IIILayer(nn.Module):
    def __init__(self, invariant='W', k=3, scale=0.0):

        super(IIILayer, self).__init__()
        assert invariant in ['E','W'], 'invalid invariant'
        self.inv_function = inv_switcher[invariant]

        self.use_cuda = torch.cuda.is_available()
        self.gpu = torch.cuda.current_device() if self.use_cuda else None

        self.gcm = torch.tensor([[0.06,0.63,0.27],[0.3,0.04,-0.35],[0.34,-0.6,0.17]])
        if self.use_cuda: self.gcm = self.gcm.cuda(self.gpu)
        self.k = k

        self.scale = torch.nn.Parameter(torch.tensor([scale]), requires_grad=True)

    def forward(self, batch):
        # Make sure scale does not explode: clamp to max abs value of 2.5
        self.scale.data = torch.clamp(self.scale.data, min=-2.5, max=2.5)

        # Measure E, El, Ell by Gaussian color model
        in_shape = batch.shape  # bchw
        batch = batch.view((in_shape[:2]+(-1,)))  # flatten image
        batch = torch.matmul(self.gcm,batch)  # estimate E,El,Ell
        batch = batch.view((in_shape[0],)+(3,)+in_shape[2:])  # reshape to original image size
        E, El, Ell = torch.split(batch, 1, dim=1)
        # Convolve with Gaussian filters
        w = gaussian_filters(scale=self.scale, gpu=self.gpu)  # KCHW

        # the padding here works as "same" for odd kernel sizes
        E_out = F.conv2d(input=E, weight=w, padding=int(w.shape[2]/2))
        El_out = F.conv2d(input=El, weight=w, padding=int(w.shape[2]/2))
        Ell_out = F.conv2d(input=Ell, weight=w, padding=int(w.shape[2]/2))

        E, Ex, Ey = torch.split(E_out,1,dim=1)
        El, Elx, Ely = torch.split(El_out,1,dim=1)
        Ell, Ellx, Elly = torch.split(Ell_out,1,dim=1)

        LIILayer_out = self.inv_function(E,Ex,Ey,El,Elx,Ely,Ell,Ellx,Elly)
        LIILayer_out = F.instance_norm(torch.log(LIILayer_out+eps))
        LIILayer_out = LIILayer_out.repeat(1,3,1,1)
        
        return LIILayer_out