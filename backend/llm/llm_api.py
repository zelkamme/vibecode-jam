import hashlib
import json
import redis
import time
import random


from tools import parse_json_list


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
    messages[0]["content"] = "/no_think" + messages[0]["content"] #TODO: Remove this
    messages_str = json.dumps(messages, sort_keys=True)
    key = f"llm_api:chat:{model}:{hashlib.sha256(messages_str.encode()).hexdigest()}"
    
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
        
    print("Using llm_api")
    # No cache hit - call llm_api

    if stream:
        full_response = []
        with client.chat.completions.stream(
            model=model,
            messages=messages,
            #max_tokens=400,
        ) as stream:
            for event in stream:
                if event.type == "chunk":
                    delta = getattr(event.chunk.choices[0].delta, "content", None)
                    if delta:
                        full_response.append(event.chunk.choices[0].delta) #print(delta, end="", flush=True)
                    #yield chunk
                    r.setex(key, ttl, ''.join(full_response))    
                elif event.type == "message.completed":
                    full_response.append("\n")
    
    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            #max_tokens=256,
        )
        response_str = str(response.choices[0].message.content)
        #print(response_str)
        r.setex(key, ttl, response_str)
        yield from [{'message': {'content': response_str}}]

def common_llm_call(prompt, llm_api, redis_host, redis_port, model="qwen3-32b-awq"):
    stream = cached_chat(
        client=llm_api,
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        redis_host=redis_host,
        redis_port=redis_port,
        stream=False,
        illusion=False,
        use_cache=True,
    )
    
    result = []
    for chunk in stream:
        result.append(chunk['message']['content'])
    
    return result

def common_list_parser(prompt, llm_api, redis_host, redis_port, model="qwen3-32b-awq"):
    stream = cached_chat(
        client=llm_api,
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        redis_host=redis_host,
        redis_port=redis_port,
        stream=False,
        illusion=False,
        use_cache=True,
    )
    
    result = []
    for chunk in stream:
        result.append(chunk['message']['content'])
    
    result = parse_json_list(result[0])
    return result