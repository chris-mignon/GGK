import unittest
from app import create_app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = '