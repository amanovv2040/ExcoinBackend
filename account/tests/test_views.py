# from .test_setup import TestSetUp
#
#
# class TestView(TestSetUp):
#
#     def test_user_cannot_register_with_no_data(self):
#         res = self.client.post(self.register_url)
#         self.assertEquals(res.status_code, 400)
#
#     def test_user_can_register_correctly(self):
#         res = self.client.post(self.register_url, self.user_data, format='json')
#         self.assertEquals(res.status_code, 201)
