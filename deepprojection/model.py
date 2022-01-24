#!/usr/bin/env python
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn


class SiameseConfig:
    alpha   = 0.5
    size_y  = None
    size_x  = None
    dim_emb = 32
    isbias  = True

    def __init__(self, **kwargs):
        # Set values of attributes that are not known when obj is created
        for k, v in kwargs.items():
            setattr(self, k, v)


class SPIImgEncoder(nn.Module):

    def __init__(self, dim_img, dim_emb = 32, isbias = True):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Linear(dim_img, dim_emb, isbias),
            nn.ReLU(inplace = True),
            nn.Sigmoid()
        )


    def encode(self, x):
        x = self.conv(x)

        return x


class Siamese(nn.Module):
    """ Embedding independent triplet loss. """

    def __init__(self, config):
        super().__init__()
        self.alpha     = config.alpha
        size_y, size_x = config.size_y, config_size_x
        dim_emb        = config.dim_emb
        isbias         = config.isbias

        dim_img = size_y * size_x
        self.encoder = SPIImgEncoder(dim_img, dim_emb, isbias)


    def forward(self, img_anchor, img_pos, img_neg):
        # Encode images
        img_anchor_embed = self.encoder.encode(img_anchor)
        img_pos_embed    = self.encoder.encode(img_pos)
        img_neg_embed    = self.encoder.encode(img_neg)

        # Calculate the RMSD between anchor and positive
        img_diff = img_anchor_embed - img_pos_embed
        rmsd_anchor_pos = torch.sqrt( torch.mean(img_diff * img_diff) )

        # Calculate the RMSD between anchor and negative
        img_diff = img_anchor_embed - img_neg_embed
        rmsd_anchor_neg = torch.sqrt( torch.mean(img_diff * img_diff) )

        # Calculate the triplet loss
        loss_triplet = max(rmsd_anchor_pos - rmsd_anchor_neg + self.alpha, 0)

        return loss_triplet


    def configure_optimizers(self, config_train):
        optimizer = torch.optim.Adam(self.encoder.parameters(), lr = config_train.lr)

        return optimizer


