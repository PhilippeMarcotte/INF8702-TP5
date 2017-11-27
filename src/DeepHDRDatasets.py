from torch.utils.data.dataset import Dataset
import numpy as np
import os
import torch
import math
import torchvision.transforms as transforms
import ModelsConstants

class DeepHDRScenes(Dataset):
    def __init__(self, root):
        self.root = os.path.join(root, '')

        self.num_patches = 10*49*74
        
    def __getitem__(self, index):
        scene = math.floor(index/self.num_patches)

        scene_labels = np.fromfile(os.path.join(self.root, str(scene), "label"), dtype='uint8')
        scene_labels = np.reshape(scene_labels, (self.num_patches, 3, 40, 40))
        scene_labels = np.squeeze(scene_labels)        
        
        scene_imgs = np.fromfile(os.path.join(self.root, str(scene), "imgs"), dtype='uint8')
        scene_imgs = scene_imgs.reshape((self.num_patches, 18, 40, 40))
        scene_imgs = np.squeeze(scene_imgs)

        return (scene_imgs, scene_labels)

    def __len__(self):
        return sum(os.path.isdir(self.root + i) for i in os.listdir(self.root))

class DeepHDRPatches(Dataset):
    def __init__(self, scene_imgs, scene_labels):
        self.scene_imgs = scene_imgs
        self.scene_labels = scene_labels
        self.label_transforms = transforms.Compose([
                        transforms.ToPILImage(),
                        transforms.CenterCrop(ModelsConstants.cnn_ouput_size),
                        transforms.ToTensor(),
                        transforms.Lambda(lambda crop: crop.renorm(1, 0, 255))
                        ])
    
    def __getitem__(self, index):
        imgs = self.scene_imgs[index].float().renorm(1, 0, 255)

        label = self.scene_labels[index]
        label = self.label_transforms(label)
        return (imgs, label)

    def __len__(self):
        return self.scene_imgs.shape[0]