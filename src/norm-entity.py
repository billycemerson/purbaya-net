import pandas as pd
from rapidfuzz import fuzz, process

# Load cleaned NER data
data = pd.read_csv("../data/cleaned_ner_results.csv")

# Get unique entities
unique_entities = data['entity'].unique()
print(f"Total unique entities: {len(unique_entities)}")

# Treshold for fuzzy matching
THRESHOLD = 90

# Function to normalize entities using fuzzy matching
normalized_map = {}

for entity in unique_entities:
    if entity in normalized_map:
        continue
    
    # Get similar entity
    matches = [
        e for e in unique_entities
        if fuzz.ratio(entity, e) >= THRESHOLD
    ]

    # Select the representation
    canonical = max(matches, key=len)

    # Flag canonical
    for m in matches:
        normalized_map[m] = canonical

# Add new column
data['normalized_entity'] = data['entity'].map(normalized_map)

# Save result
data.to_csv("../data/normalized_entities.csv", index=False)
print(data.head())
print("Unique entities:", data['normalized_entity'].nunique())
print("Top entity:", data['normalized_entity'].value_counts())