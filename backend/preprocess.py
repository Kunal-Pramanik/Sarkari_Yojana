"""
Data preprocessing pipeline.
Cleans and chunks the CSV into scheme documents.
"""
import pandas as pd
import re
import pickle
from config import config
from tqdm import tqdm

def clean_text(text: str) -> str:
    """Remove markdown artifacts, extra whitespace, list syntax."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\[\'|\'\]', '', text)        # remove python list syntax
    text = re.sub(r'#+\s*', '', text)             # remove markdown headers
    text = re.sub(r'\*+', '', text)               # remove bold markers
    text = re.sub(r'\n{3,}', '\n\n', text)        # collapse whitespace
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def clean_list_field(field: str) -> str:
    """Convert ['All'] or ['Gujarat', 'MP'] to 'All' or 'Gujarat, MP'."""
    if not isinstance(field, str):
        return "All"
    cleaned = re.sub(r"[\[\]']", "", field)
    return cleaned.strip()

def load_and_preprocess(csv_path: str) -> list[dict]:
    """Load CSV, clean all fields, return list of scheme dicts."""
    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path, encoding='utf-8', on_bad_lines='skip')
    print(f"Loaded {len(df)} rows.")

    # Rename columns for consistency
    df = df.rename(columns={
        'Scheme Name':         'name',
        'Short Title':         'short_title',
        'Category':            'category',
        'Level':               'level',
        'State':               'state',
        'Nodal Ministry':      'ministry',
        'Priority':            'priority',
        'Details':             'details',
        'Benefits':            'benefits',
        'Eligibility Criteria':'eligibility',
        'Application Process': 'application',
        'combined_text':       'combined',
    })

    schemes = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Preprocessing"):
        name = clean_text(str(row.get('name', '')))
        if not name or name == 'nan':
            continue

        scheme = {
            'id':          len(schemes),
            'name':        name,
            'short_title': clean_text(str(row.get('short_title', ''))),
            'category':    clean_list_field(str(row.get('category', ''))),
            'level':       clean_text(str(row.get('level', 'Central'))),
            'state':       clean_list_field(str(row.get('state', 'All'))),
            'ministry':    clean_text(str(row.get('ministry', ''))),
            'details':     clean_text(str(row.get('details', '')))[:800],
            'benefits':    clean_text(str(row.get('benefits', '')))[:600],
            'eligibility': clean_text(str(row.get('eligibility', '')))[:600],
            'application': clean_text(str(row.get('application', '')))[:400],
        }

        # Build a rich combined text for embedding
        scheme['embed_text'] = (
            f"Scheme: {scheme['name']}. "
            f"Category: {scheme['category']}. "
            f"State: {scheme['state']}. "
            f"Ministry: {scheme['ministry']}. "
            f"Details: {scheme['details']} "
            f"Benefits: {scheme['benefits']} "
            f"Eligibility: {scheme['eligibility']}"
        )

        schemes.append(scheme)

    print(f"Preprocessed {len(schemes)} valid schemes.")
    return schemes


if __name__ == "__main__":
    schemes = load_and_preprocess(config.DATA_PATH)
    with open(config.CHUNKS_PATH, 'wb') as f:
        pickle.dump(schemes, f)
    print(f"Saved {len(schemes)} schemes to {config.CHUNKS_PATH}")