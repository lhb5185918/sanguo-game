#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成默认背景图片脚本
这个脚本会创建一个简单的背景图片，用于测试游戏
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_default_background():
    """创建一个简单的背景图片"""
    # 创建一个深蓝色背景
    img = Image.new('RGB', (1280, 720), (20, 20, 50))
    draw = ImageDraw.Draw(img)
    
    # 添加一些装饰线条
    for i in range(0, 1280, 50):
        opacity = int(255 * (0.2 + 0.1 * (i % 3)))
        draw.line([(i, 0), (i, 720)], fill=(255, 255, 255, opacity), width=1)
    
    for i in range(0, 720, 50):
        opacity = int(255 * (0.2 + 0.1 * (i % 3)))
        draw.line([(0, i), (1280, i)], fill=(255, 255, 255, opacity), width=1)
    
    # 尝试加载字体
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("simhei.ttf", 60)
        title_font = ImageFont.truetype("simhei.ttf", 120)
    except IOError:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # 添加标题
    draw.text((640, 200), "三国霸业", fill=(255, 215, 0), font=title_font, anchor="mm")
    
    # 添加副标题
    draw.text((640, 320), "群雄逐鹿 天下三分", fill=(255, 255, 255), font=font, anchor="mm")
    
    # 保存图片
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
    img.save("resources/background.jpg")
    print("背景图片已创建: resources/background.jpg")

if __name__ == "__main__":
    create_default_background() 