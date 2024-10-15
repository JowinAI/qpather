from aiocache import Cache

cache = Cache(Cache.MEMORY)

async def cache_set(key, value, expiry):
    await cache.set(key, value, ttl=expiry)

async def cache_get(key):
    return await cache.get(key)

async def cache_delete(key):
    await cache.delete(key)

