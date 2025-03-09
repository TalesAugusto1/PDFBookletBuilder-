#!/usr/bin/env python3
import fitz
import sys
import logging
import os
import argparse
from typing import List, Tuple

# For GUI
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a booklet-formatted PDF with custom layout options.")
    parser.add_argument("--input", "-i", type=str, help="Input PDF file path", required=False)
    parser.add_argument("--output", "-o", type=str, help="Output PDF file path", required=False)
    parser.add_argument("--x_adjust", type=int, default=7, help="Horizontal shift for textbox placement (default: 7)")
    parser.add_argument("--y_adjust", type=int, default=25, help="Vertical shift for textbox placement (default: 25)")
    parser.add_argument("--skip_count", type=int, default=5, help="How many initial placements to skip numbering (default: 5)")
    parser.add_argument("--left_page_x_adjust", type=float, default=0, help="Horizontal offset for left page placement (default: 0)")
    parser.add_argument("--right_page_x_adjust", type=float, default=0, help="Horizontal offset for right page placement (default: 0)")
    parser.add_argument("--page_y_adjust", type=float, default=0, help="Vertical offset for page placements (default: 0)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output file if it exists")
    parser.add_argument("--paper_size", type=str, default="a4", help="Paper size (e.g., a4, letter) (default: a4)")
    parser.add_argument("--orientation", type=str, choices=["portrait", "landscape"], default="landscape",
                        help="Page orientation (default: landscape)")
    parser.add_argument("--font_name", type=str, default="times-roman", help="Font name for page numbering (default: times-roman)")
    parser.add_argument("--font_size", type=int, default=16, help="Font size for page numbering (default: 16)")
    parser.add_argument("--font_color", type=str, default="0,0,0", help="Font color for page numbering as R,G,B (default: 0,0,0)")
    parser.add_argument("--log_file", type=str, default=None, help="Optional log file path")
    parser.add_argument("--gui", action="store_true", help="Launch GUI for parameter input")
    return parser.parse_args()

def configure_logging(args: argparse.Namespace) -> None:
    log_level = logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=log_level, format=log_format)
    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    global logger
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
                   left_page_x_adjust: float, right_page_x_adjust: float, page_y_adjust: float,
                   paper_size: str, orientation: str,
                   font_name: str, font_size: int, font_color: Tuple[float, float, float]) -> None:
    """
    Creates a booklet-formatted PDF with page numbering and custom layout.
    Additional configuration options allow for paper size, orientation, and font settings.
    """
    try:
        doc = fitz.open(input_pdf)
    except Exception as e:
        logger.error("Failed to open input PDF '%s': %s", input_pdf, e)
        sys.exit(1)

    if doc.page_count == 0:
        logger.error("Input PDF has no pages.")
        sys.exit(1)

    add_blank_pages(doc)
    booklet_order = get_booklet_order(doc.page_count)
    logger.info("Booklet order: %s", booklet_order)
    
    new_doc = fitz.open()
    page_width, page_height = fitz.paper_size(paper_size)
    if orientation.lower() == "landscape":
        sheet_size = (page_height, page_width)
    else:
        sheet_size = (page_width, page_height)

    # Define positions for numbering text boxes with user-provided adjustments.
    y_start = sheet_size[1] - 80 + y_adjust
    y_end = sheet_size[1] - 50 + y_adjust
    left_center_x = sheet_size[0] / 4 + x_adjust
    right_center_x = 3 * sheet_size[0] / 4 + x_adjust
    left_num_rect = fitz.Rect(left_center_x - 20, y_start, left_center_x + 20, y_end)
    right_num_rect = fitz.Rect(right_center_x - 20, y_start, right_center_x + 20, y_end)
    
    # Process booklet_order in blocks of 4.
    for i in range(0, len(booklet_order), 4):
        # First new page (contains two placements)
        sheet = new_doc.new_page(width=sheet_size[0], height=sheet_size[1])
        # Define adjusted rectangles for page placements:
        right_rect = fitz.Rect((sheet_size[0] / 2) + right_page_x_adjust, 0 + page_y_adjust,
                               sheet_size[0] + right_page_x_adjust, sheet_size[1] + page_y_adjust)
        left_rect = fitz.Rect(0 + left_page_x_adjust, 0 + page_y_adjust,
                              (sheet_size[0] / 2) + left_page_x_adjust, sheet_size[1] + page_y_adjust)
        if i < len(booklet_order):
            safe_show_pdf_page(sheet, right_rect, doc, booklet_order[i] - 1)
            if i >= skip_count:
                page_num = booklet_order[i] - (skip_count - 2)
                sheet.insert_textbox(right_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)
        if i + 1 < len(booklet_order):
            safe_show_pdf_page(sheet, left_rect, doc, booklet_order[i + 1] - 1)
            if i + 1 >= skip_count:
                page_num = booklet_order[i + 1] - (skip_count - 2)
                sheet.insert_textbox(left_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)
        
        # Second new page (contains two placements)
        sheet = new_doc.new_page(width=sheet_size[0], height=sheet_size[1])
        if i + 2 < len(booklet_order):
            safe_show_pdf_page(sheet, right_rect, doc, booklet_order[i + 2] - 1)
            if i + 2 >= skip_count:
                page_num = booklet_order[i + 2] - (skip_count - 2)
                sheet.insert_textbox(right_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)
        if i + 3 < len(booklet_order):
            safe_show_pdf_page(sheet, left_rect, doc, booklet_order[i + 3] - 1)
            if i + 3 >= skip_count:
                page_num = booklet_order[i + 3] - (skip_count - 2)
                sheet.insert_textbox(left_num_rect, str(page_num),
                                     fontsize=font_size, fontname=font_name, color=font_color, align=1)

    try:
        new_doc.save(output_pdf)
        logger.info("Booklet PDF saved as '%s'", output_pdf)
    except Exception as e:
        logger.error("Failed to save output PDF '%s': %s", output_pdf, e)
        sys.exit(1)

