import unittest

from parser import HTMLParser, print_tree


class TestParser(unittest.TestCase):
    def test_parse_comments(self):
        body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
</head>
<body>
    <!--> comment comment -->
    <!-- multi-line 
    comment -->
</body>
</html>"""
        parser = HTMLParser(body)
        nodes = parser.parse()
        self.assertEqual(len(nodes.children), 2)
        body_node = nodes.children[1]
        self.assertEqual(len(body_node.children), 0)
