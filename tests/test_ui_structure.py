import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class MobileUiStructureTests(unittest.TestCase):
    def test_redesigned_ui_contains_primary_screens(self):
        ui = (ROOT / "pendo_ui.kv").read_text(encoding="utf-8")
        for screen in ("<LoginScreen>:", "<PlanScreen>:", "<HomeScreen>:", "<ModuleScreen>:", "<MoreScreen>:", "<SettingsScreen>:"):
            with self.subTest(screen=screen):
                self.assertIn(screen, ui)

    def test_module_contract_and_bottom_navigation_are_present(self):
        ui = (ROOT / "pendo_ui.kv").read_text(encoding="utf-8")
        for required in ("id: module_entry", "id: module_items", "id: sync_status", "BottomNavigation", "app.go('settings')"):
            with self.subTest(required=required):
                self.assertIn(required, ui)

    def test_horizontal_gesture_navigation_is_wired(self):
        source = (ROOT / "main.py").read_text(encoding="utf-8")
        self.assertIn("class PendoScreenManager(ScreenManager):", source)
        self.assertIn("def handle_swipe(self, dx):", source)
        self.assertIn("app.handle_swipe(dx)", source)


if __name__ == "__main__":
    unittest.main()
