import fitz
import logging
import sys
from typing import List, Tuple

def add_blank_pages(doc: fitz.Document) -> None:
    """Adds blank pages until the total count is a multiple of 4."""
    while doc.page_count % 4 != 0:
        doc.insert_page(-1)

def get_booklet_order(page_count: int) -> List[int]:
    """
    Returns the correct page order for booklet printing with two pages per sheet.
    When folded, the pages appear in the correct sequence.
    """
    booklet_order = []
    left = page_count
    right = 1
    while right < left:
        booklet_order.append(right)  # Right side on first page
        booklet_order.append(left)   # Left side on first page
        right += 1
        left -= 1
        if right < left:
            booklet_order.append(left)   # Left side on next sheet
            booklet_order.append(right)    # Right side on next sheet
            right += 1
            left -= 1
    return booklet_order

def safe_show_pdf_page(sheet: fitz.Page, rect: fitz.Rect, doc: fitz.Document, pagenum: int) -> None:
    """
    Renders a page safely, ignoring empty pages.
    Logs a warning if the page is empty.
    """
    try:
        sheet.show_pdf_page(rect, doc, pagenum)
    except ValueError as e:
        if "nothing to show" in str(e):
            logging.getLogger(__name__).warning("Page %d is empty, skipping.", pagenum + 1)
        else:
            raise

def create_booklet(input_pdf: str, output_pdf: str, x_adjust: int, y_adjust: int, skip_count: int,
                   left_page_x_adjust: float, right_page_x_adjust: float, page_y_adjust: float,
                   paper_size: str, orientation: str,
                   font_name: str, font_size: int, font_color: Tuple[float, float, float]) -> None:
    """
    Creates a booklet-formatted PDF with page numbering and custom layout.
    """
    try:
        doc = fitz.open(input_pdf)
    except Exception as e:
        logging.getLogger(__name__).error("Failed to open input PDF '%s': %s", input_pdf, e)
        sys.exit(1)

    if doc.page_count == 0:
        logging.getLogger(__name__).error("Input PDF has no pages.")
        sys.exit(1)

    add_blank_pages(doc)
    booklet_order = get_booklet_order(doc.page_count)
    logging.getLogger(__name__).info("Booklet order: %s", booklet_order)

    new_doc = fitz.open()
    page_width, page_height = fitz.paper_size(paper_size)
    sheet_size = (page_height, page_width) if orientation.lower() == "landscape" else (page_width, page_height)

    ## Define positions for numbering text boxes with mirrored adjustments.
    y_start = sheet_size[1] - 80 + y_adjust
    y_end = sheet_size[1] - 50 + y_adjust
    center_x = sheet_size[0] / 2
    left_center_x = center_x - x_adjust
    right_center_x = center_x + x_adjust
    left_num_rect = fitz.Rect(left_center_x - 20, y_start, left_center_x + 20, y_end)
    right_num_rect = fitz.Rect(right_center_x - 20, y_start, right_center_x + 20, y_end)

    # Apply mirroring logic: If right_page_x_adjust is None or same as left, mirror it.
    if right_page_x_adjust is None or right_page_x_adjust == left_page_x_adjust:
        right_page_x_adjust = left_page_x_adjust

    # Maintain default column positioning, but allow adjustments toward or away from the center.
    left_offset = -left_page_x_adjust  # Move left column left (-) or toward center (+)
    right_offset = right_page_x_adjust  # Move right column right (+) or toward center (-)
    left_rect = fitz.Rect(0 + left_offset, page_y_adjust, center_x + left_offset, sheet_size[1] + page_y_adjust)
    right_rect = fitz.Rect(center_x + right_offset, page_y_adjust, sheet_size[0] + right_offset, sheet_size[1] + page_y_adjust)

    # Process booklet_order in blocks of 4 placements.
    for i in range(0, len(booklet_order), 4):
        # First new page (two placements)
        sheet = new_doc.new_page(width=sheet_size[0], height=sheet_size[1])

        if i < len(booklet_order):
            safe_show_pdf_page(sheet, right_rect, doc, booklet_order[i] - 1)
            # Only number if the booklet order digit is greater than skip_count.
            if booklet_order[i] > skip_count:
                page_num = booklet_order[i] - skip_count
                sheet.insert_textbox(right_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)

        if i + 1 < len(booklet_order):
            safe_show_pdf_page(sheet, left_rect, doc, booklet_order[i + 1] - 1)
            if booklet_order[i + 1] > skip_count:
                page_num = booklet_order[i + 1] - skip_count
                sheet.insert_textbox(left_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)

        # Second new page (two placements)
        sheet = new_doc.new_page(width=sheet_size[0], height=sheet_size[1])

        if i + 2 < len(booklet_order):
            safe_show_pdf_page(sheet, right_rect, doc, booklet_order[i + 2] - 1)
            if booklet_order[i + 2] > skip_count:
                page_num = booklet_order[i + 2] - skip_count
                sheet.insert_textbox(right_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)

        if i + 3 < len(booklet_order):
            safe_show_pdf_page(sheet, left_rect, doc, booklet_order[i + 3] - 1)
            if booklet_order[i + 3] > skip_count:
                page_num = booklet_order[i + 3] - skip_count
                sheet.insert_textbox(left_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)

    try:
        new_doc.save(output_pdf)
        logging.getLogger(__name__).info("Booklet PDF saved as '%s'", output_pdf)
    except Exception as e:
        logging.getLogger(__name__).error("Failed to save output PDF '%s': %s", output_pdf, e)
        sys.exit(1)
