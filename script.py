import fitz
import sys
import argparse
import logging
import os
from typing import List

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

def create_booklet(input_pdf: str, output_pdf: str, x_adjust: int, y_adjust: int, skip_count: int) -> None:
    """
    Creates a booklet-formatted PDF with column labels preserving the original orientation.
    
    The process includes adding blank pages to ensure the total is a multiple of 4,
    determining the booklet order, and placing page numbers after an initial skip.
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
        if i < len(booklet_order):
            safe_show_pdf_page(
                sheet,
                fitz.Rect(landscape_size[0] / 2, 0, landscape_size[0], landscape_size[1]),
                doc, booklet_order[i] - 1
            )
            if i >= skip_count:
                page_num = booklet_order[i] - (skip_count - 2)
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
            if i + 1 >= skip_count:
                page_num = booklet_order[i + 1] - (skip_count - 2)
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
            if i + 2 >= skip_count:
                page_num = booklet_order[i + 2] - (skip_count - 2)
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
            if i + 3 >= skip_count:
                page_num = booklet_order[i + 3] - (skip_count - 2)
                sheet.insert_textbox(
                    left_num_rect, str(page_num),
                    fontsize=16, fontname="times-roman", color=(0, 0, 0), align="center"
                )

    try:
        new_doc.save(output_pdf)
        logger.info("Booklet PDF saved as %s", output_pdf)
    except Exception as e:
        logger.error("Failed to save output PDF: %s", e)
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a booklet formatted PDF.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to the output booklet PDF file.")
    parser.add_argument("--x-adjust", type=int, default=7,
                        help="Horizontal shift for textbox placement (default: 7)")
    parser.add_argument("--y-adjust", type=int, default=25,
                        help="Vertical shift for textbox placement (default: 25)")
    parser.add_argument("--skip-count", type=int, default=5,
                        help="How many initial placements to skip numbering (default: 5)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite the output file if it already exists")
    args = parser.parse_args()

    # Check if the output file already exists and confirm overwrite.
    if os.path.exists(args.output_pdf) and not args.overwrite:
        response = input(f"Output file '{args.output_pdf}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            logger.info("Exiting without overwriting output file.")
            sys.exit(0)

    create_booklet(args.input_pdf, args.output_pdf, args.x_adjust, args.y_adjust, args.skip_count)

if __name__ == "__main__":
    main()
