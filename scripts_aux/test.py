import redis

r = redis.Redis()

r.mset({'Croatia':'Zagreb','Bahamas':'Nassau'})

aer = r.get('Bahamas')