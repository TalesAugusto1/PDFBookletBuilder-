# PDFBookletBuilder

PDF Booklet Maker is a Python script that reorders pages of a PDF document into a booklet format suitable for printing. It ensures that pages are properly arranged so that when printed double-sided and folded, they appear in the correct order.

## Features

- Automatically adds blank pages if needed to ensure a multiple of 4 pages.
- Arranges pages in booklet order for double-sided printing.
- Preserves original page orientation.
- Adds page numbers with configurable positioning.
- Supports A4 landscape format.

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
python script.py input.pdf output.pdf
```

- `input.pdf`: Path to the source PDF file.
- `output.pdf`: Path to the generated booklet PDF.

### Example

```sh
python booklet_maker.py document.pdf booklet.pdf
```

This will create a `booklet.pdf` formatted for printing.

## How It Works

1. Checks if the input PDF has a page count that is a multiple of 4.
2. Adds blank pages if needed.
3. Calculates the correct booklet page order.
4. Creates a new PDF with pages arranged for booklet printing.
5. Places page numbers (after an initial skip) in proper positions.

## Customization

You can modify the script to adjust:

- `X_ADJUST` and `Y_ADJUST` values to fine-tune page number positions.
- `SKIP_COUNT` to control how many pages are skipped before numbering starts.

## Troubleshooting

- **Output has extra blank pages:** The script ensures the total page count is a multiple of 4 for proper booklet formatting.
- **Page numbers are misplaced:** Adjust `X_ADJUST` and `Y_ADJUST` in the script.
- **Installation issues:** Ensure Python and `pymupdf` are correctly installed.

## License

This project is licensed under the MIT License.

## Contributions

Contributions and improvements are welcome! Feel free to submit a pull request or open an issue.

## Author

Developed by Tales Augusto.
