#!/usr/bin/env python3
import argparse
import logging
import os
import sys

from booklet import add_blank_pages, get_booklet_order, safe_show_pdf_page, create_booklet
from gui import gui_main

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a booklet-formatted PDF with custom layout options.")
    parser.add_argument("--input", "-i", type=str, help="Input PDF file path", required=False)
    parser.add_argument("--output", "-o", type=str, help="Output PDF file path", required=False)
    parser.add_argument("--x_adjust", type=int, default=212, help="Horizontal shift for textbox placement (default: 212)")
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

def command_line_main(args: argparse.Namespace) -> None:
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
    
    create_booklet(
        args.input, args.output, args.x_adjust, args.y_adjust, args.skip_count,
        args.left_page_x_adjust, args.right_page_x_adjust, args.page_y_adjust,
        args.paper_size, args.orientation,
        args.font_name, args.font_size, font_color
    )

def main():
    args = parse_arguments()
    configure_logging(args)
    if args.gui:
        gui_main(args)
    else:
        command_line_main(args)

if __name__ == "__main__":
    main()
