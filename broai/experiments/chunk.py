import re
from typing import List
from broai.experiments.utils import experiment
from broai.interface import Context

@experiment
def split_markdown(markdown_text: str) -> List[str]:
    headings = re.findall(r'^(#+)', markdown_text, re.MULTILINE)

    # Get the maximum number of '#' found
    max_hashes = max(map(len, headings), default=0)
    print(f"Markdown headings: max({max_hashes})")
    # using % method works but f string didn't
    # retmember the pattern must not be space inside {1,&d}
    pattern = r'\n#{1,%d} ' % max_hashes
    
    result = re.split(pattern, markdown_text)
    return result

@experiment
def consolidate_markdown(chunks: List[str]) -> List[str]:
    consolidated = []
    max_len = len(chunks)
    idx = 0
    chunk_size = 10

    while idx < max_len:
        current_chunk = chunks[idx]

        # Safe check for the last element
        if idx == max_len - 1:
            consolidated.append(current_chunk)
            break

        elif len(current_chunk.split(" ")) < chunk_size:
            # Only merge if there's a next chunk
            next_chunk = chunks[idx + 1] if idx + 1 < max_len else ''
            consolidated.append(current_chunk + "\n" + next_chunk)
            idx += 2
        else:
            consolidated.append(current_chunk)
            idx += 1

    return consolidated

def clean_text(text:str) -> str:
    # Remove the <span> tag and any content inside it
    result = re.sub(r'<span.*?</span>', '', text).strip()
    return result

@experiment
def get_markdown_sections(chunks:List[str]) -> List[str]:
    sections = []
    for enum, chunk in enumerate(chunks):
        # print(enum, clean_text(chunk.split("\n")[0]), len(chunk.split(" ")))
        # print(clean_text(chunk.split("\n")[0]), len(chunk.split(" ")))
        sections.append(clean_text(chunk.split("\n")[0]))
    return sections

@experiment
def split_overlap(contexts:List[Context], max_tokens:int=500, overlap:int=150) -> List[Context]:
    new_contexts:List[Context] = []
    for context in contexts:
        data_content = context.context
        tokens = data_content.split(" ")
        max_len = len(tokens)
        if max_len <= max_tokens:
            new_contexts.append(context)
        else:
            start_idx = 0
            end_idx = max_tokens
            while True:
                new_contexts.append(
                    Context(
                        context=" ".join(tokens[start_idx:end_idx]),
                        metadata=context.metadata
                    )
                )
                if end_idx > max_len:
                    break
                start_idx = end_idx - overlap
                end_idx = start_idx + max_tokens
    for idx in range(len(new_contexts)):
        metadata = new_contexts[idx].metadata.copy()
        metadata['sequence'] = idx
        new_contexts[idx].metadata = metadata
    return new_contexts

def which_section(text:str) -> str:
    if re.search(r"(abstract|abstracts)\n", text.lower()):
        return "abstract"
    if re.search(r"(introduction|background)\n", text.lower()):
        return "introduction"
    if re.search(r"(methodology|method|methods|experiment|experiments)\n", text.lower()):
        return "methodology"
    if re.search(r"(conclusion|discussion|summary)\n", text.lower()):
        return "conclusion"
    if re.search(r"(reference|references|bibliography|works cited|citations|cited works)\n", text.lower()):
        return "reference"
    return "others"

def chunk_chunks(chunks:List[str]) -> None:
    for enum, chunk in enumerate(chunks):
        tokens = chunk.split(" ")
        print(f"[{enum}] | tokens: {len(tokens)} | chars: {len(chunk)}")