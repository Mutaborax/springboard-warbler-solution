from unittest import TestCase
from app import app, CURR_USER_KEY, do_login, do_logout
from models import db, User, Message

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['WTF_CSRF_ENABLED'] = False


class WarblerTests(TestCase):
    """Unit tests for Warbler."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_signup(self):
        """Test user signup."""

        with self.client as c:
            resp = c.post('/signup', data=dict(
                username="testuser2",
                email="test@test.com",
                password="testuser2",
                image_url=None
            ), follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Hello, testuser2!", resp.data)
            self.assertIn(f'@testuser2', resp.data.decode('utf-8'))

    def test_login(self):
        """Test user login."""

        with self.client as c:
            resp = c.post('/login', data=dict(
                username="testuser",
                password="testuser"
            ), follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Hello, testuser!", resp.data)

    def test_logout(self):
        """Test user logout."""

        self.client.post('/login', data=dict(
            username="testuser",
            password="testuser"
        ))

        with self.client as c:
            resp = c.get('/logout', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"You have successfully logged out.", resp.data)

    def test_list_users(self):
        """Test list users page."""

        with self.client as c:
            resp = c.get('/users')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@testuser', resp.data)

    def test_user_profile(self):
        """Test user profile page."""

        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'@testuser', resp.data)

    def test_following_page(self):
        """Test following page"""
