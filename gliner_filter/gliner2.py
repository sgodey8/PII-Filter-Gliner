#use dataset2 for this one

import json
from gliner import GLiNER
import re

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

def print_entities(entities, text):
    for start, end, label in sorted(entities, key=lambda x: x[0], reverse=True):
        text = text[:start] + f"<{label}>" + text[end:]
    return text

def parse_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    parsed_data = []
    model = GLiNER.from_pretrained("urchade/gliner_large-v2.1")
    total_metrics = {'true_positives': 0, 'false_positives': 0, 'false_negatives': 0}

    labels = [
        "circuits.name", "circuits.location", "circuits.country",
        "constructors.name",
        "drivers.name",
        "races.name", "races.year", "date",
        "nationality"


    ]

    for item in data:
        original_text = item['question']
        stripped_text = item['stripped_question']

        # Predict entities
        predicted_entities_raw = model.predict_entities(original_text, labels, threshold=0.7)
        predicted_entities = [(e['start'], e['end'], e['label']) for e in predicted_entities_raw]

        # Extract true entities from stripped question
        true_entities = find_placeholder_indices(stripped_text)

        filtered_text = print_entities(predicted_entities, original_text)

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
file_path = 'datasets/val2.json'
result, overall_metrics = parse_json_data(file_path)

print("\nOverall Metrics:")
print(json.dumps(overall_metrics, indent=2))

for item in result[:5]:  # Print only the first 5 items
    print("\nOriginal Text:", item['original_text'])
    print("Stripped Text:", item['stripped_text'])
    print("Filtered Text:", item['filtered_text'])
    print("True Entities:", item['true_entities'])
    print("Predicted Entities:", item['predicted_entities'])
    print("Metrics:", item['metrics'])
