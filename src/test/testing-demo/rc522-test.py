import sys
import unittest
sys.path.append("../../hardware")
from RC522 import RC522
import time
#reads the badge id from scanning on RFID reader
class badge_id_test(unittest.TestCase):     

    def test_badge_positive(self):  
        badge_id = 248473432955
        print("test with badge id ")
        self.reader = RC522()
        badge_num = self.reader.read_card()
        self.assertEqual(badge_num, badge_id)
        #sleep is necessary to make sure the tests don't overlap
        time.sleep(2)

#reads the data on the card from RFID reader
class card_data_test(unittest.TestCase):     
    
    def test_card_data(self):
        card_data = "test2                                           "
        print("test with card id")
        self.reader = RC522()
        card_text = self.reader.read_card_data(3)
        self.assertEqual(card_text,card_data)

if __name__ == '__main__': 
    unittest.main() 