#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
三国霸业游戏启动脚本
"""

import os
import sys
import subprocess

def check_requirements():
    """检查并安装必要的库"""
    print("检查依赖库...")
    try:
        import arcade
        import PIL
        print("依赖库已安装")
    except ImportError:
        print("正在安装依赖库...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖库安装完成")

def setup_resources():
    """设置游戏资源"""
    print("设置游戏资源...")
    # 创建资源目录
    if not os.path.exists("resources"):
        os.makedirs("resources")
    
    # 如果不存在背景图，生成一个默认背景
    if not os.path.exists("resources/background.jpg"):
        print("正在生成默认背景图...")
        try:
            from resources.default_background import create_default_background
            create_default_background()
        except Exception as e:
            print(f"背景图生成失败: {e}")
            # 提示用户手动添加背景图
            print("请手动将背景图片放置到resources/background.jpg")

def main():
    """主函数"""
    print("=" * 50)
    print("欢迎来到【三国霸业】")
    print("=" * 50)
    
    # 检查依赖
    check_requirements()
    
    # 设置资源
    setup_resources()
    
    # 检查gui目录
    if not os.path.exists("gui"):
        os.makedirs("gui")
        # 创建__init__.py确保gui可以作为包导入
        with open("gui/__init__.py", "w") as f:
            f.write("# GUI包初始化文件\n")
    
    # 启动游戏
    print("启动游戏...")
    try:
        from three_kingdoms_arcade import main
        main()
    except Exception as e:
        print(f"游戏启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main() 