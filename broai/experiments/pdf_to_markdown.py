from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from broai.experiments.utils import experiment

@experiment
def pdf_to_markdown(pdf_path: str) -> str:

    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )
    rendered = converter(pdf_path)
    markdown_text, _, images = text_from_rendered(rendered)
    return markdown_text, images