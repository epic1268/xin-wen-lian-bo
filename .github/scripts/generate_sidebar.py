#!/usr/bin/env python3
"""生成 docsify 侧边栏 _sidebar.md。配置直接通过 --config-json 传入 JSON 字符串。"""

import argparse
import json
import os

def should_include(name, is_dir, config):
    """根据配置判断是否包含该文件/目录。"""
    if is_dir and 'include_dirs' in config:
        if name in config['include_dirs']:
            return True
    if not is_dir and 'include_files' in config:
        if name in config['include_files']:
            return True

    if is_dir and 'exclude_dirs' in config:
        if name in config['exclude_dirs']:
            return False
    if not is_dir and 'exclude_files' in config:
        if name in config['exclude_files']:
            return False

    # 默认排除隐藏文件/文件夹和 _sidebar.md 自身
    if name.startswith('.') or name == '_sidebar.md':
        return False

    return True

def generate_auto_sidebar(root, config, title):
    """自动扫描目录生成 Markdown 列表。"""
    lines = []
    if title:
        lines.append(f"# {title}\n")

    try:
        items = sorted(os.listdir(root), reverse=True)
    except FileNotFoundError:
        return f"# 错误：目录 '{root}' 不存在\n"

    dirs = [d for d in items if os.path.isdir(os.path.join(root, d)) and should_include(d, True, config)]
    files = [f for f in items if os.path.isfile(os.path.join(root, f)) and should_include(f, False, config)]

    for d in dirs:
        entry = f""
        # entry = f"- [{d}]({d}/README.md)"
        lines.append(entry)
        # 递归一级子目录
        try:
            sub_items = sorted(os.listdir(os.path.join(root, d)), reverse=True)
        except PermissionError:
            continue
        for sub in sub_items:
            sub_path = os.path.join(root, d, sub)
            if os.path.isfile(sub_path) and sub.endswith('.md') and sub != 'README.md':
                if should_include(sub, False, config):
                    lines.append(f"  - [{sub[:-3]}]({sub})")

    for f in files:
        if f.endswith('.md'):
            name = f[:-3]
            lines.append(f"- [{name}]({f})")

    return '\n'.join(lines) + '\n'

def generate_custom_sidebar(custom_structure, title):
    """使用用户自定义结构生成侧边栏。"""
    lines = []
    if title:
        lines.append(f"# {title}\n")
    for item in custom_structure:
        if isinstance(item, str):
            lines.append(item)
        elif isinstance(item, dict):
            t = item.get('title', '')
            p = item.get('path', '')
            lines.append(f"- [{t}]({p})")
        else:
            lines.append(str(item))
    return '\n'.join(lines) + '\n'

def main():
    parser = argparse.ArgumentParser(description='生成 docsify 侧边栏')
    parser.add_argument('--root', default='.', help='扫描根目录')
    parser.add_argument('--output', default='_sidebar.md', help='输出文件')
    parser.add_argument('--title', default='', help='侧边栏标题')
    parser.add_argument('--config-json', default='{}', help='配置 JSON 字符串')
    args = parser.parse_args()

    try:
        config = json.loads(args.config_json)
    except json.JSONDecodeError as e:
        print(f"❌ 配置 JSON 解析失败: {e}")
        config = {}

    if 'custom_sidebar' in config:
        content = generate_custom_sidebar(config['custom_sidebar'], args.title)
    else:
        content = generate_auto_sidebar(args.root, config, args.title)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 侧边栏已生成：{args.output}")

if __name__ == '__main__':
    main()
