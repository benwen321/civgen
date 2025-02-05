import json
import redis

r = redis.Redis(
    host='redis-16517.c282.east-us-mz.azure.redns.redis-cloud.com',
    port=16517,
    decode_responses=True,
    username="default",
    password="rhfQ1KPEvR5JshIh33LoQiiB4D9xL7Bg",
)

client = redis.Redis(host='redis-16517.c282.east-us-mz.azure.redns.redis-cloud.com', 
                     password="rhfQ1KPEvR5JshIh33LoQiiB4D9xL7Bg", 
                     port=16517, 
                     decode_responses=True
                     )

with open('sections.json', 'r') as file:
  sections = json.load(file)

pipeline = client.pipeline()
for i, section in enumerate(sections, start=1):
    redis_key = f"section:{i:05}"
    pipeline.json().set(redis_key, "$", section)
res = pipeline.execute()