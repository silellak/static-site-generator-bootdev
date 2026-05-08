from textnode import TextNode, TextType

def main():
    text_node = TextNode("Hello, World!", TextType.BOLD, "https://example.com")
    print(text_node)

main()