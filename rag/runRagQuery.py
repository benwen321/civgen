import numpy as np
from redis.commands.search.query import Query
import redis
from redis.commands.search.field import (
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv
client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
load_dotenv(dotenv_path="../.env")
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def directQuery(query_text,k):
    return textToVectorQuery(query_text,k=5)




def textToVectorQuery(query_text, model="text-embedding-3-large", k=5):
    # 1. Encode query (keep this the same)
    query_vector = np.array(
        openai_client.embeddings.create(
            input=query_text,
            model=model
        ).data[0].embedding, 
        dtype=np.float32
    )

    # 2. Update query to match schema fields
    query = (
        Query(f'(*)=>[KNN {k} @vector $query_vector AS vector_score]')
        .sort_by('vector_score')
        .return_fields(
            'vector_score', 
            'url',         # From TextField("$.url")
            'title',       # From TextField("$.title")
            'text_content',# From TextField("$.text_content")
            'attachment_paths',  # From TextField("$.attachments.*")
            'page'
        )
        .dialect(2)
    )

    return query, query_vector

def getRedisClient():
    return client


def runRagQuery(client, data_path,query,query_vector):
# 3. Execute search (keep the same)
    result = client.ft(f'idx:{data_path}_vss').search(
        query,
        {'query_vector': query_vector.tobytes()}
    )

    # 4. Process results with schema-aligned fields
    # for doc in result.docs:
        # print(doc)
        # print(f"""
        # Score: {doc.vector_score}
        # URL: {doc.url}
        # Content: {doc.text_content}
        # Attachments: {doc.attachment_paths}
        # Page: {doc.page}
        # """)
    return result
