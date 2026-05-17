from enum import Enum

from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    root_node = ParentNode("div", [])
    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            child_nodes = text_to_children(block.strip().replace("\n", " "))
            root_node.children.append(ParentNode("p", child_nodes))

        elif block_type == BlockType.HEADING:
            heading_level = len(block) - len(block.lstrip("#"))
            if heading_level > 6:
                heading_level = 6
            child_nodes = text_to_children(block[heading_level + 1:].strip())
            root_node.children.append(ParentNode(f"h{heading_level}", child_nodes))

        elif block_type == BlockType.QUOTE:
            quote_line = clean_string_to_one_string(block, ">")

            child_nodes = text_to_children(quote_line)
            root_node.children.append(ParentNode("blockquote", child_nodes))

        elif block_type == BlockType.UNORDERED_LIST:
            child_nodes = [ParentNode("li", text_to_children(line[2:].strip())) for line in block.split("\n")]
            root_node.children.append(ParentNode("ul", child_nodes))

        elif block_type == BlockType.ORDERED_LIST:
            child_nodes = [ParentNode("li", text_to_children(re.sub(r'^\d+\. ', '', line).strip())) for line in block.split("\n")]
            root_node.children.append(ParentNode("ol", child_nodes))

        elif block_type == BlockType.CODE:
            code_content = block[4:-3]  # remove the ``` markers
            text_node = TextNode(code_content, TextType.TEXT)
            html_node = text_node_to_html(text_node)
            code_node = ParentNode("code", [html_node])
            root_node.children.append(ParentNode("pre", [code_node]))
         
        else:
            raise ValueError(f"Unknown block type: {block_type}")
  

    return root_node        

def extract_title(markdown):
    lines = markdown.split("\n")
    title = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            return title
    if title is None:
        raise Exception("No title found in markdown")
    
def clean_string_to_one_string(block, character):
    raw_lines = block.split("\n")
    cleaned_lines = []
    for line in raw_lines:
        cleaned = line.lstrip(character).strip()  # whatever cleanup you need
        cleaned_lines.append(cleaned)
    combined = " ".join(cleaned_lines)  # one string, space-separated
    return combined

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = [text_node_to_html(text_node) for text_node in text_nodes]
    return html_nodes

def block_to_block_type(block):
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    elif block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    elif all(line.startswith(">") for line in block.split("\n")):
        return BlockType.QUOTE
    elif all(line.startswith("- ") for line in block.split("\n")):
        return BlockType.UNORDERED_LIST
    elif re.match(r"^\d+\. ", block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

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

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE_TEXT)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = []
    lines = markdown.split("\n\n")
    for line in lines:
        if (line.strip() != ""):
            blocks.append(line.strip())
    return blocks

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using template {template_path}")
    with open(from_path, "r") as f:
        markdown = f.read()
    html_node = markdown_to_html_node(markdown)
    html_content = html_node.to_html()
    with open(template_path, "r") as f:
        template = f.read()
    title = extract_title(markdown)
    final_content = template.replace("{{ Content }}", html_content)
    final_content = final_content.replace("{{ Title }}", title)
    with open(dest_path, "w") as f:
        f.write(final_content)