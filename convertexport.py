import tkinter as tk
from tkinter import filedialog
import os

def convert_file(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        lines = infile.readlines()
        for line in lines[:-1]:  # Process all lines except the last one
            parts = line.split(' ', 1)  # Split only on the first space
            if len(parts) == 2:
                count, card_name = parts
                outfile.write(f"{card_name.strip()}, {count}\n")
        
        # Process the last line separately without adding a newline at the end
        last_line = lines[-1]
        if last_line.strip():  # Check if the last line is not empty
            parts = last_line.split(' ', 1)
            if len(parts) == 2:
                count, card_name = parts
                outfile.write(f"{card_name.strip()}, {count}")

def select_and_convert_file():
    input_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if input_file:
        output_file = os.path.splitext(input_file)[0] + "_converted.txt"
        convert_file(input_file, output_file)
        tk.messagebox.showinfo("Success", f"File converted and saved as {output_file}")

# Set up the tkinter window
root = tk.Tk()
root.title("File Converter")

# Create a button to trigger file selection and conversion
convert_button = tk.Button(root, text="Select File to Convert", command=select_and_convert_file)
convert_button.pack(pady=20)

# Run the tkinter main loop
root.mainloop()