def command_line_main(args: argparse.Namespace) -> None:
    # Ensure required arguments are provided; otherwise, prompt interactively.
    if not args.input:
        args.input = input("Enter input PDF path: ").strip()
    if not args.output:
        args.output = input("Enter output PDF path: ").strip()

    if os.path.exists(args.output) and not args.overwrite:
        logger.info("Output file '%s' exists and --overwrite not specified. Exiting.", args.output)
        sys.exit(0)
    
    # Convert font_color string to tuple.
    try:
        font_color = tuple(float(x.strip()) for x in args.font_color.split(","))
        if len(font_color) != 3:
            raise ValueError
    except Exception:
        logger.error("Invalid --font_color format. Expected format: R,G,B (e.g., 0,0,0)")
        sys.exit(1)
    
    create_booklet(args.input, args.output, args.x_adjust, args.y_adjust, args.skip_count,
                   args.left_page_x_adjust, args.right_page_x_adjust, args.page_y_adjust,
                   args.paper_size, args.orientation,
                   args.font_name, args.font_size, font_color)

def gui_main(args: argparse.Namespace) -> None:
    def browse_input():
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            input_entry.delete(0, tk.END)
            input_entry.insert(0, path)
    def browse_output():
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, path)
    def preview_order():
        input_path = input_entry.get().strip()
        if not os.path.exists(input_path):
            messagebox.showerror("Error", "Input PDF does not exist.")
            return
        try:
            doc = fitz.open(input_path)
            add_blank_pages(doc)
            order = get_booklet_order(doc.page_count)
            messagebox.showinfo("Booklet Order", f"Calculated Booklet Order:\n{order}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate booklet order: {e}")
    def generate_booklet():
        # Get all parameters from GUI
        input_path = input_entry.get().strip()
        output_path = output_entry.get().strip()
        if os.path.exists(output_path) and not overwrite_var.get():
            messagebox.showinfo("Info", "Output file exists and overwrite is not enabled.")
            return
        try:
            x_adj = int(x_adjust_entry.get().strip())
            y_adj = int(y_adjust_entry.get().strip())
            skip = int(skip_count_entry.get().strip())
            left_x = float(left_page_x_entry.get().strip())
            right_x = float(right_page_x_entry.get().strip())
            page_y = float(page_y_adjust_entry.get().strip())
            paper = paper_size_var.get().strip()
            orient = orientation_var.get().strip()
            f_name = font_name_entry.get().strip()
            f_size = int(font_size_entry.get().strip())
            # Convert color string to tuple.
            f_color = tuple(float(x.strip()) for x in font_color_entry.get().split(","))
            if len(f_color) != 3:
                raise ValueError("Font color must be in R,G,B format")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid parameter: {e}")
            return
        
        try:
            create_booklet(input_path, output_path, x_adj, y_adj, skip, left_x, right_x, page_y,
                           paper, orient, f_name, f_size, f_color)
            messagebox.showinfo("Success", f"Booklet PDF saved as '{output_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create booklet: {e}")

    root = tk.Tk()
    root.title("Booklet Creator")

    # Input file
    tk.Label(root, text="Input PDF:").grid(row=0, column=0, sticky="e")
    input_entry = tk.Entry(root, width=50)
    input_entry.grid(row=0, column=1, padx=5)
    tk.Button(root, text="Browse", command=browse_input).grid(row=0, column=2, padx=5)
    
    # Output file
    tk.Label(root, text="Output PDF:").grid(row=1, column=0, sticky="e")
    output_entry = tk.Entry(root, width=50)
    output_entry.grid(row=1, column=1, padx=5)
    tk.Button(root, text="Browse", command=browse_output).grid(row=1, column=2, padx=5)
    
    # Other parameters
    tk.Label(root, text="x_adjust:").grid(row=2, column=0, sticky="e")
    x_adjust_entry = tk.Entry(root)
    x_adjust_entry.insert(0, str(args.x_adjust))
    x_adjust_entry.grid(row=2, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="y_adjust:").grid(row=3, column=0, sticky="e")
    y_adjust_entry = tk.Entry(root)
    y_adjust_entry.insert(0, str(args.y_adjust))
    y_adjust_entry.grid(row=3, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="skip_count:").grid(row=4, column=0, sticky="e")
    skip_count_entry = tk.Entry(root)
    skip_count_entry.insert(0, str(args.skip_count))
    skip_count_entry.grid(row=4, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="left_page_x_adjust:").grid(row=5, column=0, sticky="e")
    left_page_x_entry = tk.Entry(root)
    left_page_x_entry.insert(0, str(args.left_page_x_adjust))
    left_page_x_entry.grid(row=5, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="right_page_x_adjust:").grid(row=6, column=0, sticky="e")
    right_page_x_entry = tk.Entry(root)
    right_page_x_entry.insert(0, str(args.right_page_x_adjust))
    right_page_x_entry.grid(row=6, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="page_y_adjust:").grid(row=7, column=0, sticky="e")
    page_y_adjust_entry = tk.Entry(root)
    page_y_adjust_entry.insert(0, str(args.page_y_adjust))
    page_y_adjust_entry.grid(row=7, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="Paper size:").grid(row=8, column=0, sticky="e")
    paper_size_var = tk.StringVar(value=args.paper_size)
    tk.Entry(root, textvariable=paper_size_var).grid(row=8, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="Orientation:").grid(row=9, column=0, sticky="e")
    orientation_var = tk.StringVar(value=args.orientation)
    tk.Entry(root, textvariable=orientation_var).grid(row=9, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="Font name:").grid(row=10, column=0, sticky="e")
    font_name_entry = tk.Entry(root)
    font_name_entry.insert(0, args.font_name)
    font_name_entry.grid(row=10, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="Font size:").grid(row=11, column=0, sticky="e")
    font_size_entry = tk.Entry(root)
    font_size_entry.insert(0, str(args.font_size))
    font_size_entry.grid(row=11, column=1, sticky="w", padx=5)
    
    tk.Label(root, text="Font color (R,G,B):").grid(row=12, column=0, sticky="e")
    font_color_entry = tk.Entry(root)
    font_color_entry.insert(0, args.font_color)
    font_color_entry.grid(row=12, column=1, sticky="w", padx=5)
    
    overwrite_var = tk.BooleanVar(value=args.overwrite)
    tk.Checkbutton(root, text="Overwrite existing output file", variable=overwrite_var).grid(row=13, column=1, sticky="w")
    
    # Buttons
    tk.Button(root, text="Preview Booklet Order", command=preview_order).grid(row=14, column=0, pady=10)
    tk.Button(root, text="Generate Booklet", command=generate_booklet).grid(row=14, column=1, pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    args = parse_arguments()
    configure_logging(args)
    if args.gui:
        gui_main(args)
    else:
        command_line_main(args)
