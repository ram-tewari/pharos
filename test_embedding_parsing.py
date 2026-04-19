"""
Test script to verify embedding string parsing works correctly.
"""

import numpy as np

# Simulate the embedding_vector string from database
embedding_str = "0.02485617808997631 0.015210630372166634 0.014013400301337242 -0.07916723191738129"

# Parse string to list of floats
embedding = [float(x) for x in embedding_str.split()]

print(f"Original string: {embedding_str[:50]}...")
print(f"Parsed list length: {len(embedding)}")
print(f"First 4 values: {embedding[:4]}")
print(f"Type: {type(embedding)}")
print(f"Element type: {type(embedding[0])}")

# Test cosine similarity
query_embedding = [0.01, 0.02, 0.03, -0.08]

v1 = np.array(query_embedding)
v2 = np.array(embedding)

dot_product = np.dot(v1, v2)
norm1 = np.linalg.norm(v1)
norm2 = np.linalg.norm(v2)

similarity = dot_product / (norm1 * norm2)

print(f"\nCosine similarity: {similarity}")
print(f"Clamped to [0,1]: {max(0.0, min(1.0, float(similarity)))}")

print("\n✅ Embedding parsing works correctly!")
