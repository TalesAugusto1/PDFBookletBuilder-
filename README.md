# PDFBookletBuilder

PDFBookletBuilder is a Python script that reorders pages of a PDF document into a booklet format suitable for printing. It ensures that pages are properly arranged so that when printed double-sided and folded, they appear in the correct order.

## Features

- **Command-Line and GUI Support:** Use the script via command line or an easy-to-use graphical interface.
- **Automatic Blank Page Handling:** Ensures the total page count is a multiple of 4.
- **Flexible Paper Size & Orientation:** Supports A4, Letter, and other formats in landscape or portrait orientation.
- **Configurable Page Numbering:** Adjust positioning, font, size, and color of numbers.
- **Custom Layout Adjustments:** Fine-tune horizontal/vertical shifts for better alignment.
- **Logging & Error Handling:** Provides clear error messages and logging options.

## Prerequisites

This script requires Python and the `pymupdf` (PyMuPDF) library.

### Install Dependencies

```sh
pip install pymupdf
```

## Usage

### Command-Line Usage

Run the script with:

```sh
python script.py --input input.pdf --output output.pdf
```

#### Available Options:

- `--input`: Path to the source PDF file (required).
- `--output`: Path to the generated booklet PDF (required).
- `--x_adjust`: Horizontal shift for numbering (default: 7).
- `--y_adjust`: Vertical shift for numbering (default: 25).
- `--skip_count`: Pages to skip before numbering (default: 5).
- `--left_page_x_adjust`: Offset for left page placement (default: 0).
- `--right_page_x_adjust`: Offset for right page placement (default: 0).
- `--page_y_adjust`: Vertical offset for page placements (default: 0).
- `--paper_size`: Paper format (e.g., a4, letter) (default: a4).
- `--orientation`: Page layout (portrait or landscape) (default: landscape).
- `--font_name`: Font for numbering (default: Times-Roman).
- `--font_size`: Font size for numbering (default: 16).
- `--font_color`: Font color in R,G,B format (default: 0,0,0).
- `--overwrite`: Overwrite output file if it exists.
- `--gui`: Launches the graphical interface.

### GUI Usage

Run the script with:

```sh
python script.py --gui
```

- Browse for an input PDF file.
- Set output filename and options.
- Preview the calculated booklet order before generating.

### Example

```sh
python script.py --input document.pdf --output booklet.pdf --paper_size letter --orientation portrait
```

This will create a `booklet.pdf` formatted for booklet printing with Letter-sized portrait pages.

## How It Works

1. Checks if the input PDF has a page count that is a multiple of 4.
2. Adds blank pages if needed.
3. Calculates the correct booklet page order.
4. Creates a new PDF with pages arranged for booklet printing.
5. Places page numbers (after an initial skip) in proper positions.

## Customization

Users can modify parameters to fine-tune the output. The script supports:

- Custom font styles, sizes, and colors for numbering.
- Layout tweaks for better alignment.
- Different paper sizes and orientations.

## Troubleshooting

- **Extra blank pages appear:** This is intentional to maintain proper booklet formatting.
- **Page numbers are misplaced:** Adjust `x_adjust` and `y_adjust` values.
- **Installation issues:** Ensure Python and `pymupdf` are installed.

## License

This project is licensed under the MIT License.

## Contributions

Contributions and improvements are welcome! Feel free to submit a pull request or open an issue.

## Author

Developed by Tales Augusto.
