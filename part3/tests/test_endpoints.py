import unittest
from app import create_app
from app.services.facade import facade

ADMIN_EMAIL = 'admin@hbnb.io'
ADMIN_PASSWORD = 'admin1234'


def reset_facade():
    """Clear all in-memory storage between tests, then reseed the default admin."""
    facade.user_repo._storage.clear()
    facade.place_repo._storage.clear()
    facade.review_repo._storage.clear()
    facade.amenity_repo._storage.clear()
    facade._seed_admin()


class AuthedTestCase(unittest.TestCase):
    """Base class providing helpers to bootstrap users (via the admin account)
    and log in to get a JWT."""

    def setUp(self):
        self.app = create_app()
        self.app.config['BCRYPT_LOG_ROUNDS'] = 4
        self.client = self.app.test_client()
        reset_facade()

    def _login(self, email, password):
        res = self.client.post('/api/v1/auth/login', json={
            'email': email, 'password': password
        })
        return res.get_json()['access_token']

    def _admin_token(self):
        return self._login(ADMIN_EMAIL, ADMIN_PASSWORD)

    def _auth_header(self, token):
        return {'Authorization': f'Bearer {token}'}

    def _register_and_login(self, email, password='password123',
                             first_name='Test', last_name='User'):
        """Create a regular (non-admin) user via the admin account, then log
        in as that user and return (user_id, token)."""
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/users/', json={
            'first_name': first_name, 'last_name': last_name,
            'email': email, 'password': password
        }, headers=self._auth_header(admin_token))
        user_id = res.get_json()['id']
        token = self._login(email, password)
        return user_id, token


