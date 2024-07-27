import quart_cognito
from unittest import TestCase
from unittest.mock import Mock


class objectview(object):
    def __init__(self, d):
        self.__dict__ = d

class TestHeaderPrefix(TestCase):

  def test_valid_header_prefix(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : 'Bearer'})

    get_mock = Mock(return_value='Bearer Test')
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    
    quart_cognito.request = request_mock


    ca = quart_cognito.CognitoAuth()
    result  = ca.get_token()
    assert (result == 'Test')
    
  def test_incorrect_header_prefix(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : 'Bearer'})

    get_mock = Mock(return_value='Something Test')
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    quart_cognito.request = request_mock
    ca = quart_cognito.CognitoAuth()
    self.assertRaises(quart_cognito.CognitoAuthError, ca.get_token)
  
    
  def test_malformed_header(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : 'Bearer'})

    get_mock = Mock(return_value='Something To Fail')
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    quart_cognito.request = request_mock
    ca = quart_cognito.CognitoAuth()
    self.assertRaises(quart_cognito.CognitoAuthError, ca.get_token)

  def test_with_prefix_empty_string(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : ''})

    get_mock = Mock(return_value='Something')
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    quart_cognito.request = request_mock
    ca = quart_cognito.CognitoAuth()
    result = ca.get_token()
    self.assertEqual('Something',result)
  
  def test_with_prefix_none(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : None})

    get_mock = Mock(return_value='Something')
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    quart_cognito.request = request_mock
    ca = quart_cognito.CognitoAuth()
    result = ca.get_token()
    self.assertEqual('Something',result)

  def test_without_prefix_malformed(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : None})

    get_mock = Mock(return_value='Something Else')
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    quart_cognito.request = request_mock
    ca = quart_cognito.CognitoAuth()
    self.assertRaises(quart_cognito.CognitoAuthError, ca.get_token)

  def test_without_prefix_missing(self):
    quart_cognito._cog = objectview({'jwt_header_name' :'Authorization',
                          'jwt_header_prefix' : None})

    get_mock = Mock(return_value=None)
    request_mock = objectview({'headers': objectview({'get': get_mock})})
    quart_cognito.request = request_mock
    ca = quart_cognito.CognitoAuth()
    result = ca.get_token()
    self.assertIsNone(result)


  def test_group_permissions_decorator(self):
    quart_cognito.current_cognito_jwt = {'cognito:groups': ['admin', 'other']}
    @quart_cognito.cognito_group_permissions(['admin'])
    def some_func():
      return True
    self.assertTrue(some_func())

  def test_group_permissions_fail_if_not_in_group(self):
    quart_cognito.current_cognito_jwt = {'cognito:groups': ['other']}
    @quart_cognito.cognito_group_permissions(['admin'])
    def some_func():
      return True
    self.assertRaises(quart_cognito.CognitoAuthError, some_func)

  def test_group_permissions_fail_if_no_groups(self):
    quart_cognito.current_cognito_jwt = {'cognito:groups': []}
    @quart_cognito.cognito_group_permissions(['admin'])
    def some_func():
      return True
    self.assertRaises(quart_cognito.CognitoAuthError, some_func)

  def test_group_permissions_fail_if_groups_is_none(self):
    quart_cognito.current_cognito_jwt = {'cognito:groups': None}
    @quart_cognito.cognito_group_permissions(['admin'])
    def some_func():
      return True
    self.assertRaises(quart_cognito.CognitoAuthError, some_func) 

  def test_group_permissions_fail_if_no_group_attribute(self):
    quart_cognito.current_cognito_jwt = {'cognito:name': 'Something'}
    @quart_cognito.cognito_group_permissions(['admin'])
    def some_func():
      return True
    self.assertRaises(quart_cognito.CognitoAuthError, some_func)

  def test_identity_handler_late_init(self):
    ca = quart_cognito.CognitoAuth()

    # This throws an exception if self.identity_callback is not defined yet,
    # particularly if the property is defined by init_app which may not have
    # been called yet.
    @ca.identity_handler
    def handler(payload):
      return None

    self.assertEqual(ca.identity_callback, handler)
