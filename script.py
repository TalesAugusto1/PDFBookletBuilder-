import fitz
import sys
import argparse
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for configuration
X_ADJUST = 7   # Horizontal shift for textbox placement
Y_ADJUST = 25    # Vertical shift for textbox placement
SKIP_COUNT = 5   # How many initial placements to skip numbering

def add_blank_pages(doc: fitz.Document) -> None:
    """Adds blank pages until the total count is a multiple of 4."""
    while doc.page_count % 4 != 0:
        doc.insert_page(-1)

def get_booklet_order(page_count: int) -> List[int]:
    """
    Returns the correct page order for booklet printing with two pages per sheet.
    
    The function calculates the ordering for printing such that when the pages are folded,
    they appear in the correct sequence.
    """
    booklet_order = []
    left = page_count
    right = 1
    
    while right < left:
        booklet_order.append(right)  # First page (right side)
        booklet_order.append(left)   # Last page (left side)
        right += 1
        left -= 1
        
        if right < left:
            booklet_order.append(left)   # Second-last page (left side, next sheet)
            booklet_order.append(right)    # Second page (right side, next sheet)
            right += 1
            left -= 1
            
    return booklet_order

def safe_show_pdf_page(sheet: fitz.Page, rect: fitz.Rect, doc: fitz.Document, pagenum: int) -> None:
    """
    Renders a page safely, ignoring empty pages.
    
    If the page is empty, a warning is logged instead of stopping the program.
    """
    try:
        sheet.show_pdf_page(rect, doc, pagenum)
    except ValueError as e:
        if "nothing to show" in str(e):
            logger.warning("Page %d is empty, skipping.", pagenum + 1)
        else:
            raise

def create_booklet(input_pdf: str, output_pdf: str) -> None:
    """
    Creates a booklet-formatted PDF with column labels preserving the original orientation.
    
    The process includes adding blank pages to ensure the total is a multiple of 4,
    determining the booklet order, and placing page numbers after an initial skip.
    """
    doc = fitz.open(input_pdf)
    
    if doc.page_count == 0:
        logger.error("Input PDF has no pages.")
        sys.exit(1)
    
    add_blank_pages(doc)
    booklet_order = get_booklet_order(doc.page_count)
    logger.info("Booklet order: %s", booklet_order)
    
    new_doc = fitz.open()
    page_width, page_height = fitz.paper_size("a4")
    landscape_size = (page_height, page_width)  # A4 in landscape orientation

    # Define positions for numbering text boxes
    y_start = landscape_size[1] - 80 + Y_ADJUST
    y_end = landscape_size[1] - 50 + Y_ADJUST
    left_center_x = landscape_size[0] / 4 + X_ADJUST
    right_center_x = 3 * landscape_size[0] / 4 + X_ADJUST
    left_num_rect = fitz.Rect(left_center_x - 20, y_start, left_center_x + 20, y_end)
    right_num_rect = fitz.Rect(right_center_x - 20, y_start, right_center_x + 20, y_end)
    
    # Process booklet_order in blocks of 4.
    for i in range(0, len(booklet_order), 4):
        # First new page (contains two placements)
        sheet = new_doc.new_page(width=landscape_size[0], height=landscape_size[1])
        
        if i < len(booklet_order):
            safe_show_pdf_page(
                sheet,
                fitz.Rect(landscape_size[0] / 2, 0, landscape_size[0], landscape_size[1]),
                doc, booklet_order[i] - 1
            )
            if i >= SKIP_COUNT:
                page_num = booklet_order[i] - (SKIP_COUNT - 2)
                sheet.insert_textbox(
                    right_num_rect, str(page_num),
                    fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center"
                )
        
        if i + 1 < len(booklet_order):
            safe_show_pdf_page(
                sheet,
                fitz.Rect(0, 0, landscape_size[0] / 2, landscape_size[1]),
                doc, booklet_order[i + 1] - 1
            )
            if i + 1 >= SKIP_COUNT:
                page_num = booklet_order[i + 1] - (SKIP_COUNT - 2)
                sheet.insert_textbox(
                    left_num_rect, str(page_num),
                    fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center"
                )
        
        # Second new page (contains two placements)
        sheet = new_doc.new_page(width=landscape_size[0], height=landscape_size[1])
        
        if i + 2 < len(booklet_order):
            safe_show_pdf_page(
                sheet,
                fitz.Rect(landscape_size[0] / 2, 0, landscape_size[0], landscape_size[1]),
                doc, booklet_order[i + 2] - 1
            )
            if i + 2 >= SKIP_COUNT:
                page_num = booklet_order[i + 2] - (SKIP_COUNT - 2)
                sheet.insert_textbox(
                    right_num_rect, str(page_num),
                    fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center"
                )
        
        if i + 3 < len(booklet_order):
            safe_show_pdf_page(
                sheet,
                fitz.Rect(0, 0, landscape_size[0] / 2, landscape_size[1]),
                doc, booklet_order[i + 3] - 1
            )
            if i + 3 >= SKIP_COUNT:
                page_num = booklet_order[i + 3] - (SKIP_COUNT - 2)
                sheet.insert_textbox(
                    left_num_rect, str(page_num),
                    fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center"
                )

    # Save the final document once after processing all pages.
    new_doc.save(output_pdf)
    logger.info("Booklet PDF saved as %s", output_pdf)

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a booklet formatted PDF.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to the output booklet PDF file.")
    args = parser.parse_args()
    
    create_booklet(args.input_pdf, args.output_pdf)

if __name__ == "__main__":
    main()
