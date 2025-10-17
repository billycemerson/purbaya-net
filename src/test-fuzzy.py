from rapidfuzz import fuzz

entity1 = "purbaya yudhi sadewa"
entity2 = "yudhi sadewa"

# Calculate the simpple fuzzy ratio
ratio = fuzz.ratio(entity1, entity2)
print(f"Fuzzy ratio: {ratio}")

# Calculate the partial ratio (useful for matching substrings)
partial_ratio = fuzz.partial_ratio(entity1, entity2)
print(f"Partial ratio: {partial_ratio}")