import os, sys, unittest

sys.path.append(os.path.join(__file__, *[os.pardir] * 2))
from libs.extract_channel_latest_video import get_channel_id_by_username, get_latest_video_url


class TestStringMethods(unittest.TestCase):
    def test_get_IRyS_channel_id(self):
        self.assertIsNotNone(get_channel_id_by_username("@IRyS"))

    def test_get_IRyS_latest_video_url(self):
        channel_id = get_channel_id_by_username("@IRyS")
        self.assertIsInstance(get_latest_video_url(channel_id), tuple)
        
        
if __name__ == "__main__":
    unittest.main()
