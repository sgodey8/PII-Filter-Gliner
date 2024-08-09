#use dataset1 for this code

import json
import re
import spacy

class PIIFilter:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def remove_dates(self, text):
        text = re.sub(r'\b\d{1,2}[- /.]\d{1,2}[- /.]\d{2,4}\b', '<FILTERED>', text)
        text = re.sub(r'\b\d{1,2}[- /.](January|February|March|April|May|June|July|August|September|October|November|December)[- /.]?\d{0,4}\b', '<DATE>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d{1,2}[- /.](Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[- /.]?\d{0,4}\b', '<DATE>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b', '<DATE>', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}\b', '<DATE>', text, flags=re.IGNORECASE)
        return text

    def remove_email(self, text):
        return re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w{2,6}\b', '<FILTERED>', text)

    def remove_postal_codes(self, text):
        return re.sub(r'\b\d{5}(-\d{4})?\b', '<FILTERED>', text)

    def remove_social_media_handles(self, text):
        return re.sub(r'@\w+', "<FILTERED>", text)

    def remove_urls(self, text):
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '<FILTERED>', text)

    def remove_ssn(self, text):
        ssn_pattern = r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
        return re.sub(ssn_pattern, '<FILTERED>', text)

    def remove_credit_card(self, text):
        cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        return re.sub(cc_pattern, '<FILTERED>', text)

    def remove_credit_card_numbers(self, text):
        cc_pattern = r'\b\d{16}\b'
        return re.sub(cc_pattern, '<FILTERED>', text)

    def remove_ip_addresses(self, text):
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return re.sub(ip_pattern, '<FILTERED>', text)

    def remove_phone_numbers(self, text):
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        return re.sub(phone_pattern, '<FILTERED>', text)

    def remove_names(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                text = text.replace(ent.text, "<FILTERED>")
        return text

    def remove_organizations(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                text = text.replace(ent.text, "<FILTERED>")
        return text

    def remove_locations(self, text):
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                text = text.replace(ent.text, "<FILTERED>")
        return text

    def filter(self, inputtext):
        text = self.remove_dates(inputtext)
        text = self.remove_email(text)
        text = self.remove_postal_codes(text)
        text = self.remove_names(text)
        text = self.remove_organizations(text)
        text = self.remove_locations(text)
        text = self.remove_social_media_handles(text)
        text = self.remove_urls(text)
        text = self.remove_ssn(text)
        text = self.remove_credit_card(text)
        text = self.remove_credit_card_numbers(text)
        text = self.remove_ip_addresses(text)
        text = self.remove_phone_numbers(text)
        return text

def char_to_token_index(char_index, tokenized_text):
    token_index = 0
    char_count = 0
    for token in tokenized_text:
        if char_count + len(token) > char_index:
            return token_index
        char_count += len(token) + 1  # +1 for the space
        token_index += 1
    return token_index

def calculate_metrics(true_entities, filtered_text, original_text):
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    filtered_tokens = filtered_text.split()
    original_tokens = original_text.split()

    for start, end, label in true_entities:
        # Expand the search range further
        search_start = max(0, start - 3)
        search_end = min(len(filtered_tokens), end + 4)

        if any("<FILTERED>" in filtered_tokens[i] for i in range(search_start, search_end)):
            true_positives += 1
        else:
            false_negatives += 1

    for i, token in enumerate(filtered_tokens):
        if "<FILTERED>" in token:
            # Check if this filtered token corresponds to any true entity
            if not any(start - 2 <= i <= end + 2 for start, end, _ in true_entities):
                false_positives += 1

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

def parse_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    parsed_data = []
    pii_filter = PIIFilter()
    total_metrics = {'true_positives': 0, 'false_positives': 0, 'false_negatives': 0}

    for item in data:
        original_text = " ".join(item['tokenized_text'])
        filtered_text = pii_filter.filter(original_text)

        metrics = calculate_metrics(item['ner'], filtered_text, original_text)
        for key in total_metrics:
            total_metrics[key] += metrics[key]

        parsed_item = {
            'original_text': original_text,
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
