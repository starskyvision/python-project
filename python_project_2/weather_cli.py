#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import requests
import argparse
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
# 如果当前目录有 .env 文件，它会自动加载其中的变量到 os.environ
load_dotenv()


def get_api_key(cli_key):
    """
    获取 API Key 的逻辑优先级：
    1. 命令行参数 --key (最高优先级)
    2. 环境变量 AMAP_API_KEY (来自 .env 或系统设置)
    3. 无 (返回 None)
    """
    if cli_key:
        return cli_key

    env_key = os.getenv("AMAP_API_KEY")
    if env_key:
        return env_key

    return None


def get_weather_data(city, api_key, extensions='base'):
    """调用高德天气API"""
    base_url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params = {
        'city': city,
        'key': api_key,
        'extensions': extensions,
        'output': 'json'
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == '1':
            return data
        else:
            return {'error': data.get('info', '未知错误')}

    except requests.exceptions.RequestException as e:
        return {'error': f'网络请求失败: {str(e)}'}


def format_output(data, extensions):
    """格式化输出天气信息"""
    if 'error' in data:
        print(f"\n查询失败: {data['error']}\n")
        return

    lives = data.get('lives', [])
    forecasts = data.get('forecasts', [])

    # 输出实况
    if lives:
        live = lives[0]
        print("\n" + "=" * 40)
        print(f"地区：{live.get('province')}{live.get('city')}")
        print("-" * 40)
        print(f"温度：{live.get('temperature')}°C")
        print(f"天气：{live.get('weather')}")
        print(f"风向：{live.get('winddirection')}风")
        print(f"风力：{live.get('windpower')}级")
        print(f"湿度：{live.get('humidity')}%")
        print(f"时间：{live.get('reporttime')}")
        print("=" * 40)
    else:
        print("未获取到实况数据。")

    # 输出预报
    if extensions == 'all' and forecasts:
        print(f"\n{forecasts[0].get('city')} 未来预报:")
        print("-" * 40)
        for day in forecasts[0].get('casts', []):
            print(f"[{day.get('date')} {day.get('week')}]")
            print(
                f"白天：{day.get('dayweather')} {day.get('daytemp')}°C ({day.get('daywind')}{day.get('daypower')}级)")
            print(f"晚上：{day.get('nightweather')} {day.get('nighttemp')}°C")
        print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="高德地图 CLI 天气查询工具",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="示例:\n  python weather_cli.py 北京\n  python weather_cli.py 上海 --extensions all"
    )

    parser.add_argument('city', type=str, help='城市名称 (例如: 北京, 杭州)')
    parser.add_argument('--key', '-k', type=str, default=None,
                        help='API Key (优先级高于 .env 文件)')
    parser.add_argument('--extensions', '-e', type=str, choices=['base', 'all'],
                        default='base', help='base: 实况 (默认); all: 实况+预报')

    args = parser.parse_args()

    # 获取 Key
    api_key = get_api_key(args.key)

    if not api_key:
        print("\n错误：未找到 API Key!")
        print("解决方法:")
        print("  1. 在项目根目录创建 .env 文件，写入: AMAP_API_KEY=你的Key")
        print("  2. 或者在命令中添加参数: --key 你的Key")
        print("  3. 或者在系统环境变量中设置 AMAP_API_KEY")
        sys.exit(1)

    print(f"正在查询 [{args.city}] ...")
    data = get_weather_data(args.city, api_key, args.extensions)
    format_output(data, args.extensions)


if __name__ == "__main__":
    main()