import unittest

from md2html import inline


class EmailLinkTest(unittest.TestCase):
    def test_korean_particle_stays_outside_the_link(self):
        self.assertEqual(
            inline("hello.elowa@gmail.com으로 보내 주세요"),
            '<a href="mailto:hello.elowa@gmail.com">hello.elowa@gmail.com</a>으로 보내 주세요',
        )

    def test_english_address_before_a_period(self):
        self.assertEqual(
            inline("Write to hello.elowa@gmail.com."),
            'Write to <a href="mailto:hello.elowa@gmail.com">hello.elowa@gmail.com</a>.',
        )


if __name__ == "__main__":
    unittest.main()
