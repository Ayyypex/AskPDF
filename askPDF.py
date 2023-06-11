import os
import tkinter as tk
from tkinter import filedialog

# Define global variable for the chosen PDF
pdf_name = ""

# Function to 
def send_question():
    # Check that question is not empty and that a PDF has been selected
    question = question_entry.get()
    if not question or question.isspace() or not pdf_name:
        return
    
    # Make API call to get response
    response = "[response]"
    
    # Add question and response to list
    response_list.insert(tk.END, f"{question}")
    response_list.insert(tk.END, f"{response}")
    response_list.insert(tk.END, "")
    question_entry.delete(0, tk.END)

# Function to clear chat history
def clear_list():
    response_list.delete(0, tk.END)

# Function to select a PDF file
def select_pdf_file():
    file_path = filedialog.askopenfilename(title="Select a PDF File", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        global pdf_name 
        pdf_name = os.path.basename(file_path)
        label.config(text="Selected PDF: " + pdf_name)

# Create the main window
root = tk.Tk()
root.title("AskPDF")

# Define the window's dimensions and set the window' position to center of screen
window_width = 1200
window_height = 720
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 4
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Create a centered frame
frame = tk.Frame(root, relief="solid", borderwidth=1)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Create label at the top of the frame
label = tk.Label(frame, text="No PDF Selected", font=("Arial", 16, "bold"))
label.pack(pady=10)

# Create the question-response listbox 
response_frame = tk.Frame(frame)
response_frame.pack()
response_list = tk.Listbox(response_frame, width=80, height=20)
response_list.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

# Create and set scrollbar
scrollbar = tk.Scrollbar(response_frame, command=response_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
response_list.config(yscrollcommand=scrollbar.set)

# Create the question input line
question_entry = tk.Entry(frame, width=80)
question_entry.pack(pady=5)

# Create the buttons
send_button = tk.Button(frame, text="Send Question", command=send_question, width=15)
send_button.pack(pady=5)
clear_button = tk.Button(frame, text="Clear History", command=clear_list, width=15)
clear_button.pack(pady=5)
select_button = tk.Button(frame, text="Select PDF File", command=select_pdf_file, width=15)
select_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
