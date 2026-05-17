from functions import generate_page
from textnode import TextNode, TextType

def main():
    print("Starting static site generation...")
    copy_from_static_to_public()

def copy_from_static_to_public():
    import shutil
    import os

    src_dir = "static"
    dst_dir = "public"

    print(f"Copying contents from {src_dir} to {dst_dir}...")

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for item in os.listdir(dst_dir):
        item_path = os.path.join(dst_dir, item)
        if os.path.isdir(item_path):
            print(f"Removing existing directory {item_path}")
            shutil.rmtree(item_path)
        else:
            print(f"Removing existing file {item_path}")
            os.remove(item_path)

    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.isdir(s):
            print(f"Copying directory {s} to {d}")
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            print(f"Copying file {s} to {d}")
            shutil.copy2(s, d)

    generate_page("content/index.md", "template.html", "public/index.html")

main()