import unittest

from campus_resource_management import CampusResourceManager


class CampusResourceManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = CampusResourceManager()

    def test_add_resource_rejects_duplicate_ids(self) -> None:
        self.assertTrue(self.manager.add_resource("LAP-01", "Laptop", "Electronics", 5))
        self.assertFalse(self.manager.add_resource("LAP-01", "Another", "Electronics", 2))
        self.assertEqual(1, len(self.manager.resources))

    def test_borrow_reject_does_not_mutate_state(self) -> None:
        self.manager.add_resource("CAM-01", "Camera", "Media", 2)

        self.assertFalse(self.manager.borrow_resource("", "CAM-01", 1))
        self.assertFalse(self.manager.borrow_resource("F001", "CAM-01", 3))

        resource = self.manager.resources["CAM-01"]
        self.assertEqual(2, resource.available_units)
        self.assertEqual({}, self.manager.loans)
        self.assertEqual([], self.manager.borrow_log)

    def test_successful_borrow_logs_and_updates_inventory(self) -> None:
        self.manager.add_resource("TAB-01", "Tablet", "Electronics", 4)

        self.assertTrue(self.manager.borrow_resource("F100", "TAB-01", 2))

        self.assertEqual(2, self.manager.resources["TAB-01"].available_units)
        self.assertEqual(2, self.manager.loans[("F100", "TAB-01")])
        self.assertEqual(1, len(self.manager.borrow_log))

    def test_return_must_not_exceed_current_loan(self) -> None:
        self.manager.add_resource("MIC-01", "Microphone", "Media", 5)
        self.manager.borrow_resource("F200", "MIC-01", 2)

        self.assertFalse(self.manager.return_resource("F200", "MIC-01", 3))
        self.assertEqual(3, self.manager.resources["MIC-01"].available_units)
        self.assertEqual(2, self.manager.loans[("F200", "MIC-01")])

    def test_search_filter_and_report(self) -> None:
        self.manager.add_resource("L1", "Laptop Pro", "Electronics", 6)
        self.manager.add_resource("L2", "Laptop Air", "Electronics", 5)
        self.manager.add_resource("R1", "Router", "Network", 2)

        self.manager.borrow_resource("F1", "L1", 2)
        self.manager.borrow_resource("F2", "L2", 2)
        self.manager.borrow_resource("F3", "R1", 1)

        search_results = self.manager.search_by_name("laptop")
        self.assertEqual({"L1", "L2"}, {r.resource_id for r in search_results})

        filtered = self.manager.filter_by_category("electronics")
        self.assertEqual({"L1", "L2"}, {r.resource_id for r in filtered})

        report = self.manager.generate_report()
        self.assertEqual(13, report["total_units"])
        self.assertEqual(8, report["available_units"])
        self.assertEqual(5, report["units_borrowed"])

        low_stock_ids = {r.resource_id for r in report["low_stock_resources"]}
        self.assertIn("R1", low_stock_ids)

        most_borrowed_ids = {r.resource_id for r in report["most_borrowed_resources"]}
        self.assertEqual({"L1", "L2"}, most_borrowed_ids)


if __name__ == "__main__":
    unittest.main()
