#!/usr/bin/env python3
"""Split DeepSeek conversations.json into individual conversation files."""

import json
import os
import re
from pathlib import Path
from datetime import datetime

def create_title_slug(title):
    """Create a URL-safe slug from title."""
    if not title:
        return "untitled"
    # Remove/replace invalid characters
    slug = re.sub(r'[^\w\s-]', '', title)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:80]  # Limit length

def extract_turns(mapping):
    """
    Extract turns from conversation mapping.
    mapping is a dict with node_id -> {role, content, ...}
    Returns list of {role, content_text, timestamp}
    """
    turns = []

    # Build tree structure to sort by parent relationships
    nodes = {}
    for node_id, node in mapping.items():
        nodes[node_id] = {
            'id': node_id,
            'parent_id': node.get('parent_id'),
            'role': node.get('role'),
            'content': node.get('content', {}),
            'create_time': node.get('create_time'),
        }

    # Find root nodes (nodes with no parent or parent not in mapping)
    roots = []
    for node_id in nodes:
        parent_id = nodes[node_id]['parent_id']
        if parent_id is None or parent_id not in nodes:
            roots.append(node_id)

    # DFS traversal from roots to get ordered turns
    def traverse(node_id):
        node = nodes[node_id]
        role = node['role']

        # Only process user and assistant messages
        if role not in ['user', 'assistant']:
            return []

        result = []

        # Extract text content
        content = node['content']
        content_text = ''
        if isinstance(content, dict):
            parts = content.get('parts', [])
            if parts and isinstance(parts[0], str):
                content_text = parts[0]
            elif isinstance(content, dict):
                # Sometimes content is nested differently
                content_text = str(content.get('text', ''))
        elif isinstance(content, str):
            content_text = content

        timestamp = node.get('create_time')

        result.append({
            'role': role,
            'content_text': content_text,
            'timestamp': timestamp
        })

        # Traverse children
        for child_id, child_node in nodes.items():
            if child_node['parent_id'] == node_id:
                result.extend(traverse(child_id))

        return result

    # Process from each root
    for root_id in roots:
        turns.extend(traverse(root_id))

    return turns

def split_conversations(input_file, output_dir):
    """Read conversations.json and split into individual files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"Error: Expected list, got {type(data)}")
        return 0, 0

    total = len(data)
    success = 0

    for conv in data:
        try:
            conversation_id = conv.get('id', 'unknown')
            title = conv.get('title', '')
            created_at = conv.get('create_time', '')
            mapping = conv.get('mapping', {})

            slug = create_title_slug(title)
            safe_id = re.sub(r'[^\w-]', '', conversation_id)[:50]

            filename = f"{safe_id}_{slug}.json"
            filepath = output_path / filename

            turns = extract_turns(mapping)

            output_data = {
                'conversation_id': conversation_id,
                'title': title,
                'created_at': created_at,
                'turns': turns
            }

            with open(filepath, 'w', encoding='utf-8') as out:
                json.dump(output_data, out, ensure_ascii=False, indent=2)

            success += 1
            print(f"  Created: {filename}")

        except Exception as e:
            print(f"  Error processing conversation: {e}")
            continue

    return success, total

if __name__ == '__main__':
    input_file = '/Users/Zhuanz/Desktop/workspace/知识库/deepseek_data-2026-04-23/conversations.json'
    output_dir = '/Users/Zhuanz/Desktop/workspace/知识库/deepseek_split/'

    print(f"Splitting conversations from {input_file}")
    print(f"Output directory: {output_dir}")

    success, total = split_conversations(input_file, output_dir)
    print(f"\nResult: {success}/{total} conversations split successfully")