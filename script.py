import fitz
import sys
import logging
import os
from typing import List

def transparent_input(prompt: str, default: str) -> str:
    """Displays input prompt with a transparent default value that reappears if erased."""
    user_input = input(f"{prompt} ({default} DEFAULT): ")
    return user_input.strip() if user_input.strip() != "" else default

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def create_booklet(input_pdf: str, output_pdf: str, x_adjust: int, y_adjust: int, skip_count: int,
                   left_page_x_adjust: float, right_page_x_adjust: float, page_y_adjust: float) -> None:
    """
    Creates a booklet-formatted PDF with column labels preserving the original orientation.
    
    The process includes adding blank pages to ensure the total is a multiple of 4,
    determining the booklet order, and placing page numbers after an initial skip.
    The positions for page placements are adjusted using the provided column adjustment parameters.
    """
    try:
        doc = fitz.open(input_pdf)
    except Exception as e:
        logger.error("Failed to open input PDF: %s", e)
        sys.exit(1)

    if doc.page_count == 0:
        logger.error("Input PDF has no pages.")
        sys.exit(1)

    add_blank_pages(doc)
    booklet_order = get_booklet_order(doc.page_count)
    logger.info("Booklet order: %s", booklet_order)
    
    new_doc = fitz.open()
    page_width, page_height = fitz.paper_size("a4")
    landscape_size = (page_height, page_width)  # A4 in landscape orientation

    # Define positions for numbering text boxes with user-provided adjustments
    y_start = landscape_size[1] - 80 + y_adjust
    y_end = landscape_size[1] - 50 + y_adjust
    left_center_x = landscape_size[0] / 4 + x_adjust
    right_center_x = 3 * landscape_size[0] / 4 + x_adjust
    left_num_rect = fitz.Rect(left_center_x - 20, y_start, left_center_x + 20, y_end)
    right_num_rect = fitz.Rect(right_center_x - 20, y_start, right_center_x + 20, y_end)
    
    # Process booklet_order in blocks of 4.
    for i in range(0, len(booklet_order), 4):
        # First new page (contains two placements)
        sheet = new_doc.new_page(width=landscape_size[0], height=landscape_size[1])
        # Define adjusted rectangles for page placements:
        right_rect = fitz.Rect((landscape_size[0] / 2) + right_page_x_adjust, 0 + page_y_adjust,
                               landscape_size[0] + right_page_x_adjust, landscape_size[1] + page_y_adjust)
        left_rect = fitz.Rect(0 + left_page_x_adjust, 0 + page_y_adjust,
                              (landscape_size[0] / 2) + left_page_x_adjust, landscape_size[1] + page_y_adjust)
        if i < len(booklet_order):
            safe_show_pdf_page(sheet, right_rect, doc, booklet_order[i] - 1)
            if i >= skip_count:
                page_num = booklet_order[i] - (skip_count - 2)
                sheet.insert_textbox(right_num_rect, str(page_num),
                                     fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center")
        if i + 1 < len(booklet_order):
            safe_show_pdf_page(sheet, left_rect, doc, booklet_order[i + 1] - 1)
            if i + 1 >= skip_count:
                page_num = booklet_order[i + 1] - (skip_count - 2)
                sheet.insert_textbox(left_num_rect, str(page_num),
                                     fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center")
        
        # Second new page (contains two placements)
        sheet = new_doc.new_page(width=landscape_size[0], height=landscape_size[1])
        if i + 2 < len(booklet_order):
            safe_show_pdf_page(sheet, right_rect, doc, booklet_order[i + 2] - 1)
            if i + 2 >= skip_count:
                page_num = booklet_order[i + 2] - (skip_count - 2)
                sheet.insert_textbox(right_num_rect, str(page_num),
                                     fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center")
        if i + 3 < len(booklet_order):
            safe_show_pdf_page(sheet, left_rect, doc, booklet_order[i + 3] - 1)
            if i + 3 >= skip_count:
                page_num = booklet_order[i + 3] - (skip_count - 2)
                sheet.insert_textbox(left_num_rect, str(page_num),
                                     fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center")

    try:
        new_doc.save(output_pdf)
        logger.info("Booklet PDF saved as %s", output_pdf)
    except Exception as e:
        logger.error("Failed to save output PDF: %s", e)
        sys.exit(1)

def main() -> None:
    # Interactive input for parameters
    input_pdf = input("Enter input PDF path: ")
    output_pdf = input("Enter output PDF path: ")
    x_adjust = int(transparent_input("Enter horizontal shift for textbox placement", "7"))
    y_adjust = int(transparent_input("Enter vertical shift for textbox placement", "25"))
    skip_count = int(transparent_input("Enter how many initial placements to skip numbering", "5"))
    left_page_x_adjust = float(transparent_input("Enter horizontal offset for left page placement", "0"))
    right_page_x_adjust = float(transparent_input("Enter horizontal offset for right page placement", "0"))
    page_y_adjust = float(transparent_input("Enter vertical offset for page placements", "0"))
    overwrite = input("Overwrite existing output file? (y/n) (n DEFAULT): ") or "n"
    
    if os.path.exists(output_pdf) and overwrite.lower() != 'y':
        logger.info("Exiting without overwriting output file.")
        sys.exit(0)
    
    create_booklet(input_pdf, output_pdf, x_adjust, y_adjust, skip_count,
                   left_page_x_adjust, right_page_x_adjust, page_y_adjust)

if __name__ == "__main__":
    main()
