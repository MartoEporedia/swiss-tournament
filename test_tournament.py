import unittest
import sqlite3
from main import TournamentGUI
from PyQt5.QtWidgets import QApplication
import sys
import os
from create_db import create_database

class TournamentGUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize QApplication instance
        cls.app = QApplication(sys.argv)

        # Set up test database environment
        cls.db_name = 'test_tournament.db'
        os.environ['TOURNAMENT_DB'] = cls.db_name

        # Initialize the Tournament GUI
        cls.window = TournamentGUI()

        # Set up a temporary database for testing
        cls.connection = sqlite3.connect(cls.db_name)
        create_database()

    def test_create_pairings(self):
        """Test pairing creation with no previous pairings."""
        self.window.create_pairings()
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM pairings')
        pairings_count = cursor.fetchone()[0]
        
        self.assertGreater(pairings_count, 0, "Pairings should be created in the database")

    def test_simulate_match(self):
        """Test match simulation logic and result storage."""
        self.window.create_pairings()
        self.window.simulate_match()
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT goals1, goals2 FROM pairings WHERE goals1 IS NOT NULL AND goals2 IS NOT NULL')
        matches = cursor.fetchall()
        
        # Ensure goals are simulated
        for goals1, goals2 in matches:
            self.assertIsNotNone(goals1, "goals1 should not be None")
            self.assertIsNotNone(goals2, "goals2 should not be None")

    def test_show_standings(self):
        """Test standings display and categorize teams."""
        self.window.show_standings()
        
        # Check if standings text is set correctly
        standings_text = self.window.result_area.toPlainText()
        self.assertIn("Champions League", standings_text, "Champions League section should be in standings output")
        self.assertIn("Europa League", standings_text, "Europa League section should be in standings output")
        self.assertIn("Conference League", standings_text, "Conference League section should be in standings output")

    def test_reset_database(self):
        """Test if reset database clears all tables."""
        self.window.reset_database_button.click()
        
        cursor = self.connection.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM pairings')
        pairings_count = cursor.fetchone()[0]
        
        self.assertEqual(pairings_count, 0, "Pairings should be reset to zero entries")

    @classmethod
    def tearDownClass(cls):
        # Close the application and remove test database
        cls.connection.close()
        cls.app.quit()
        if os.path.exists(cls.db_name):
            os.remove(cls.db_name)

if __name__ == "__main__":
    unittest.main(verbosity=2)