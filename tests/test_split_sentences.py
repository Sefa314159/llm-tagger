import unittest
from conversation_analysis import split_sentences

class TestSplitSentences(unittest.TestCase):
    def test_newline_separation(self):
        text = "Hello there!\nHow are you?"
        self.assertEqual(split_sentences(text), ["Hello there!", "How are you?"])

    def test_multiple_spaces(self):
        text = "Hello there!  How are you?"
        self.assertEqual(split_sentences(text), ["Hello there!", "How are you?"])

if __name__ == '__main__':
    unittest.main()
