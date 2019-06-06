import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import skimage


def gray_enhance(img, num):
    """图像转灰度，亮度、对比度变换

    Args:
        img(PIL.Image): 图像
        num(int): 返回变换图像数量

    Returns:
        list: (transformed_imgs) 变换后图像
    """
    # RGB转灰度
    img = img.convert('L')

    # 随机变换
    transformed_imgs = []
    for i in range(num):
        # 亮度调整上下界
        brightness_low_factor = 0.5
        brightness_high_factor = 1.5
        enhance_brightness = ImageEnhance.Brightness(img)
        brightness = random.uniform(brightness_low_factor, brightness_high_factor)
        bright_img = enhance_brightness.enhance(brightness)

        # 对比度调整上下界
        contrast_low_factor = 0.5
        contrast_high_factor = 1.5
        enhance_contrast = ImageEnhance.Contrast(bright_img)
        contrast = random.uniform(contrast_low_factor, contrast_high_factor)
        contrast_img = enhance_contrast.enhance(contrast)

        transformed_imgs.append(contrast_img)

    return transformed_imgs


def mosaic(img, num):
    """图像随机部分加大小随机马赛克

    Args:
        img(PIL.Image): 图像
        num(int): 返回变换图像数量

    Returns:
        list: (transformed_imgs) 变换后图像
    """
    transformed_imgs = []
    width, height = img.size
    img = np.array(img)
    for i in range(num):
        # 随机马赛克块大小
        mosaic_block_size = random.randint(5, 20)

        # 随机马赛克位置
        start_x = random.randint(0, height - 5 * mosaic_block_size)
        end_x = random.randint(start_x + 5 * mosaic_block_size, height)
        start_y = random.randint(0, width - 5 * mosaic_block_size)
        end_y = random.randint(start_y + 5 * mosaic_block_size, width)

        mosaiced_img = img.copy()
        for x in range(start_x, end_x - mosaic_block_size, mosaic_block_size):
            for y in range(start_y, end_y - mosaic_block_size, mosaic_block_size):
                try:
                    mosaiced_img[x: x + mosaic_block_size, y: y + mosaic_block_size] = \
                    mosaiced_img[x + (mosaic_block_size // 2)][y + (mosaic_block_size // 2)]
                except IndexError:
                    print('width: {} height: {}'.format(width, height))
                    print('start_x: {} end_x: {}\nstart_y: {} end_y: {}'.format(start_x, end_x, start_y, end_y))
                    print('block_size: {}'.format(mosaic_block_size))
                    print('x: {}-{}'.format(x, x + mosaic_block_size))
                    print('y: {}-{}'.format(y, y + mosaic_block_size))
                    return
        transformed_imgs.append(Image.fromarray(mosaiced_img.astype('uint8')))

    return transformed_imgs


def resize_flip(img, num):
    """图像随机缩放加翻转

    Args:
        img(PIL.Image): 图像
        num(int): 返回变换图像数量

    Returns:
        list: (transformed_imgs) 变换后图像
    """
    transformed_imgs = []
    width, height = img.size

    for i in range(num):
        # 缩放比例
        scale_factor_width = random.uniform(0.5, 0.9)
        scale_factor_height = random.uniform(0.5, 0.9)
        resized_img = img.resize(
            (int(width * scale_factor_width),
             int(height * scale_factor_height)),
            Image.ANTIALIAS,
        )

        # 翻转
        flipped_img = resized_img
        left_to_right = random.randint(0, 1)
        top_to_bottom = random.randint(0, 1)

        if left_to_right:
            flipped_img = resized_img.transpose(Image.FLIP_LEFT_RIGHT)

        if top_to_bottom:
            flipped_img = flipped_img.transpose(Image.FLIP_TOP_BOTTOM)

        transformed_imgs.append(flipped_img)

    return transformed_imgs


def noise(img, num):
    """图像随机添加高斯白噪声和椒盐噪声

    Args:
        img(PIL.Image): 图像
        num(int): 返回变换图像数量

    Returns:
        list: (transformed_imgs) 变换后图像
    """
    transformed_imgs = []

    for i in range(num):
        noised_img = np.array(img)

        # 添加白噪声，椒盐噪声
        noised_img = skimage.util.random_noise(noised_img, mode='gaussian', seed=random.randint(0, 8888))
        noised_img = skimage.util.random_noise(noised_img, mode='s&p', seed=random.randint(0, 8888))

        # 转成PIL.Image
        noised_img = Image.fromarray((noised_img * 255).astype('uint8'))

        transformed_imgs.append(noised_img)

    return transformed_imgs


def picture_in_picture(img, num, base_dir='src'):
    """图像画中画，占比原图1/4~1/2

    Args:
        img(PIL.Image): 图像
        num(int): 返回变换图像数量
        base_dir(str): 图像目录

    Returns:
        list: (transformed_imgs) 变换后图像
    """
    transformed_imgs = []

    for i in range(num):
        filename = os.listdir(base_dir)

        # 随机挑一张图像作为背景
        backgroud = np.random.choice(filename)
        backgroud_img = Image.open(os.path.join(base_dir, backgroud))
        backgroud_width, backgroud_height = backgroud_img.size

        # 图像放缩后大小占比1/4~1/2
        resized_width = int(random.uniform(backgroud_width * 1 / 4, backgroud_width * 1 / 2))
        resized_height = int(random.uniform(backgroud_height * 1 / 4, backgroud_height * 1 / 2))

        # 图像放缩，旋转
        width, height = img.size
        resized_img = img.resize(
            (resized_width,
             resized_height),
            Image.ANTIALIAS,
        )
        # rotated_img = resized_img.rotate(random.randint(0, 180))
        # 旋转后黑边问题未解决
        rotated_img = resized_img

        # 粘贴到背景图中
        start_x = random.randint(backgroud_height // 4, backgroud_height // 2)
        start_y = random.randint(backgroud_width // 4, backgroud_width // 2)
        backgroud_img.paste(rotated_img, (start_x, start_y))
        transformed_imgs.append(backgroud_img)

    return transformed_imgs


def watermark(img, num):
    """图片加水印

    Args:
        img(PIL.Image): 图像
        num(int): 返回变换图像数量

    Returns:
        list: (transformed_imgs) 变换后图像
    """
    transformed_imgs = []
    width, height = img.size

    for i in range(num):
        # 水印位置随机
        start_x = random.randint(height // 8, height // 8 * 7)
        start_y = random.randint(width // 8, width // 8 * 7)

        # 水印内容随机
        content_length = random.randint(1, 10)
        content = random.sample('zyxwvutsrqponmlkjihgfedcba', content_length)

        watermarked_img = img.copy()
        watermarked_img = watermarked_img.convert('RGBA')
        fnt = ImageFont.truetype("/usr/share/fonts/type1/gsfonts/n021003l.pfb", 40)
        txt = Image.new('RGBA', watermarked_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt)
        draw.text((txt.size[0] - 115, txt.size[1] - 80), "cnBlogs", font=fnt, fill=(255, 255, 255, 255))
        watermarked_img = Image.alpha_composite(watermarked_img, txt)

        transformed_imgs.append(watermarked_img)

    return transformed_imgs


if __name__ == "__main__":
    base_dir = 'src'
    out_dir = 'out'
    num = 10

    for file in os.listdir(base_dir):
        pic_id, pic_type = file.split('.')
        pic_id = pic_id.split('_')[0]

        img = Image.open(os.path.join(base_dir, file))

        transformed_list = gray_enhance(img, num)
        for i, transformed_img in enumerate(transformed_list):
            transformed_img.save(os.path.join(out_dir, pic_id + '_grayenhance_{}.'.format(i) + pic_type))

        transformed_list = mosaic(img, num)
        for i, transformed_img in enumerate(transformed_list):
            transformed_img.save(os.path.join(out_dir, pic_id + '_mosaic_{}.'.format(i) + pic_type))

        transformed_list = resize_flip(img, num)
        for i, transformed_img in enumerate(transformed_list):
            transformed_img.save(os.path.join(out_dir, pic_id + '_resizeflip_{}.'.format(i) + pic_type))

        transformed_list = noise(img, num)
        for i, transformed_img in enumerate(transformed_list):
            transformed_img.save(os.path.join(out_dir, pic_id + '_noise_{}.'.format(i) + pic_type))

        transformed_list = picture_in_picture(img, num, base_dir=base_dir)
        for i, transformed_img in enumerate(transformed_list):
            transformed_img.save(os.path.join(out_dir, pic_id + '_pictureinpicture_{}.'.format(i) + pic_type))

