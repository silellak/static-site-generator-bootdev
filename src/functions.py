from htmlnode import LeafNode
from textnode import TextNode, TextType
import re

def text_node_to_html(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE_TEXT:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception(f"Unknown text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        matches = extract_markdown_images(old_node.text)
        last_index = 0
        for alt_text, url in matches:
            start_index = old_node.text.find(f"![{alt_text}]({url})", last_index)
            if start_index == -1:
                continue
            if start_index > last_index:
                split_nodes.append(TextNode(old_node.text[last_index:start_index], TextType.TEXT))
            split_nodes.append(TextNode(alt_text, TextType.IMAGE, url=url))
            last_index = start_index + len(f"![{alt_text}]({url})")
        if last_index < len(old_node.text):
            split_nodes.append(TextNode(old_node.text[last_index:], TextType.TEXT))
        new_nodes.extend(split_nodes)
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        matches = extract_markdown_links(old_node.text)
        last_index = 0
        for link_text, url in matches:
            start_index = old_node.text.find(f"[{link_text}]({url})", last_index)
            if start_index == -1:
                continue
            if start_index > last_index:
                split_nodes.append(TextNode(old_node.text[last_index:start_index], TextType.TEXT))
            split_nodes.append(TextNode(link_text, TextType.LINK, url=url))
            last_index = start_index + len(f"[{link_text}]({url})")
        if last_index < len(old_node.text):
            split_nodes.append(TextNode(old_node.text[last_index:], TextType.TEXT))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images(text):
    images = []
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    for alt_text, url in matches:
        images.append((alt_text, url))
    return images

def extract_markdown_links(text):
    links = []
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    for link_text, url in matches:
        links.append((link_text, url))
    return links
