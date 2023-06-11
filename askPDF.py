import os
import myutil
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from sentence_transformers import SentenceTransformer

# Define global variables
pdf_name = ""
sentences = []
sentence_embeddings = []

# Function to validate that the question input field has text
def validate_question_entry(*args):
    question = question_entry.get().strip()
    send_button.config(state=tk.NORMAL if question else tk.DISABLED)  

# Function to ask and answer the user's question
def ask_question():
    # Check whether a pdf has been selected
    if not pdf_name:
        messagebox.showerror("No PDF Selected", "Please select a PDF file to ask questions about.")
        return
    
    # Check question's word count
    question = question_entry.get().strip()
    word_count = len(question.split())
    if word_count > 30:
        messagebox.showerror(f"Word Limit Exceeded", "Please limit your question to 30 words.")
        return
    
    # Make API call to answer the question
    response = myutil.get_response(question, sentences, sentence_embeddings)
    
    # Add question and response to list
    history_text.insert(tk.END, f"Q: {question}\n")
    history_text.insert(tk.END, f"A: {response}\n\n")

    # Clear question field, disable send button, scroll to end
    question_entry.delete(0, tk.END)
    send_button.config(state=tk.DISABLED)
    history_text.see(tk.END)

# Function to clear chat history
def clear_history():
    history_text.delete("1.0", tk.END)

# Function to process a pdf file
def process_pdf(pdf_name):
    # Parse the pdf file's sentences
    global sentences
    sentences = myutil.parse_sentences(pdf_name)

    # Embed the pdf file's sentences
    global sentence_embeddings
    sentence_embeddings = myutil.embed_sentences(sentences)

    messagebox.showinfo("Processing Complete", "PDF processing completed.")

# Function to select a PDF file and process it
def select_pdf_file():
    file_path = filedialog.askopenfilename(title="Select a PDF File", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        global pdf_name 
        pdf_name = os.path.basename(file_path)
        label.config(text="Processing PDF... Please wait.")
        clear_history()
        root.update()

        # Process the file
        process_pdf(pdf_name)
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

# Create the question-response frame 
response_frame = tk.Frame(frame)
response_frame.pack()
history_text = tk.Text(response_frame, width=80, height=20, wrap=tk.WORD)
history_text.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)

# Create and set scrollbar
scrollbar = tk.Scrollbar(response_frame, command=history_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
history_text.config(yscrollcommand=scrollbar.set)

# Disable user input in question-response frame - disables scrolling as well :/
history_text.bindtags((str(history_text), root, "all"))

# Create the question input line
question_entry = tk.Entry(frame, width=80)
question_entry.pack(pady=5)
question_entry.bind("<KeyRelease>", validate_question_entry)

# Create the buttons
send_button = tk.Button(frame, text="Ask Question", command=ask_question, width=15, state=tk.DISABLED)
send_button.pack(pady=5)
clear_button = tk.Button(frame, text="Clear History", command=clear_history, width=15)
clear_button.pack(pady=5)
select_button = tk.Button(frame, text="Select PDF File", command=select_pdf_file, width=15)
select_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
