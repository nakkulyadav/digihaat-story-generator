import unittest

from scraper import shorten_product_name


class ShortenProductNameTests(unittest.TestCase):

    def test_no_delimiter_returns_unchanged(self):
        self.assertEqual(
            shorten_product_name("Amul Fresh Butter"),
            "Amul Fresh Butter"
        )

    def test_bundle_listing_with_standalone_plus_is_untouched(self):
        name = "Shampoo 200ml + Conditioner 200ml, Combo Pack"
        self.assertEqual(shorten_product_name(name), name)

    def test_comma_truncates(self):
        self.assertEqual(
            shorten_product_name("Amul Butter, 500g Pack"),
            "Amul Butter"
        )

    def test_hyphen_word_truncates(self):
        self.assertEqual(
            shorten_product_name("Amul Butter - Pack of 2"),
            "Amul Butter"
        )

    def test_pipe_word_truncates(self):
        self.assertEqual(
            shorten_product_name("Amul Butter | Best Seller"),
            "Amul Butter"
        )

    def test_paren_word_truncates(self):
        self.assertEqual(
            shorten_product_name("Amul Butter (Pack of 2)"),
            "Amul Butter"
        )

    def test_digit_word_truncates_when_not_first_word(self):
        self.assertEqual(
            shorten_product_name("Choco 500g Bar, Rich Taste"),
            "Choco"
        )

    def test_leading_bracket_is_skipped_then_further_truncated(self):
        self.assertEqual(
            shorten_product_name("(Combo Pack) Amul Butter - 500g"),
            "Amul Butter"
        )

    def test_leading_bracket_with_nothing_after_falls_back_to_original(self):
        self.assertEqual(
            shorten_product_name("(Combo Offer)"),
            "(Combo Offer)"
        )

    def test_unmatched_leading_bracket_falls_back_to_original(self):
        name = "(Combo Pack Amul Butter 500g"
        self.assertEqual(shorten_product_name(name), name)

    def test_name_starting_with_digit_falls_back_to_original(self):
        name = "3M Command Strips 500g"
        self.assertEqual(shorten_product_name(name), name)

    def test_compound_hyphenated_word_is_not_mangled(self):
        self.assertEqual(
            shorten_product_name("Wi-Fi Router"),
            "Wi-Fi Router"
        )

    def test_earliest_delimiter_wins_over_later_comma(self):
        self.assertEqual(
            shorten_product_name("Non-Stick Frying Pan, 2 Pieces"),
            "Non-Stick Frying Pan"
        )

    def test_empty_and_none_name(self):
        self.assertEqual(shorten_product_name(""), "")
        self.assertIsNone(shorten_product_name(None))


if __name__ == "__main__":
    unittest.main()
