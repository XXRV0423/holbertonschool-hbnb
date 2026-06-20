import unittest
from app import create_app
from app.services.facade import facade


def reset_facade():
    """Clear all in-memory storage between tests."""
    facade.user_repo._storage.clear()
    facade.place_repo._storage.clear()
    facade.review_repo._storage.clear()
    facade.amenity_repo._storage.clear()


class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        reset_facade()

    def test_create_user_success(self):
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.com'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['email'], 'john.doe@example.com')

    def test_create_user_duplicate_email(self):
        self.client.post('/api/v1/users/', json={
            'first_name': 'Jane', 'last_name': 'Doe', 'email': 'dup@example.com'
        })
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'Jane', 'last_name': 'Doe', 'email': 'dup@example.com'
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', res.get_json())

    def test_create_user_invalid_email(self):
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'John', 'last_name': 'Doe', 'email': 'not-an-email'
        })
        self.assertEqual(res.status_code, 400)

    def test_create_user_empty_first_name(self):
        res = self.client.post('/api/v1/users/', json={
            'first_name': '', 'last_name': 'Doe', 'email': 'valid@example.com'
        })
        self.assertEqual(res.status_code, 400)

    def test_create_user_first_name_too_long(self):
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'A' * 51, 'last_name': 'Doe', 'email': 'long@example.com'
        })
        self.assertEqual(res.status_code, 400)

    def test_get_all_users(self):
        res = self.client.get('/api/v1/users/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_user_by_id(self):
        create = self.client.post('/api/v1/users/', json={
            'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com'
        })
        user_id = create.get_json()['id']
        res = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['email'], 'alice@example.com')

    def test_get_user_not_found(self):
        res = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(res.status_code, 404)

    def test_update_user_success(self):
        create = self.client.post('/api/v1/users/', json={
            'first_name': 'Bob', 'last_name': 'Brown', 'email': 'bob@example.com'
        })
        user_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/users/{user_id}', json={
            'first_name': 'Bobby', 'last_name': 'Brown', 'email': 'bob@example.com'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['first_name'], 'Bobby')

    def test_update_user_not_found(self):
        res = self.client.put('/api/v1/users/bad-id', json={
            'first_name': 'X', 'last_name': 'Y', 'email': 'x@y.com'
        })
        self.assertEqual(res.status_code, 404)


class TestAmenityEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        reset_facade()

    def test_create_amenity_success(self):
        res = self.client.post('/api/v1/amenities/', json={'name': 'WiFi'})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()['name'], 'WiFi')

    def test_create_amenity_empty_name(self):
        res = self.client.post('/api/v1/amenities/', json={'name': ''})
        self.assertEqual(res.status_code, 400)

    def test_create_amenity_name_too_long(self):
        res = self.client.post('/api/v1/amenities/', json={'name': 'A' * 51})
        self.assertEqual(res.status_code, 400)

    def test_get_all_amenities(self):
        res = self.client.get('/api/v1/amenities/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_get_amenity_by_id(self):
        create = self.client.post('/api/v1/amenities/', json={'name': 'Pool'})
        amenity_id = create.get_json()['id']
        res = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['name'], 'Pool')

    def test_get_amenity_not_found(self):
        res = self.client.get('/api/v1/amenities/bad-id')
        self.assertEqual(res.status_code, 404)

    def test_update_amenity_success(self):
        create = self.client.post('/api/v1/amenities/', json={'name': 'Gym'})
        amenity_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/amenities/{amenity_id}', json={'name': 'Fitness Center'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('message', res.get_json())

    def test_update_amenity_not_found(self):
        res = self.client.put('/api/v1/amenities/bad-id', json={'name': 'X'})
        self.assertEqual(res.status_code, 404)


class TestPlaceEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        reset_facade()
        res = self.client.post('/api/v1/users/', json={
            'first_name': 'Owner', 'last_name': 'User', 'email': 'owner@example.com'
        })
        self.owner_id = res.get_json()['id']

    def _create_place(self, **overrides):
        payload = {
            'title': 'Test Place', 'description': 'A nice place',
            'price': 100.0, 'latitude': 37.7749, 'longitude': -122.4194,
            'owner_id': self.owner_id, 'amenities': []
        }
        payload.update(overrides)
        return self.client.post('/api/v1/places/', json=payload)

    def test_create_place_success(self):
        res = self._create_place()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['title'], 'Test Place')

    def test_create_place_invalid_owner(self):
        res = self._create_place(owner_id='nonexistent')
        self.assertEqual(res.status_code, 400)

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

    def test_update_place_success(self):
        create = self._create_place()
        place_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/places/{place_id}', json={
            'title': 'Updated Place', 'description': 'Updated',
            'price': 150.0, 'latitude': 40.0, 'longitude': -74.0,
            'owner_id': self.owner_id, 'amenities': []
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Place updated successfully')

    def test_update_place_not_found(self):
        res = self.client.put('/api/v1/places/bad-id', json={
            'title': 'X', 'description': '', 'price': 1.0,
            'latitude': 0.0, 'longitude': 0.0,
            'owner_id': self.owner_id, 'amenities': []
        })
        self.assertEqual(res.status_code, 404)


class TestReviewEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        reset_facade()
        user_res = self.client.post('/api/v1/users/', json={
            'first_name': 'Reviewer', 'last_name': 'User', 'email': 'reviewer@example.com'
        })
        self.user_id = user_res.get_json()['id']
        place_res = self.client.post('/api/v1/places/', json={
            'title': 'Review Target', 'description': 'A place',
            'price': 50.0, 'latitude': 0.0, 'longitude': 0.0,
            'owner_id': self.user_id, 'amenities': []
        })
        self.place_id = place_res.get_json()['id']

    def _create_review(self, **overrides):
        payload = {
            'text': 'Great place!', 'rating': 5,
            'user_id': self.user_id, 'place_id': self.place_id
        }
        payload.update(overrides)
        return self.client.post('/api/v1/reviews/', json=payload)

    def test_create_review_success(self):
        res = self._create_review()
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['rating'], 5)

    def test_create_review_invalid_user(self):
        res = self._create_review(user_id='bad-id')
        self.assertEqual(res.status_code, 400)

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

    def test_update_review_success(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.put(f'/api/v1/reviews/{review_id}', json={
            'text': 'Amazing stay!', 'rating': 4,
            'user_id': self.user_id, 'place_id': self.place_id
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Review updated successfully')

    def test_update_review_not_found(self):
        res = self.client.put('/api/v1/reviews/bad-id', json={
            'text': 'X', 'rating': 3,
            'user_id': self.user_id, 'place_id': self.place_id
        })
        self.assertEqual(res.status_code, 404)

    def test_delete_review_success(self):
        create = self._create_review()
        review_id = create.get_json()['id']
        res = self.client.delete(f'/api/v1/reviews/{review_id}')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()['message'], 'Review deleted successfully')

    def test_delete_review_not_found(self):
        res = self.client.delete('/api/v1/reviews/bad-id')
        self.assertEqual(res.status_code, 404)

    def test_get_reviews_by_place(self):
        self._create_review()
        res = self.client.get(f'/api/v1/places/{self.place_id}/reviews')
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(res.get_json()), 0)

    def test_get_reviews_by_place_not_found(self):
        res = self.client.get('/api/v1/places/bad-id/reviews')
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
