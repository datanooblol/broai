import re

def clean_up_markdown_link(markdown):
    cleaned_text = re.sub(r'!\[.*?\]\(.*?\)|\[(.*?)\]\(.*?\)', r'\1', markdown)
    return cleaned_text