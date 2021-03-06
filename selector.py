#!/usr/bin/python
# -*- encoding: utf-8 -*-


import torch
import numpy as np


class BatchHardTripletSelector(object):
    '''
    a selector to generate hard batch embeddings from the embedded batch
    '''
    def __init__(self, *args, **kwargs):
        super(BatchHardTripletSelector, self).__init__()

    def __call__(self, embeds, labels):
        dist_mtx = self.pdist(embeds, embeds).detach().cpu().numpy()
        labels = labels.contiguous().cpu().numpy().reshape((-1, 1))
        num = labels.shape[0]
        lb_eqs = labels == labels.T
        pos_idxs = []
        neg_idxs = []
        for i in range(num):
            dist_min, dist_max = dist_mtx[i][0], dist_mtx[i][0]
            id_min, id_max = 0, 0
            ## TODO: reimplement this with c++ to avoid overhead of python loop
            for j in range(num):
                if labels[i] == labels[j]:
                    if i != j:
                        if dist_mtx[i][j] > dist_max:
                            dist_max = dist_mtx[i][j]
                            id_max = j
                else:
                    if dist_mtx[i][j] < dist_min:
                        dist_min = dist_mtx[i][j]
                        id_min = j
            pos_idxs.append(id_max)
            neg_idxs.append(id_min)
        neg_idxs = np.array(neg_idxs).reshape((-1, 1))
        pos_idxs = np.array(pos_idxs).reshape((-1, 1))
        pos = embeds[pos_idxs].contiguous().view(num, -1)
        neg = embeds[neg_idxs].contiguous().view(num, -1)
        return embeds, pos, neg


    def pdist(self, ten1, ten2):
        m, n = ten1.shape[0], ten2.shape[0]
        ten1_pow = torch.pow(ten1, 2).sum(dim = 1, keepdim = True).expand((m, n))
        ten2_pow = torch.pow(ten2, 2).sum(dim = 1, keepdim = True).expand((n, m)).t()
        dist_mtx = ten1_pow + ten2_pow
        dist_mtx = dist_mtx.addmm_(1, -2, ten1, ten2.t())
        dist_mtx = dist_mtx.clamp(min = 1e-12).sqrt()
        return dist_mtx

if __name__ == '__main__':
    pass