class TestUserEndpoints(AuthedTestCase):
    def test_create_user_requires_auth(self):
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com',
            'password': 'mysecretpassword'
        })
        self.assertEqual(res.status_code, 401)

    def test_create_user_forbidden_for_regular_user(self):
        _, token = self._register_and_login('regular@example.com')
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe2@example.com',
            'password': 'mysecretpassword'
        }, headers=self._auth_header(token))
        self.assertEqual(res.status_code, 403)

    def test_create_user_success_as_admin(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com',
            'password': 'mysecretpassword'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertIn('message', data)
        self.assertNotIn('password', data)

    def test_create_user_password_hashed_and_not_leaked(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'Hash', 'last_name': 'Test', 'email': 'hash.test@example.com',
            'password': 'mysecretpassword'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 201)
        user_id = res.get_json()['id']

        get_res = self.client.get(f'/api/v1/users/{user_id}')
        self.assertNotIn('password', get_res.get_json())

        list_res = self.client.get('/api/v1/users/')
        for u in list_res.get_json():
            self.assertNotIn('password', u)

        user = facade.get_user(user_id)
        self.assertIsNotNone(user.password)
        self.assertNotEqual(user.password, 'mysecretpassword')
        self.assertTrue(user.verify_password('mysecretpassword'))
        self.assertFalse(user.verify_password('wrongpassword'))

    def test_create_user_duplicate_email(self):
        admin_token = self._admin_token()
        self.client.post('/api/v1/users/', json={
            'first_name': 'Jane', 'last_name': 'Doe', 'email': 'dup@example.com',
            'password': 'password123'
        }, headers=self._auth_header(admin_token))
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'Jane', 'last_name': 'Doe', 'email': 'dup@example.com',
            'password': 'password123'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', res.get_json())

    def test_create_user_invalid_email(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'John', 'last_name': 'Doe', 'email': 'not-an-email',
            'password': 'password123'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)

    def test_create_user_empty_first_name(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/users/', json={
            'first_name': '', 'last_name': 'Doe', 'email': 'valid@example.com',
            'password': 'password123'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)

    def test_create_user_first_name_too_long(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'A' * 51, 'last_name': 'Doe', 'email': 'long@example.com',
            'password': 'password123'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)

    def test_get_all_users(self):
        res = self.client.get('/api/v1/users/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_user_by_id(self):
        user_id, _ = self._register_and_login('alice@example.com')
        res = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['email'], 'alice@example.com')

    def test_get_user_not_found(self):
        res = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(res.status_code, 404)

    def test_update_user_requires_auth(self):
        user_id, _ = self._register_and_login('bob@example.com')
        res = self.client.put(f'/api/v1/users/{user_id}', json={'first_name': 'Bobby'})
        self.assertEqual(res.status_code, 401)

    def test_update_user_success(self):
        user_id, token = self._register_and_login('bob2@example.com')
        res = self.client.put(f'/api/v1/users/{user_id}', json={
            'first_name': 'Bobby'
        }, headers=self._auth_header(token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['first_name'], 'Bobby')

    def test_update_user_other_user_forbidden(self):
        _, token_a = self._register_and_login('usera@example.com')
        user_b_id, _ = self._register_and_login('userb@example.com')
        res = self.client.put(f'/api/v1/users/{user_b_id}', json={
            'first_name': 'Hacked'
        }, headers=self._auth_header(token_a))
        self.assertEqual(res.status_code, 403)

    def test_update_user_cannot_change_email(self):
        user_id, token = self._register_and_login('nochange@example.com')
        res = self.client.put(f'/api/v1/users/{user_id}', json={
            'email': 'new@example.com'
        }, headers=self._auth_header(token))
        self.assertEqual(res.status_code, 400)

    def test_update_user_cannot_change_password(self):
        user_id, token = self._register_and_login('nochangepw@example.com')
        res = self.client.put(f'/api/v1/users/{user_id}', json={
            'password': 'newpassword'
        }, headers=self._auth_header(token))
        self.assertEqual(res.status_code, 400)

    def test_admin_can_update_any_user_email_and_password(self):
        user_id, _ = self._register_and_login('changeme@example.com')
        admin_token = self._admin_token()
        res = self.client.put(f'/api/v1/users/{user_id}', json={
            'email': 'changed@example.com',
            'password': 'brandnewpassword'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['email'], 'changed@example.com')

        user = facade.get_user(user_id)
        self.assertTrue(user.verify_password('brandnewpassword'))

    def test_admin_update_duplicate_email_rejected(self):
        _, _ = self._register_and_login('first@example.com')
        second_id, _ = self._register_and_login('second@example.com')
        admin_token = self._admin_token()
        res = self.client.put(f'/api/v1/users/{second_id}', json={
            'email': 'first@example.com'
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['error'], 'Email already in use')


class TestAmenityEndpoints(AuthedTestCase):
    def test_create_amenity_requires_auth(self):
        res = self.client.post('/api/v1/amenities/', json={'name': 'WiFi'})
        self.assertEqual(res.status_code, 401)

    def test_create_amenity_forbidden_for_regular_user(self):
        _, token = self._register_and_login('regularuser@example.com')
        res = self.client.post('/api/v1/amenities/', json={'name': 'WiFi'},
                                headers=self._auth_header(token))
        self.assertEqual(res.status_code, 403)

    def test_create_amenity_success_as_admin(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/amenities/', json={'name': 'WiFi'},
                                headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()['name'], 'WiFi')

    def test_create_amenity_empty_name(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/amenities/', json={'name': ''},
                                headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)

    def test_create_amenity_name_too_long(self):
        admin_token = self._admin_token()
        res = self.client.post('/api/v1/amenities/', json={'name': 'A' * 51},
                                headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 400)

    def test_get_all_amenities(self):
        res = self.client.get('/api/v1/amenities/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_amenity_by_id(self):
        admin_token = self._admin_token()
        create = self.client.post('/api/v1/amenities/', json={'name': 'Pool'},
                                   headers=self._auth_header(admin_token))
        amenity_id = create.get_json()['id']
        res = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['name'], 'Pool')

    def test_get_amenity_not_found(self):
        res = self.client.get('/api/v1/amenities/bad-id')
        self.assertEqual(res.status_code, 404)

    def test_update_amenity_requires_auth(self):
        admin_token = self._admin_token()
        create = self.client.post('/api/v1/amenities/', json={'name': 'Gym'},
                                   headers=self._auth_header(admin_token))
        amenity_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Fitness Center'})
        self.assertEqual(res.status_code, 401)

    def test_update_amenity_forbidden_for_regular_user(self):
        admin_token = self._admin_token()
        create = self.client.post('/api/v1/amenities/', json={'name': 'Gym'},
                                   headers=self._auth_header(admin_token))
        amenity_id = create.get_json()['id']
        _, token = self._register_and_login('regularuser2@example.com')
        res = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Hacked'},
                               headers=self._auth_header(token))
        self.assertEqual(res.status_code, 403)

    def test_update_amenity_success_as_admin(self):
        admin_token = self._admin_token()
        create = self.client.post('/api/v1/amenities/', json={'name': 'Gym'},
                                   headers=self._auth_header(admin_token))
        amenity_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Fitness Center'},
                               headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('message', res.get_json())

    def test_update_amenity_not_found(self):
        admin_token = self._admin_token()
        res = self.client.put('/api/v1/amenities/bad-id', json={'name': 'X'},
                               headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 404)


class TestPlaceEndpoints(AuthedTestCase):
    def setUp(self):
        super().setUp()
        self.owner_id, self.owner_token = self._register_and_login('owner@example.com')

    def _create_place(self, token=None, **overrides):
        payload = {
            'title': 'Test Place', 'description': 'A nice place',
            'price': 100.0, 'latitude': 37.7749, 'longitude': -122.4194,
            'amenities': []
        }
        payload.update(overrides)
        headers = self._auth_header(token if token is not None else self.owner_token)
        return self.client.post('/api/v1/places/', json=payload, headers=headers)

    def test_create_place_requires_auth(self):
        res = self.client.post('/api/v1/places/', json={
            'title': 'No Auth Place', 'price': 10.0,
            'latitude': 0.0, 'longitude': 0.0, 'amenities': []
        })
        self.assertEqual(res.status_code, 401)

    def test_create_place_success(self):
        res = self._create_place()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['title'], 'Test Place')
        self.assertEqual(data['owner_id'], self.owner_id)

    def test_create_place_negative_price(self):
        res = self._create_place(price=-10)
        self.assertEqual(res.status_code, 400)

    def test_create_place_latitude_out_of_range(self):
        res = self._create_place(latitude=91.0)
        self.assertEqual(res.status_code, 400)

    def test_create_place_longitude_out_of_range(self):
        res = self._create_place(longitude=181.0)
        self.assertEqual(res.status_code, 400)

    def test_create_place_empty_title(self):
        res = self._create_place(title='')
        self.assertEqual(res.status_code, 400)

    def test_get_all_places(self):
        res = self.client.get('/api/v1/places/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_place_by_id(self):
        create = self._create_place()
        place_id = create.get_json()['id']
        res = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('owner', data)
        self.assertIn('amenities', data)
        self.assertIn('reviews', data)

    def test_get_place_not_found(self):
        res = self.client.get('/api/v1/places/bad-id')
        self.assertEqual(res.status_code, 404)

    def test_update_place_requires_auth(self):
        create = self._create_place()
        place_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Updated Place', 'description': 'Updated',
            'price': 150.0, 'latitude': 40.0, 'longitude': -74.0,
            'amenities': []
        })
        self.assertEqual(res.status_code, 401)

    def test_update_place_success(self):
        create = self._create_place()
        place_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Updated Place', 'description': 'Updated',
            'price': 150.0, 'latitude': 40.0, 'longitude': -74.0,
            'amenities': []
        }, headers=self._auth_header(self.owner_token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Place updated successfully')

    def test_update_place_unauthorized(self):
        create = self._create_place()
        place_id = create.get_json()['id']
        _, other_token = self._register_and_login('intruder@example.com')
        res = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Hacked Place', 'description': '', 'price': 1.0,
            'latitude': 0.0, 'longitude': 0.0, 'amenities': []
        }, headers=self._auth_header(other_token))
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()['error'], 'Unauthorized action')

    def test_update_place_as_admin_bypasses_ownership(self):
        create = self._create_place()
        place_id = create.get_json()['id']
        admin_token = self._admin_token()
        res = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Admin Edited', 'description': 'Edited by admin', 'price': 200.0,
            'latitude': 10.0, 'longitude': 10.0, 'amenities': []
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Place updated successfully')

    def test_update_place_not_found(self):
        res = self.client.put('/api/v1/places/bad-id', json={
            'title': 'X', 'description': '', 'price': 1.0,
            'latitude': 0.0, 'longitude': 0.0, 'amenities': []
        }, headers=self._auth_header(self.owner_token))
        self.assertEqual(res.status_code, 404)


