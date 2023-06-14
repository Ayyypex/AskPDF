import os
import myutil
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

# Create database and tables if the database file does not exist
if not os.path.exists('chat_history.db'):
    # Create a database file
    conn = sqlite3.connect('chat_history.db')

    # Create cursor and new database tables
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PDF (
            pdf_name TEXT PRIMARY KEY
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS QuestionResponse (
            id INTEGER PRIMARY KEY,
            question TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pdf_name TEXT,
            FOREIGN KEY (pdf_name) REFERENCES PDF (pdf_name)
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Define global variables
pdf_name = ""
sentences = []
sentence_embeddings = []

# Function to validate that the question input field has text
def validate_question_entry(*args):
    question = question_entry.get().strip()
    send_button.config(state=tk.NORMAL if question else tk.DISABLED)

# Function to select a PDF file and process it
def select_pdf_file():
    file_path = filedialog.askopenfilename(title="Select a PDF File", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        # Return if the file is already selected
        global pdf_name
        if pdf_name == os.path.basename(file_path):
            messagebox.showinfo("PDF Already Selected", "The selected PDF is the same as the current one.")
            return

        # Set to selected PDF
        pdf_name = os.path.basename(file_path)

        # Process the file, updating the window before processing begins
        title_label.config(text="Processing PDF... Please wait.")
        clear_history()
        root.update()
        process_pdf(file_path)

        # Update title and add file to database
        title_label.config(text="Selected PDF: " + pdf_name)
        add_pdf_to_database(pdf_name)

# Function to process a PDF file
def process_pdf(pdf_filepath):
    # Parse the PDF file's sentences
    global sentences
    sentences = myutil.parse_sentences(pdf_filepath)

    # Embed the PDF file's sentences
    global sentence_embeddings
    sentence_embeddings = myutil.embed_sentences(sentences)

    messagebox.showinfo("Processing Complete", "PDF processing completed.")

# Function to add a PDF file to the database
def add_pdf_to_database(pdf_name):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    # Check if the PDF file name already exists in the database
    cursor.execute("SELECT COUNT(*) FROM PDF WHERE pdf_name = ?", (pdf_name,))
    result = cursor.fetchone()

    # If it exists, load history
    if result[0] > 0:
        messagebox.showinfo("PDF Already Exists", "This PDF already exists in the database, the history will be loaded.")
        load_history(pdf_name)

    # Else, add it to the database
    else:
        cursor.execute("INSERT INTO PDF (pdf_name) VALUES (?)", (pdf_name,))
        conn.commit()

    conn.close()

# Function to load the question-response history of a selected PDF
def load_history(pdf_name):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()

    # Retrieve question-response history for the given PDF name
    cursor.execute("SELECT question, response FROM QuestionResponse WHERE pdf_name = ? ORDER BY created_at", (pdf_name,))
    rows = cursor.fetchall()

    # Display the question-response history
    for row in rows:
        question = row[0]
        response = row[1]
        history_text.insert(tk.END, f"Q: {question}\n")
        history_text.insert(tk.END, f"A: {response}\n\n")

    conn.close()

# Function to ask and answer the user's question
def ask_question():
    # Return if a PDF has not been selected
    if not pdf_name:
        messagebox.showerror("No PDF Selected", "Please select a PDF file to ask questions about.")
        return
    
    # Check question's word count
    question = question_entry.get().strip()
    word_count = len(question.split())
    if word_count > 30:
        messagebox.showerror(f"Word Limit Exceeded", "Please limit your question to 30 words.")
        return
    
    # Clear question field, disable send button, display question
    question_entry.delete(0, tk.END)
    send_button.config(state=tk.DISABLED)
    history_text.insert(tk.END, f"Q: {question}\n")
    history_text.insert(tk.END, "Getting response...")
    root.update()

    # Make API call to answer the question, 
    response = myutil.get_response(question, sentences, sentence_embeddings)

    # Get the index of the last character and start of the last line
    last_char_index = history_text.index(tk.END + "-1c")
    last_line_start = history_text.index(last_char_index + " linestart")

    # Delete the placeholder line and display the response
    history_text.delete(last_line_start, tk.END)
    history_text.insert(tk.END, f"\nA: {response}\n\n")

    # Scroll to end
    history_text.see(tk.END)

    # Add question-response to database
    add_question_response_to_database(question, response)

# Function to add the question-response to the database
def add_question_response_to_database(question, response):
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO QuestionResponse (question, response, pdf_name) VALUES (?, ?, ?)", (question, response, pdf_name))
    conn.commit()
    conn.close()

# Function to clear question-response history
def clear_history():
    # Return if a PDF has not been selected
    if not pdf_name:
        return
    
    # Clear question-response history in the frontend
    history_text.delete("1.0", tk.END)
    
    # Clear database question-response history for the PDF
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM QuestionResponse WHERE pdf_name = ?", (pdf_name,))
    conn.commit()
    conn.close()

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
title_label = tk.Label(frame, text="No PDF Selected", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

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
