import unittest
from transplant.data.dataset import Dataset


class DatasetTest(unittest.TestCase):

    full_dataset = Dataset()
    full_static_df = full_dataset.get_static()

    test_dataset = Dataset(test=True)
    test_static_df = test_dataset.get_static()

    train_dataset = Dataset(train=True)
    train_static_df = train_dataset.get_static()

    def test_static_train_test_split(self):
        self.assertEqual(
            len(self.full_static_df.index),
            len(self.test_static_df.index) + len(self.train_static_df.index),
            "Test and train df lengths should add up to full df length"
        )

        self.assertGreater(
            len(self.train_static_df.index),
            len(self.test_static_df.index),
            "Train df should have more rows than test df"
        )

    def test_no_target_on_test_dataset(self):
        self.assertTrue(
            "target" in self.train_static_df,
            "Train df should have a 'target' column"
        )

        self.assertTrue(
            "target" not in self.test_static_df,
            "Test df should have no 'target' column"
        )
