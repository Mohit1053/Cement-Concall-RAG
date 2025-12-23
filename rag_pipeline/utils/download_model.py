"""
Download embedding model with SSL workaround
"""
import ssl
import os

# Disable SSL verification (for corporate proxies/firewalls)
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = ''

from sentence_transformers import SentenceTransformer

print("Downloading BAAI/bge-small-en-v1.5 model...")
print("(Disabling SSL verification due to network restrictions)")

model = SentenceTransformer('BAAI/bge-small-en-v1.5')

print(f"✓ Model downloaded successfully!")
print(f"  Dimension: {model.get_sentence_embedding_dimension()}")

# Test embedding
test_text = "This is a test sentence for cement industry analysis."
embedding = model.encode(test_text)
print(f"  Test embedding shape: {embedding.shape}")
print("\n✓ Model is ready to use!")
