import matplotlib.pyplot as plt
import numpy as np
# 将根目录（execute所在目录）添加到环境变量
from utils.GlobalVar import add_path_to_sys
rootdir = add_path_to_sys()

# 800 x 600
plt.figure(figsize=(8, 6), dpi=200, facecolor='black')

# img = np.full((800, 600, 3), (255, 255, 255), np.uint8)
img1 = np.full((900, 700, 3), (0, 0, 0), np.uint8)
plt.savefig(f'{rootdir}/logo_imgs/bkg1.png', dpi=200)

img2 = np.full((500, 400, 3), (0, 0, 0), np.uint8)
plt.savefig(f'{rootdir}/logo_imgs/bkg2.png', dpi=200)

# plt.imshow(img1)
# plt.show(img1)
