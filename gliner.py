

import json
from gliner import GLiNER
import numpy as np




def char_to_token_index(char_index, tokenized_text):
    token_index = 0
    char_count = 0
    for token in tokenized_text:
        if char_count + len(token) > char_index:
            return token_index
        char_count += len(token) + 1  # +1 for the space
        token_index += 1
    return token_index


def calculate_metrics(true_entities, predicted_entities, tokenized_text):
    true_positives = 0
    false_positives = 0
    false_negatives = 0


    true_spans = set((e[0], e[1], e[2]) for e in true_entities)


    # Convert predicted entities to token-based indices
    pred_spans = set()
    for p in predicted_entities:
        start_token = char_to_token_index(p['start'], tokenized_text)
        end_token = char_to_token_index(p['end'] - 1, tokenized_text)  # -1 because end is exclusive
        pred_spans.add((start_token, end_token, p['label']))


    for pred_span in pred_spans:
        if any(true_span[0] <= pred_span[0] and true_span[1] >= pred_span[1] and true_span[2] == pred_span[2] for true_span in true_spans):
            true_positives += 1
        else:
            false_positives += 1


    for true_span in true_spans:
        if not any(pred_span[0] <= true_span[0] and pred_span[1] >= true_span[1] and pred_span[2] == true_span[2] for pred_span in pred_spans):
            false_negatives += 1


    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0


    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
def print_entities(entities, text):
    for entity in sorted(entities, key=lambda x: x['start'], reverse=True):
        start, end = entity['start'], entity['end']
        text = text[:start] + '<FILTERED>' + text[end:]
    return text


def parse_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)


    parsed_data = []
    model = GLiNER.from_pretrained("urchade/gliner_large-v2.1")
    total_metrics = {'true_positives': 0, 'false_positives': 0, 'false_negatives': 0}


    for item in data:
        original_text = item['tokenized_text']
        text = " ".join(original_text)


        # Extract labels for this specific item
        labels = list(set(entity[2] for entity in item['ner']))


        entities = model.predict_entities(text, labels, threshold=0.45)


        # Convert predicted entities to token-based indices for display
        token_based_entities = []
        for e in entities:
            start_token = char_to_token_index(e['start'], original_text)
            end_token = char_to_token_index(e['end'] - 1, original_text)
            token_based_entities.append([start_token, end_token, e['label']])


        filtered_text = print_entities(entities, text)


        metrics = calculate_metrics(item['ner'], entities, original_text)
        for key in total_metrics:
            total_metrics[key] += metrics[key]


        parsed_item = {
            'original_text': text,
            'filtered_text': filtered_text,
            'metrics': metrics
        }
        parsed_data.append(parsed_item)


    total_true_positives = total_metrics['true_positives']
    total_false_positives = total_metrics['false_positives']
    total_false_negatives = total_metrics['false_negatives']


    overall_precision = total_true_positives / (total_true_positives + total_false_positives) if (total_true_positives + total_false_positives) > 0 else 0
    overall_recall = total_true_positives / (total_true_positives + total_false_negatives) if (total_true_positives + total_false_negatives) > 0 else 0
    overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0


    overall_metrics = {
        'precision': overall_precision,
        'recall': overall_recall,
        'f1': overall_f1
    }


    return parsed_data, overall_metrics


# Example usage
file_path = 'datasets/first_10_tokens.json'
result, overall_metrics = parse_json_data(file_path)


print("\nOverall Metrics:")
print(json.dumps(overall_metrics, indent=2))


for item in result:
    print("\nOriginal Text:", item['original_text'])
    print("Filtered Text:", item['filtered_text'])
    print("Metrics:", item['metrics'])
