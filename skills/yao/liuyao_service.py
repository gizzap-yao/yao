#!/usr/bin/env python3
"""
六爻占卜服务客户端
提供 /divine、/divine/chat、/notice 三个接口
"""
import json
import os
from typing import List, Dict, Any

import httpx

BASE_URL = "http://yao.gizzap.com"
API_KEY_FILE = os.path.expanduser("~/.liuyao_key")


def check_api_key() -> bool:
    """检查 API Key 是否存在"""
    return os.path.exists(API_KEY_FILE)


def load_api_key() -> str:
    """从 ~/.liuyao_key 文件加载 API Key"""
    api_key = ""
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            api_key = f.read().strip()
            return api_key
    raise FileNotFoundError(f"未找到 API Key 文件 {API_KEY_FILE}")


def get_headers() -> Dict[str, str]:
    """获取请求头"""
    return {
        "Content-Type": "application/json",
        "X-API-Key": load_api_key()
    }


def divine(numbers: List[int], category: str = "综合", matter: str = "数字起卦") -> Dict[str, Any]:
    """
    调用起卦接口 /divine

    Args:
        numbers: 数字列表，建议3-5个数字
        category: 占卜类别，可选值：综合、感情、事业、财富、健康、出行
        matter: 占卜事项描述

    Returns:
        排盘结果，包含卦象信息和解读
    """
    if not check_api_key():
        raise FileNotFoundError(f"未找到 API Key 文件 {API_KEY_FILE}")
    payload = {
        "numbers": numbers,
        "category": category,
        "matter": matter
    }

    with httpx.Client(timeout=600.0) as client:
        response = client.post(
            f"{BASE_URL}/divine",
            headers=get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()


def divine_chat(question: str) -> Dict[str, Any]:
    """
    调用聊天接口 /divine/chat

    Args:
        question: 用户问题

    Returns:
        回复结果
    """
    if not check_api_key():
        raise FileNotFoundError(f"未找到 API Key 文件 {API_KEY_FILE}")
    payload = {
        "question": question
    }

    with httpx.Client(timeout=600.0) as client:
        response = client.post(
            f"{BASE_URL}/divine/chat",
            headers=get_headers(),
            json=payload
        )
        response.raise_for_status()
        return response.json()


def notice() -> Dict[str, Any]:
    """
    调用消息接口 /notice

    Returns:
        发送结果
    """
    with httpx.Client(timeout=600.0) as client:
        response = client.get(
            f"{BASE_URL}/notice"
        )
        response.raise_for_status()
        return response.json()


def get_categories() -> Dict[str, Any]:
    """
    调用查询占卜类型接口 /categories

    Returns:
        支持的占卜类型列表
    """
    if not check_api_key():
        raise FileNotFoundError(f"未找到 API Key 文件 {API_KEY_FILE}")

    with httpx.Client(timeout=600.0) as client:
        response = client.get(
            f"{BASE_URL}/categories",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    # 测试示例
    import argparse

    parser = argparse.ArgumentParser(description="六爻占卜服务客户端")
    subparsers = parser.add_subparsers(dest="command", help="可用指令")

    # divine 指令
    divine_parser = subparsers.add_parser("divine", help="起卦")
    divine_parser.add_argument("-n", "--numbers", type=str, help="数字列表，逗号分隔，例如：33,6,86")
    divine_parser.add_argument("-c", "--category", type=str, default="综合", help="占卜类别")
    divine_parser.add_argument("-m", "--matter", type=str, default="数字起卦", help="占卜事项")

    # chat 指令
    chat_parser = subparsers.add_parser("chat", help="问答")
    chat_parser.add_argument("-q", "--question", type=str, help="问题")

    # notice 指令
    notice_parser = subparsers.add_parser("notice", help="发送消息")
    notice_parser.add_argument("-k", "--key", type=str, help="从返回结果中提取指定字段的值")

    # check_api_key 指令
    check_parser = subparsers.add_parser("check_api_key", help="检查 API Key 是否存在")
    check_parser.set_defaults(command="check_api_key")

    # category 指令
    category_parser = subparsers.add_parser("category", help="查询支持的占卜类型")
    category_parser.set_defaults(command="category")

    args = parser.parse_args()

    if args.command == "divine":
        numbers = []
        if args.numbers:
            numbers = [int(n.strip()) for n in args.numbers.split(",")]
        if not numbers:
            print("请输入数字列表！")
            exit(1)
        category = args.category
        matter = args.matter
        result = divine(numbers, category, matter)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "chat":
        question = args.question
        if not question:
            print("请输入问题！")
            exit(1)
        result = divine_chat(question)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "notice":
        result = notice()
        if args.key:
            print(result.get(args.key, ""))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "check_api_key":
        if check_api_key():
            print(f"API Key 文件存在: {API_KEY_FILE}")
        else:
            print(f"API Key 文件不存在: {API_KEY_FILE}")
    elif args.command == "category":
        result = get_categories()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
