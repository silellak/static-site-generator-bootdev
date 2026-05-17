import unittest
from functions import extract_markdown_images, extract_markdown_links, extract_title, markdown_to_blocks, markdown_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, text_node_to_html, text_to_textnodes
from textnode import TextNode, TextType


class TestFunctions(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        html_node = text_node_to_html(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node")
    
    def test_italic(self):
        node = TextNode("This is an italic node", TextType.ITALIC)
        html_node = text_node_to_html(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node")

    def test_code_text(self):
        node = TextNode("This is a code text node", TextType.CODE_TEXT)
        html_node = text_node_to_html(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code text node")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, url="https://example.com")
        html_node = text_node_to_html(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode("An image", TextType.IMAGE, url="https://example.com/image.png")
        html_node = text_node_to_html(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.png", "alt": "An image"})

    def test_split_nodes_delimiter(self):
        old_nodes = [TextNode("This is *bold* text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
        self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))

    def test_split_nodes_delimiter_invalid(self):
        old_nodes = [TextNode("This is *bold text", TextType.TEXT)]
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter(old_nodes, "*", TextType.BOLD)
        self.assertEqual(str(context.exception), "invalid markdown, formatted section not closed")

    def test_split_nodes_delimiter_no_delimiter(self):
        old_nodes = [TextNode("This is bold text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0], TextNode("This is bold text", TextType.TEXT))

    def test_split_nodes_delimiter_multiple_delimiters(self):
        old_nodes = [TextNode("This is *bold* and *italic* text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)
        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
        self.assertEqual(new_nodes[2], TextNode(" and ", TextType.TEXT))
        self.assertEqual(new_nodes[3], TextNode("italic", TextType.BOLD))
        self.assertEqual(new_nodes[4], TextNode(" text", TextType.TEXT))

    def test_split_nodes_delimiter_empty_parts(self):
        old_nodes = [TextNode("*bold*", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(old_nodes, "*", TextType.BOLD)
        self.assertEqual(len(new_nodes), 1)
        self.assertEqual(new_nodes[0], TextNode("bold", TextType.BOLD))

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "This is text with an ![image1](https://i.imgur.com/zjjcJKZ.png) and another ![image2](https://i.imgur.com/abc123.png)"
        )
        self.assertListEqual(
            [
                ("image1", "https://i.imgur.com/zjjcJKZ.png"),
                ("image2", "https://i.imgur.com/abc123.png"),
            ],
            matches,
        )

    def test_extract_markdown_images_no_images(self):
        matches = extract_markdown_images("This is text with no images")
        self.assertListEqual([], matches)

    def test_extract_markdown_images_invalid_format(self):
        matches = extract_markdown_images("This is text with an ![invalid image](https://i.imgur.com/zjjcJKZ.png and another ![also invalid](https://i.imgur.com/abc123.png")
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://example.com)"
        )
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "This is text with a [link1](https://example.com) and another [link2](https://example.org)"
        )
        self.assertListEqual(
            [
                ("link1", "https://example.com"),
                ("link2", "https://example.org"),
            ],
            matches,
        )

    def test_extract_markdown_links_no_links(self):
        matches = extract_markdown_links("This is text with no links")
        self.assertListEqual([], matches)

    def test_extract_markdown_links_invalid_format(self):
        matches = extract_markdown_links("This is text with a [invalid link](https://example.com and another [also invalid](https://example.org")
        self.assertListEqual([], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_invalid_format(self):
        node = TextNode(
            "This is text with an ![invalid image](https://i.imgur.com/zjjcJKZ.png and another ![also invalid](https://i.imgur.com/3elNhQu.png",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_non_text_node(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and another [second link](https://example.org)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://example.org"),
            ],
            new_nodes,
        )

    def test_split_links_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_invalid_format(self):
        node = TextNode(
            "This is text with a [invalid link](https://example.com and another [also invalid](https://example.org",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_non_text_node(self):
        node = TextNode("This is a bold node", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_with_images(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link(split_nodes_image([node]))
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )   
    
    def test_split_images_with_links(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image(split_nodes_link([node]))
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_links_with_images_and_delimiters(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and an ![image](https://i.imgur.com/zjjcJKZ.png) and *bold* text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_delimiter(split_nodes_link(split_nodes_image([node])), "*", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
            new_nodes,
        )
    
    def test_split_images_with_links_and_delimiters(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://example.com) and *bold* text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_delimiter(split_nodes_image(split_nodes_link([node])), "*", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE_TEXT),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_text_to_textnodes_no_formatting(self):
        text = "This is text with no formatting"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("This is text with no formatting", TextType.TEXT)],
            nodes,
        )

    def test_text_to_textnodes_only_formatting(self):
        text = "**bold** _italic_ `code block` ![image](https://i.imgur.com/fJRm4Vk.jpeg) [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("code block", TextType.CODE_TEXT),
                TextNode(" ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_empty(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])
    
    def test_markdown_to_blocks_only_newlines(self):
        md = "\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])
    
    def test_markdown_to_blocks_no_newlines(self):
        md = "This is a single block of text with no newlines"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a single block of text with no newlines"])

    def  test_markdown_to_blocks_multiple_newlines(self):
        md = "This is a block of text\n\n\nwith multiple newlines\n\nand some more text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a block of text", "with multiple newlines", "and some more text"])

    def test_markdown_to_blocks_newlines_at_start_and_end(self):
        md = "\n\nThis is a block of text with newlines at the start and end\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a block of text with newlines at the start and end"])

    def test_markdown_to_blocks_only_newlines_and_whitespace(self):
        md = "\n\n   \n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_newlines_and_whitespace_between_blocks(self):
        md = "This is a block of text\n\n   \n\nThis is another block of text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a block of text", "This is another block of text"])  

    def test_block_to_block_type(self):
        from functions import block_to_block_type, BlockType

        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("```\ncode\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("> Quote\n> Line 2"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("This is a paragraph."), BlockType.PARAGRAPH)

    def test_block_to_block_type_invalid(self):
        from functions import block_to_block_type, BlockType

        self.assertEqual(block_to_block_type("This is a block with an invalid format\n- Item 1\n> Quote"), BlockType.PARAGRAPH)

    def test_block_to_block_type_empty(self):
        from functions import block_to_block_type, BlockType

        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)

    def test_block_to_block_type_whitespace(self):
        from functions import block_to_block_type, BlockType

        self.assertEqual(block_to_block_type("   \n   "), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_headings(self):
        md = """# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5         

###### Heading 6

####### Heading 7 (should be treated as paragraph)
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3><h4>Heading 4</h4><h5>Heading 5</h5><h6>Heading 6</h6><p>####### Heading 7 (should be treated as paragraph)</p></div>",
        )

#     def test_codeblock(self):
#         md = """
# ```
# This is text that _should_ remain
# the **same** even with inline stuff
# ```
# """

#         node = markdown_to_html_node(md)
#         html = node.to_html()
#         self.assertEqual(
#             html,
#             "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
#         )

    def test_quote(self):
        md = """> This is a quote
> that spans multiple lines
> and should be in a blockquote"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote that spans multiple lines and should be in a blockquote</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """- Item 1
- Item 2
- Item 3"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul></div>",
        )
    
    def test_ordered_list(self):
        md = """1. Item 1
2. Item 2
3. Item 3"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>Item 1</li><li>Item 2</li><li>Item 3</li></ol></div>",
        ) 

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_mixed_markdown(self):
        md = """# Heading

```
This is code that should not be parsed for *formatting* or [links](https://example.com)
```

> This is a quote with a [link](https://example.com) and **bold** text

- This is a list item with _italic_ text and an ![image](https://i.imgur.com/zjjcJKZ.png)
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading</h1><pre><code>This is code that should not be parsed for *formatting* or [links](https://example.com)\n</code></pre><blockquote>This is a quote with a <a href=\"https://example.com\">link</a> and <b>bold</b> text</blockquote><ul><li>This is a list item with <i>italic</i> text and an <img src=\"https://i.imgur.com/zjjcJKZ.png\" alt=\"image\" /></li></ul></div>",
        )

    def test_extract_title(self):
        md = """# This is the title that should be extracted
This is some content that should not be part of the title block here
"""
        title = extract_title(md)
        self.assertEqual(title, "This is the title that should be extracted")   

    def test_extract_title_no_title(self):
        md = """This is some content that should not be part of the title block here
"""
        with self.assertRaises(Exception) as context:
            extract_title(md)
        self.assertEqual(str(context.exception), "No title found in markdown")
    
    def test_extract_title_multiple_titles(self):
            md = """# This is the first title that should be extracted
# This is the second title that should not be extracted
This is some content that should not be part of the title block here
"""
            title = extract_title(md)
            self.assertEqual(title, "This is the first title that should be extracted")

# if __name__ == "__main__":
#     unittest.main()