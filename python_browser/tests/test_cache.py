import time
import unittest

from cache import browser_cache


url = "https://browser.engineering/examples"
data = "Some content"


class TestBrowserCache(unittest.TestCase):
    def test_add_to_cache(self):
        browser_cache.add(url, data, 86400)
        self.assertEqual(browser_cache.has(url), True)
        self.assertEqual(browser_cache.get(url), data)

    def test_get_valid_value(self):
        browser_cache.add(url, data, 86400)
        self.assertEqual(browser_cache.has(url), True)
        self.assertEqual(browser_cache.get(url), data)

    def test_get_expired_value(self):
        browser_cache.add(url, data, 1)
        time.sleep(2)
        self.assertEqual(browser_cache.has(url), False)
        self.assertEqual(browser_cache.get(url), None)
