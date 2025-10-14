import pandas as pd
import numpy as np


# Load NER data
data = pd.read_csv("../data/ner_results.csv")
print(data.head())

# Basic statistics
print("Number of records:", len(data))
print("Unique entities:", data['entity'].nunique())
print("Label distribution:\n", data['label'].value_counts())

# Cleaning, get only entity with label PER, NOR, and ORG
cleaned_data = data[data['label'].isin(['PER', 'NOR', 'ORG'])]

# Remove record with score less than 0.7
cleaned_data = cleaned_data[cleaned_data['score'] >= 0.7]

# Save cleaned data
cleaned_data.to_csv("../data/cleaned_ner_results.csv", index=False)

# See statistics of cleaned data
print("Cleaned data records:", len(cleaned_data))
print("Unique entities:", cleaned_data['entity'].nunique())
print("Cleaned label distribution:\n", cleaned_data['label'].value_counts())