#use dataset2 for this code

import json
import re
import spacy

class PIIFilter:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def remove_dates(self, text):
        text = re.sub(r'\b\d{4}\b', '<races.year>', text)
        return text

    def remove_names(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                text = text.replace(ent.text, "<drivers.name>")
        return text

    def remove_locations(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                text = text.replace(ent.text, "<circuits.location>")
        return text

    def remove_race(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "EVENT":
                text = text.replace(ent.text, "<races.name>")
        return text

    def remove_nationalities(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "NORP":
                text = text.replace(ent.text, "<nationality>")
        return text

    def remove_organizations(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                text = text.replace(ent.text, "<circuits.name>")
        return text

    def remove_grand_prix(self, text):
        pattern = r'\b\w+(\s+\w+)* Grand Prix\b'
        return re.sub(pattern, '<races.name>', text)

    def filter(self, inputtext):
        text = self.remove_dates(inputtext)
        text = self.remove_names(text)
        text = self.remove_locations(text)
        text = self.remove_race(text)
        text = self.remove_nationalities(text)
        text = self.remove_organizations(text)
        text = self.remove_grand_prix(text)
        return text

def find_placeholder_indices(text):
    return [(m.start(), m.end(), m.group(1)) for m in re.finditer(r'<([^>]+)>', text)]

def calculate_metrics(true_entities, predicted_entities):
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    # Create sets of ranges for true and predicted entities
    true_ranges = set((start, end) for start, end, _ in true_entities)
    pred_ranges = set((start, end) for start, end, _ in predicted_entities)

    # Count true positives and false positives
    for pred_start, pred_end in pred_ranges:
        if any(true_start <= pred_end and pred_start <= true_end for true_start, true_end in true_ranges):
            true_positives += 1
        else:
            false_positives += 1

    # Count false negatives
    false_negatives = len(true_ranges) - true_positives

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0

    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def parse_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    parsed_data = []
    pii_filter = PIIFilter()
    total_metrics = {'true_positives': 0, 'false_positives': 0, 'false_negatives': 0}

    for item in data:
        original_text = item['question']
        stripped_text = item['stripped_question']

        filtered_text = pii_filter.filter(original_text)

        true_entities = find_placeholder_indices(stripped_text)
        predicted_entities = find_placeholder_indices(filtered_text)

        metrics = calculate_metrics(true_entities, predicted_entities)
        for key in total_metrics:
            total_metrics[key] += metrics[key]

        parsed_item = {
            'original_text': original_text,
            'stripped_text': stripped_text,
            'filtered_text': filtered_text,
            'true_entities': true_entities,
            'predicted_entities': predicted_entities,
            'metrics': metrics
        }
        parsed_data.append(parsed_item)

    total_samples = len(data)
    overall_precision = total_metrics['true_positives'] / (total_metrics['true_positives'] + total_metrics['false_positives']) if (total_metrics['true_positives'] + total_metrics['false_positives']) > 0 else 0
    overall_recall = total_metrics['true_positives'] / (total_metrics['true_positives'] + total_metrics['false_negatives']) if (total_metrics['true_positives'] + total_metrics['false_negatives']) > 0 else 0
    overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0

    overall_metrics = {
        'precision': overall_precision,
        'recall': overall_recall,
        'f1': overall_f1,
        'total_samples': total_samples,
        'total_true_positives': total_metrics['true_positives'],
        'total_false_positives': total_metrics['false_positives'],
        'total_false_negatives': total_metrics['false_negatives']
    }

    return parsed_data, overall_metrics

# Example usage
file_path = 'datasets/dataset2.json'
result, overall_metrics = parse_json_data(file_path)

print("\nOverall Metrics:")
print(json.dumps(overall_metrics, indent=2))

for item in result[:20]:  # Print only the first 5 items
    print("\nOriginal Text:", item['original_text'])
    print("Stripped Text:", item['stripped_text'])
    print("Filtered Text:", item['filtered_text'])
    print("True Entities:", item['true_entities'])
    print("Predicted Entities:", item['predicted_entities'])
    print("Metrics:", item['metrics'])
