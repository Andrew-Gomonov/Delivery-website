import bcrypt
from App import api
from datetime import date
import unittest


class TestApi(unittest.TestCase):
    def test_get_all_news(self):
        news = api.get_news()
        self.assertIsInstance(news, list)

    def test_get_all_users(self):
        users = api.get_news()
        self.assertIsInstance(users, list)

    def test_create_news(self):
        news1 = {
            "title": "testing",
            "content": "testing api",
            "image": "https://st.depositphotos.com/1032577/3238/i/950/depositphotos_32382611-stock-photo-test.jpg"
        }
        news2 = {
            "title": "testing",
            "content": "testing api",
        }
        data = api.create_news(news1)
        self.assertIsInstance(data, dict)
        self.assertDictEqual(data, {"Code": 201, "msg": "News created"})
        with self.assertRaises(KeyError):
            api.create_news(news2)

    def test_create_user(self):
        user1 = {
            "name": "testing",
            "email": "testing@gmail.com",
            "password": "testing",
            "is_admin": 0,
        }
        user2 = {
            "name": "testing",
            "email": "testing@gmail.com",
        }
        data = api.create_user(user1)
        self.assertIsInstance(data, dict)
        self.assertDictEqual(data, {"Code": 201, "msg": "User created"})
        with self.assertRaises(KeyError):
            api.create_user(user2)

    def test_crud_news(self):
        all_news = api.get_news()
        last_id = all_news[-1]['id']
        last_news = api.News(int(last_id))
        info_last_news = last_news.get()
        self.assertIsInstance(info_last_news, dict)
        self.assertDictEqual(
            last_news.get(),
            {
                "id": all_news[-1]['id'],
                "title": "testing",
                "content": "testing api",
                "publish_date": date.today().strftime('%Y-%m-%d'),
                "image_url": "https://st.depositphotos.com/1032577/3238/i/950/"
                             "depositphotos_32382611-stock-photo-test.jpg"
            }
        )
        edit = last_news.edit({"content": "unitTest"})
        self.assertIsInstance(edit, dict)
        self.assertDictEqual(edit, {"Code": 200, "msg": "News updated successfully"})
        self.assertEqual(last_news.get()['content'], "unitTest")
        delete = last_news.delete()
        self.assertIsInstance(delete, dict)
        self.assertDictEqual(delete, {"Code": 200, "msg": "News deleted successfully"})
        is_deleted = True
        for news in api.get_news():
            if news['id'] == last_id:
                is_deleted = False
        self.assertTrue(is_deleted)

    def test_crud_users(self):
        all_users = api.get_users()
        last_id = all_users[-1]['id']
        last_user = api.User(int(last_id))
        info_last_user = last_user.get()
        self.assertIsInstance(info_last_user, dict)
        self.assertDictEqual(
            last_user.get(),
            {
                "id": all_users[-1]['id'],
                "name": "testing",
                "email": "testing@gmail.com",
                "register_date": date.today().strftime('%Y-%m-%d'),
                "password":
                    info_last_user['password']
                    if bcrypt.checkpw("testing".encode(), info_last_user['password'].encode()) else "error",
                "is_admin": 0
            }
        )
        edit = last_user.edit({"name": "testingEdit"})
        self.assertIsInstance(edit, dict)
        self.assertDictEqual(edit, {"Code": 200, "msg": "User updated successfully"})
        self.assertEqual(last_user.get()['name'], "testingEdit")
        delete = last_user.delete()
        self.assertIsInstance(delete, dict)
        self.assertDictEqual(delete, {"Code": 200, "msg": "User deleted successfully"})
        is_deleted = True
        for user in api.get_users():
            if user['id'] == last_id:
                is_deleted = False
        self.assertTrue(is_deleted)


if __name__ == '__main__':
    unittest.main()
