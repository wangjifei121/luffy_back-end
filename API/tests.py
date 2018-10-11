from django.test import TestCase

# Create your tests here.
import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)

redis = redis.Redis(connection_pool=pool)

redis.delete('shopping_car_1_5')
ret = redis.keys()
print(ret)
