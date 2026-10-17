import unittest

from answer import answer


class AnswerTest(unittest.TestCase):
    def test_answer(self):
        # This assertion gives the agent a concrete functional target.
        self.assertEqual(answer(), 42)


if __name__ == "__main__":
    unittest.main()