class TestReviewEndpoints(AuthedTestCase):
    def setUp(self):
        super().setUp()
        self.owner_id, self.owner_token = self._register_and_login('placeowner@example.com')
        self.reviewer_id, self.reviewer_token = self._register_and_login('reviewer@example.com')
        place_res = self.client.post('/api/v1/places/', json={
            'title': 'Review Target', 'description': 'A place',
            'price': 50.0, 'latitude': 0.0, 'longitude': 0.0, 'amenities': []
        }, headers=self._auth_header(self.owner_token))
        self.place_id = place_res.get_json()['id']

    def _create_review(self, token=None, **overrides):
        payload = {
            'text': 'Great place!', 'rating': 5, 'place_id': self.place_id
        }
        payload.update(overrides)
        headers = self._auth_header(token if token is not None else self.reviewer_token)
        return self.client.post('/api/v1/reviews/', json=payload, headers=headers)

    def test_create_review_requires_auth(self):
        res = self.client.post('/api/v1/reviews/', json={
            'text': 'Great place!', 'rating': 5, 'place_id': self.place_id
        })
        self.assertEqual(res.status_code, 401)

    def test_create_review_success(self):
        res = self._create_review()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['user_id'], self.reviewer_id)

    def test_create_review_own_place_forbidden(self):
        res = self._create_review(token=self.owner_token)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()['error'], 'You cannot review your own place')

    def test_create_review_duplicate_forbidden(self):
        first = self._create_review()
        self.assertEqual(first.status_code, 201)
        second = self._create_review(rating=3, text='Again')
        self.assertEqual(second.status_code, 400)
        self.assertEqual(second.get_json()['error'], 'You have already reviewed this place')

    def test_admin_can_review_owned_place_and_duplicate(self):
        admin_token = self._admin_token()
        first = self._create_review(token=admin_token)
        self.assertEqual(first.status_code, 201)
        # Admin reviewing the same place again (would normally be a duplicate) is allowed.
        second = self._create_review(token=admin_token, rating=2, text='Second admin review')
        self.assertEqual(second.status_code, 201)

    def test_create_review_invalid_place(self):
        res = self._create_review(place_id='bad-id')
        self.assertEqual(res.status_code, 400)

    def test_create_review_rating_out_of_range(self):
        res = self._create_review(rating=6)
        self.assertEqual(res.status_code, 400)

    def test_create_review_rating_zero(self):
        res = self._create_review(rating=0)
        self.assertEqual(res.status_code, 400)

    def test_create_review_empty_text(self):
        res = self._create_review(text='')
        self.assertEqual(res.status_code, 400)

    def test_get_all_reviews(self):
        res = self.client.get('/api/v1/reviews/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_review_by_id(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['text'], 'Great place!')

    def test_get_review_not_found(self):
        res = self.client.get('/api/v1/reviews/bad-id')
        self.assertEqual(res.status_code, 404)

    def test_update_review_requires_auth(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'text': 'Amazing stay!', 'rating': 4
        })
        self.assertEqual(res.status_code, 401)

    def test_update_review_success(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'text': 'Amazing stay!', 'rating': 4
        }, headers=self._auth_header(self.reviewer_token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Review updated successfully')

    def test_update_review_unauthorized(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'text': 'Hacked review', 'rating': 1
        }, headers=self._auth_header(self.owner_token))
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()['error'], 'Unauthorized action')

    def test_update_review_as_admin_bypasses_ownership(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        admin_token = self._admin_token()
        res = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'text': 'Edited by admin', 'rating': 2
        }, headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 200)

    def test_update_review_not_found(self):
        res = self.client.put('/api/v1/reviews/bad-id', json={
            'text': 'X', 'rating': 3
        }, headers=self._auth_header(self.reviewer_token))
        self.assertEqual(res.status_code, 404)

    def test_delete_review_requires_auth(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.delete(f'/api/v1/reviews/{review_id}')
        self.assertEqual(res.status_code, 401)

    def test_delete_review_success(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.delete(f'/api/v1/reviews/{review_id}',
                                  headers=self._auth_header(self.reviewer_token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Review deleted successfully')

    def test_delete_review_unauthorized(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.delete(f'/api/v1/reviews/{review_id}',
                                  headers=self._auth_header(self.owner_token))
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()['error'], 'Unauthorized action')

    def test_delete_review_as_admin_bypasses_ownership(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        admin_token = self._admin_token()
        res = self.client.delete(f'/api/v1/reviews/{review_id}',
                                  headers=self._auth_header(admin_token))
        self.assertEqual(res.status_code, 200)

    def test_delete_review_not_found(self):
        res = self.client.delete('/api/v1/reviews/bad-id',
                                  headers=self._auth_header(self.reviewer_token))
        self.assertEqual(res.status_code, 404)

    def test_get_reviews_by_place(self):
        self._create_review()
        res = self.client.get(f'/api/v1/places/{self.place_id}/reviews')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.get_json()), 0)

    def test_get_reviews_by_place_not_found(self):
        res = self.client.get('/api/v1/places/bad-id/reviews')
        self.assertEqual(res.status_code, 404)


class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['BCRYPT_LOG_ROUNDS'] = 4
        self.client = self.app.test_client()
        reset_facade()
        admin_token_res = self.client.post('/api/v1/auth/login', json={
            'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD
        })
        admin_token = admin_token_res.get_json()['access_token']
        self.client.post('/api/v1/users/', json={
            'first_name': 'Auth', 'last_name': 'User', 'email': 'auth.user@example.com',
            'password': 'correctpassword'
        }, headers={'Authorization': f'Bearer {admin_token}'})

    def test_login_success(self):
        res = self.client.post('/api/v1/auth/login', json={
            'email': 'auth.user@example.com', 'password': 'correctpassword'
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('access_token', res.get_json())

    def test_login_wrong_password(self):
        res = self.client.post('/api/v1/auth/login', json={
            'email': 'auth.user@example.com', 'password': 'wrongpassword'
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('error', res.get_json())

    def test_login_unknown_email(self):
        res = self.client.post('/api/v1/auth/login', json={
            'email': 'nobody@example.com', 'password': 'whatever'
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn('error', res.get_json())

    def test_protected_without_token(self):
        res = self.client.get('/api/v1/protected/')
        self.assertEqual(res.status_code, 401)

    def test_protected_with_valid_token(self):
        login = self.client.post('/api/v1/auth/login', json={
            'email': 'auth.user@example.com', 'password': 'correctpassword'
        })
        token = login.get_json()['access_token']
        res = self.client.get('/api/v1/protected/', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('message', res.get_json())

    def test_protected_with_invalid_token(self):
        res = self.client.get('/api/v1/protected/', headers={'Authorization': 'Bearer not-a-real-token'})
        self.assertEqual(res.status_code, 422)


class TestAdminSeed(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['BCRYPT_LOG_ROUNDS'] = 4
        self.client = self.app.test_client()
        reset_facade()

    def test_default_admin_can_login(self):
        res = self.client.post('/api/v1/auth/login', json={
            'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('access_token', res.get_json())


if __name__ == '__main__':
    unittest.main()
