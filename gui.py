import os
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar
from tkinter import ttk
import fitz
from booklet import add_blank_pages, get_booklet_order, create_booklet

def gui_main(args) -> None:
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
            paper = paper_size_var.get().strip().lower()
            orient = orientation_var.get().strip().lower()
            f_name = font_name_entry.get().strip()
            f_size = int(font_size_entry.get().strip())
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

    # Main window
    root = tk.Tk()
    root.title("Booklet Creator")
    root.geometry("600x600")
    
    # Use a main frame for padding
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    
    # File selection frame
    file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
    file_frame.grid(row=0, column=0, sticky="ew", pady=5)
    
    ttk.Label(file_frame, text="Input PDF File:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
    input_entry = ttk.Entry(file_frame, width=50)
    input_entry.grid(row=0, column=1, padx=5, pady=2)
    ttk.Button(file_frame, text="Browse...", command=browse_input).grid(row=0, column=2, padx=5, pady=2)
    
    ttk.Label(file_frame, text="Output PDF File:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
    output_entry = ttk.Entry(file_frame, width=50)
    output_entry.grid(row=1, column=1, padx=5, pady=2)
    ttk.Button(file_frame, text="Browse...", command=browse_output).grid(row=1, column=2, padx=5, pady=2)
    
    # Layout and numbering settings frame
    settings_frame = ttk.LabelFrame(main_frame, text="Layout & Numbering Settings", padding="10")
    settings_frame.grid(row=1, column=0, sticky="ew", pady=5)
    
    ttk.Label(settings_frame, text="Page Number Horizontal Offset (moves numbers left/right):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
    x_adjust_entry = ttk.Entry(settings_frame, width=20)
    x_adjust_entry.insert(0, str(args.x_adjust))
    x_adjust_entry.grid(row=0, column=1, padx=5, pady=2)
    
    ttk.Label(settings_frame, text="Page Number Vertical Offset (moves numbers up/down):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
    y_adjust_entry = ttk.Entry(settings_frame, width=20)
    y_adjust_entry.insert(0, str(args.y_adjust))
    y_adjust_entry.grid(row=1, column=1, padx=5, pady=2)
    
    ttk.Label(settings_frame, text="Skip numbering for the first X pages:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
    skip_count_entry = ttk.Entry(settings_frame, width=20)
    skip_count_entry.insert(0, str(args.skip_count))
    skip_count_entry.grid(row=2, column=1, padx=5, pady=2)
    
    ttk.Label(settings_frame, text="Left Page Horizontal Offset (fine-tune left page position):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
    left_page_x_entry = ttk.Entry(settings_frame, width=20)
    left_page_x_entry.insert(0, str(args.left_page_x_adjust))
    left_page_x_entry.grid(row=3, column=1, padx=5, pady=2)
    
    ttk.Label(settings_frame, text="Right Page Horizontal Offset (fine-tune right page position):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
    right_page_x_entry = ttk.Entry(settings_frame, width=20)
    right_page_x_entry.insert(0, str(args.right_page_x_adjust))
    right_page_x_entry.grid(row=4, column=1, padx=5, pady=2)
    
    ttk.Label(settings_frame, text="Content Vertical Offset (adjust overall page positioning):").grid(row=5, column=0, sticky="e", padx=5, pady=2)
    page_y_adjust_entry = ttk.Entry(settings_frame, width=20)
    page_y_adjust_entry.insert(0, str(args.page_y_adjust))
    page_y_adjust_entry.grid(row=5, column=1, padx=5, pady=2)
    
    # Paper and orientation settings frame
    paper_frame = ttk.LabelFrame(main_frame, text="Paper & Orientation Settings", padding="10")
    paper_frame.grid(row=2, column=0, sticky="ew", pady=5)
    
    ttk.Label(paper_frame, text="Paper Size:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
    paper_size_var = StringVar(root, value=args.paper_size)
    paper_dropdown = ttk.Combobox(paper_frame, textvariable=paper_size_var, values=["a4", "letter"], width=17)
    paper_dropdown.grid(row=0, column=1, padx=5, pady=2)
    
    ttk.Label(paper_frame, text="Orientation:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
    orientation_var = StringVar(root, value=args.orientation)
    orientation_dropdown = ttk.Combobox(paper_frame, textvariable=orientation_var, values=["portrait", "landscape"], width=17)
    orientation_dropdown.grid(row=1, column=1, padx=5, pady=2)
    
    # Font settings frame
    font_frame = ttk.LabelFrame(main_frame, text="Font Settings for Numbering", padding="10")
    font_frame.grid(row=3, column=0, sticky="ew", pady=5)
    
    ttk.Label(font_frame, text="Font for Page Numbers:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
    font_name_entry = ttk.Entry(font_frame, width=20)
    font_name_entry.insert(0, args.font_name)
    font_name_entry.grid(row=0, column=1, padx=5, pady=2)
    
    ttk.Label(font_frame, text="Font Size:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
    font_size_entry = ttk.Entry(font_frame, width=20)
    font_size_entry.insert(0, str(args.font_size))
    font_size_entry.grid(row=1, column=1, padx=5, pady=2)
    
    ttk.Label(font_frame, text="Font Color (R,G,B):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
    font_color_entry = ttk.Entry(font_frame, width=20)
    font_color_entry.insert(0, args.font_color)
    font_color_entry.grid(row=2, column=1, padx=5, pady=2)
    
    # Overwrite option
    overwrite_var = tk.BooleanVar(value=args.overwrite)
    ttk.Checkbutton(main_frame, text="Overwrite existing output file", variable=overwrite_var).grid(row=4, column=0, sticky="w", padx=5, pady=5)
    
    # Action buttons
    action_frame = ttk.Frame(main_frame, padding="10")
    action_frame.grid(row=5, column=0, sticky="ew", pady=10)
    ttk.Button(action_frame, text="Preview Booklet Order", command=preview_order).grid(row=0, column=0, padx=10, pady=5)
    ttk.Button(action_frame, text="Generate Booklet", command=generate_booklet).grid(row=0, column=1, padx=10, pady=5)
    
    root.mainloop()


if __name__ == '__main__':
    # Dummy args for testing
    class DummyArgs:
        x_adjust = 7
        y_adjust = 25
        skip_count = 5
        left_page_x_adjust = 0
        right_page_x_adjust = 0
        page_y_adjust = 0
        paper_size = 'a4'
        orientation = 'landscape'
        font_name = 'times-roman'
        font_size = 16
        font_color = '0,0,0'
        overwrite = False

    gui_main(DummyArgs())
