import hashlib
import json
import redis
import time
import random


def stream_text_words_with_delay(text, min_delay=0.02, max_delay=0.10):
    words = text.split()
    for i, word in enumerate(words):
        # Add space after each word except the last one
        content = word + (" " if word != words[-1] else "")
        yield {'message': {'content': content}}
        
        # Add delay after each word except the last
        if i < len(words) - 1:
            time.sleep(random.uniform(min_delay, max_delay))

def cached_chat(client, model, messages, stream=False, redis_host="localhost", redis_port=6379, ttl=3600, illusion=True, use_cache=True):
    # Generate unique cache key
    messages_str = json.dumps(messages, sort_keys=True)
    key = f"ollama:chat:{model}:{hashlib.sha256(messages_str.encode()).hexdigest()}"
    
    # Connect to Redis
    r = redis.Redis(host=redis_host, port=redis_port, db=0)
    
    # Check cache
    cached = r.get(key)
    if cached and use_cache:
        response_str = cached.decode('utf-8')
        if stream and illusion:
            # illusion makes the cached data seem like it is generated on the LLM to the end user, but doesn't actually use the LLM, fetching answer from cache
            # Yield from the generator instead of returning it
            print("Using cache with generation illusion")
            yield from stream_text_words_with_delay(response_str)
            return
            
        else:
            print("Using cache")
            yield from [{'message': {'content': response_str}}]
            return
        
    print("Using ollama")
    # No cache hit - call Ollama
    response = client.chat(model=model, messages=messages, stream=stream)
    
    if stream:
        full_response = []
        for chunk in response:
            if 'message' in chunk:
                full_response.append(chunk['message']['content'])
            yield chunk
        # Cache the complete response
        r.setex(key, ttl, ''.join(full_response))
    else:
        response_str = str(response['message']['content'])
        #print(response_str)
        r.setex(key, ttl, response_str)
        yield from [{'message': {'content': response_str}}]