"""
Public Dataset Loader for Proto RAG Pipeline
Uses the real pix2code dataset from HuggingFace: N0zomu/pix2code-data
Source: https://github.com/tonybeltramelli/pix2code
HuggingFace: https://huggingface.co/datasets/N0zomu/pix2code-data

Total: 1573 training samples + 175 test samples = 1748 real DSL-HTML pairs
"""

import logging
import re

logger = logging.getLogger(__name__)

DATASET_NAME = "N0zomu/pix2code-data"
DATASET_REF = "https://huggingface.co/datasets/N0zomu/pix2code-data"
ORIGINAL_REF = "https://github.com/tonybeltramelli/pix2code"

DSL_DESCRIPTIONS = {
    "header": "navigation header bar",
    "btn-active": "active navigation button",
    "btn-inactive": "inactive navigation button",
    "row": "horizontal content row",
    "single": "full-width single column layout",
    "double": "two-column layout",
    "quadruple": "four-column grid layout",
    "big-title": "large heading text",
    "small-title": "small subheading text",
    "text": "paragraph text content",
    "btn-green": "green action button",
    "btn-orange": "orange warning button",
    "btn-red": "red danger button"
}


def parse_pix2code_sample(content: str):
    """Parse a single pix2code sample into DSL and HTML components."""
    parts = content.split('|>')
    
    dsl_code = ""
    html_code = ""
    
    for i, part in enumerate(parts):
        stripped = part.strip()
        if stripped.startswith('header') or stripped.startswith('row'):
            dsl_code = stripped.rstrip('<|assistant')
        if stripped.startswith('<html>') or stripped.startswith(' <html>'):
            html_code = stripped.rstrip('<|')
    
    return dsl_code.strip(), html_code.strip()


def dsl_to_description(dsl_code: str) -> str:
    """Convert pix2code DSL tokens into a human-readable layout description."""
    description_parts = []
    
    lines = dsl_code.strip().split('\n')
    
    has_header = False
    nav_btn_count = 0
    row_count = 0
    current_row_type = None
    content_types = set()
    
    for line in lines:
        line = line.strip().rstrip(',')
        
        if line.startswith('header'):
            has_header = True
        elif 'btn-active' in line or 'btn-inactive' in line:
            nav_btn_count += 1
        elif line.startswith('row'):
            row_count += 1
        elif line.startswith('single'):
            current_row_type = "full-width single column"
        elif line.startswith('double'):
            current_row_type = "two-column"
        elif line.startswith('quadruple'):
            current_row_type = "four-column grid"
        
        for token in DSL_DESCRIPTIONS:
            if token in line and token not in ('header', 'row', 'single', 'double', 'quadruple'):
                if 'btn' in token and 'nav' not in line:
                    content_types.add(DSL_DESCRIPTIONS[token])
                elif 'title' in token or token == 'text':
                    content_types.add(DSL_DESCRIPTIONS[token])
    
    if has_header:
        description_parts.append(f"Navigation header with {nav_btn_count} menu buttons")
    
    if row_count > 0:
        description_parts.append(f"{row_count} content row(s)")
    
    if current_row_type:
        description_parts.append(f"{current_row_type} layout")
    
    if content_types:
        description_parts.append(f"containing {', '.join(content_types)}")
    
    if not description_parts:
        description_parts.append("Web UI layout with Bootstrap components")
    
    return ". ".join(description_parts) + "."


def categorize_layout(dsl_code: str) -> str:
    """Categorize a DSL layout into a semantic category."""
    has_header = 'header' in dsl_code
    has_single = 'single' in dsl_code
    has_double = 'double' in dsl_code
    has_quad = 'quadruple' in dsl_code
    has_btn = 'btn-green' in dsl_code or 'btn-orange' in dsl_code or 'btn-red' in dsl_code
    has_title = 'big-title' in dsl_code
    has_text = 'text' in dsl_code
    row_count = dsl_code.count('row')
    
    if has_header and has_single and has_title and has_btn and row_count <= 2:
        return "hero_section"
    elif has_quad and row_count >= 2:
        return "grid_layout"
    elif has_double and row_count >= 1:
        return "two_column_layout"
    elif has_single and has_title and has_text:
        return "content_page"
    elif has_header and has_quad:
        return "dashboard_layout"
    elif has_header and not has_single and not has_double:
        return "navigation_bar"
    elif has_btn and has_text:
        return "form_layout"
    else:
        return "web_layout"


def load_public_dataset():
    """
    Load the real pix2code public dataset from HuggingFace.
    Returns list of processed samples with DSL, HTML, description, and category.
    """
    from datasets import load_dataset
    
    logger.info(f"Loading public dataset: {DATASET_NAME}")
    
    # Load both train and test splits
    train_ds = load_dataset(DATASET_NAME, split='train')
    test_ds = load_dataset(DATASET_NAME, split='test')
    
    logger.info(f"Loaded {len(train_ds)} train + {len(test_ds)} test samples")
    
    processed = []
    
    for split_name, split_data in [("train", train_ds), ("test", test_ds)]:
        for i, sample in enumerate(split_data):
            content = sample['content']
            dsl_code, html_code = parse_pix2code_sample(content)
            
            if not dsl_code or not html_code:
                continue
            
            description = dsl_to_description(dsl_code)
            category = categorize_layout(dsl_code)
            
            processed.append({
                "id": f"pix2code_{split_name}_{i:04d}",
                "category": category,
                "description": description,
                "code": html_code,
                "dsl": dsl_code,
                "framework": "HTML/Bootstrap",
                "source": "pix2code",
                "split": split_name
            })
    
    logger.info(f"Processed {len(processed)} valid samples from pix2code dataset")
    return processed


def get_dataset_info():
    """Get metadata about the public dataset without loading it."""
    return {
        "dataset_name": "pix2code (Tony Beltramelli, 2017)",
        "huggingface_id": DATASET_NAME,
        "description": "Public dataset of 1748 web UI screenshots with paired DSL code and generated HTML. Originally created for the pix2code paper on generating code from GUI screenshots.",
        "reference_paper": "https://arxiv.org/abs/1705.07962",
        "reference_github": ORIGINAL_REF,
        "reference_huggingface": DATASET_REF,
        "total_train": 1573,
        "total_test": 175,
        "total_samples": 1748,
        "framework": "HTML/Bootstrap",
        "source": "pix2code"
    }


if __name__ == "__main__":
    dataset = load_public_dataset()
    print(f"Loaded {len(dataset)} samples from pix2code public dataset")
    
    categories = {}
    for item in dataset:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"Categories: {categories}")
    print(f"\nSample 0:")
    print(f"  ID: {dataset[0]['id']}")
    print(f"  Category: {dataset[0]['category']}")
    print(f"  Description: {dataset[0]['description']}")
    print(f"  DSL: {dataset[0]['dsl'][:100]}...")
    print(f"  HTML: {dataset[0]['code'][:100]}...")
