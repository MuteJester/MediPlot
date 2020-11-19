import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import cm


class BodyMap:
    def __init__(self):
        self.body_sil = plt.imread('Body_Sil.png')
        self.bmap = {'head': self.set_head, 'legs': self.set_legs, 'les': self.set_right_leg,
                     'left leg': self.set_left_leg, 'right leg': self.set_right_leg, 'right arm': self.set_right_arm,
                     'left arm': self.set_left_arm, 'torso': self.set_torso, 'arms': self.set_arms,
                     'waist': self.set_waist,
                     'neck': self.set_neck, 'left hand': self.set_left_hand, 'right hand': self.set_right_hand,
                     'left foot': self.set_left_foot, 'right foot': self.set_right_foot}

    def list_of_targets(self):
        return ['head', 'legs', 'right leg', 'left leg', 'right arm', 'left arm', 'torso', 'arms', 'waist', 'neck',
                'left hand', 'right hand']

    def set_head(self, value):
        head = self.body_sil[0:270, 300:580]
        self.body_sil[0:270, 300:580] = np.where(head == [1, 1, 1], head, value)

    def set_neck(self, value):
        neck = self.body_sil[270:330, 300:580]
        self.body_sil[270:330, 300:580] = np.where(neck == [1, 1, 1], neck, value)

    def set_torso(self, value):
        torso = self.body_sil[330:965, 265:640]
        self.body_sil[330:965, 265:640] = np.where(torso == [1, 1, 1], torso, value)

    def set_waist(self, value):
        waist = self.body_sil[965:1155, 235:670]
        self.body_sil[965:1155, 235:670] = np.where(waist == [1, 1, 1], waist, value)

    def set_left_leg(self, value):
        right_leg = self.body_sil[1155:2290, 230:455]
        self.body_sil[1155:2290, 230:455] = np.where(right_leg == [1, 1, 1], right_leg, value)

    def set_right_leg(self, value):
        left_leg = self.body_sil[1155:2290, 455:685]
        self.body_sil[1155:2290, 455:685] = np.where(left_leg == [1, 1, 1], left_leg, value)

    def set_legs(self, value):
        self.set_right_leg(value)
        self.set_left_leg(value)

    def set_left_arm(self, value):
        right_arm = self.body_sil[380:1350, 0:235]
        self.body_sil[380:1350, 0:235] = np.where(right_arm == [1, 1, 1], right_arm, value)
        self.body_sil[380:1000, 0:265] = np.where(self.body_sil[380:1000, 0:265] == [1, 1, 1],
                                                  self.body_sil[380:1000, 0:265], value)

    def set_right_arm(self, value):
        right_arm = self.body_sil[870:1370, 682:1299]
        self.body_sil[870:1370, 682:1299] = np.where(right_arm == [1, 1, 1], right_arm, value)
        self.body_sil[385:940, 640:1289] = np.where(self.body_sil[385:940, 640:1289] == [1, 1, 1],
                                                    self.body_sil[385:940, 640:1289], value)

    def set_arms(self, value):
        self.set_left_arm(value)
        self.set_right_arm(value)

    def set_left_hand(self, value):
        left_hand = self.body_sil[1135:1400, 0:180]
        self.body_sil[1135:1400, 0:180] = np.where(left_hand == [1, 1, 1], left_hand, value)

    def set_right_hand(self, value):
        right_hand = self.body_sil[1135:1400, 760:907]
        self.body_sil[1135:1400, 760:907] = np.where(right_hand == [1, 1, 1], right_hand, value)

    def set_left_foot(self, value):
        left_foot = self.body_sil[2195:2289, 225:361]
        self.body_sil[2195:2289, 225:361] = np.where(left_foot == [1, 1, 1], left_foot, value)

    def set_right_foot(self, value):
        right_foot = self.body_sil[2195:2289, 540:690]
        self.body_sil[2195:2289, 540:690] = np.where(right_foot == [1, 1, 1], right_foot, value)

    def generate(self, areas, values, figsize=(9, 15), cmap='coolwarm', background='white'):
        self.f, self.ax = plt.subplots(figsize=figsize)
        self.ax.axis('off')
        norm = plt.Normalize(np.min(values), np.max(values))
        col_map = cm.get_cmap(cmap)
        for area, value in zip(areas, values):
            self.bmap[area.lower()](col_map(norm(value))[:3])

        if background == 'black':
            self.body_sil = np.where(self.body_sil == [1, 1, 1], [0, 0, 0], self.body_sil)

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes('right', size='10%', pad=0.5)
        x = self.ax.imshow(self.body_sil, cmap=cmap, vmin=np.min(values), vmax=np.max(values))
        self.f.colorbar(x, cax=cax, orientation='vertical')

        return self.ax

