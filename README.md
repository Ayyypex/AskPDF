# AskPDF
AskPDF is a program that utilizes a Tkinter-based graphical user interface (GUI) to facilitate user interaction. The program allows users to select a PDF document and ask questions related to its content. The application leverages various technologies for PDF parsing, sentence embedding, and the OpenAI GPT API for question answering. Additionally, the program stores the questions and corresponding responses in a SQLite3 database.

## Features
- PDF Selection
- Question Answering
- Chat History and Clearing

## Limitations
The program currently identifies PDFs based solely on their names, which means that selecting a different PDF with the same name may result in the question and response history not matching the content of the current PDF. The program uses large dependencies, so the setup and installation process may take a while before the program is up and running. Due to the large size of the dependencies, I did not end up properly containerizing the application using Docker. Building a Docker image took a substantial amount of time, making it tedious to test and implement necessary changes.

## Installation
1. Clone the repository
    ```shell
    git clone https://github.com/Ayyypex/AskPDF.git
    ```
    
2. Run the `setup.sh` script to install the requirements
    ```shell
    AskPDF/app$ chmod u+x setup.sh
    AskPDF/app$ ./setup.sh
    ```
    OR just install the requirements directly
    ```shell
    AskPDF/docker$ pip install -r requirements.txt
    ```
    
3. Set your OpenAI API key in `myutil.py`
    ```shell
    openai.api_key = 'secret'    # Replace with your own API key
    ```
    OpenAI gives new free trial accounts a certain number of free credits. How to get an API key: https://openaimaster.com/how-to-get-openai-api-key-for-free/
   
5. Run the program
    ```shell
    AskPDF/app$ python3 askPDF.py
    ```
    Additional resource packages will be downloaded here, but that's pretty much it. Enjoy!

## Screenshots
Since it may take a while to get the program up and running, I'll show some screen shots.
![image](https://github.com/Ayyypex/AskPDF/blob/main/screenshots/img1.PNG)
![image](https://github.com/Ayyypex/AskPDF/blob/main/screenshots/img2.PNG)
![image](https://github.com/Ayyypex/AskPDF/blob/main/screenshots/img3.PNG)


The GPT API is prompted to use the information gathered from the paper to answer the question, so asking questions irrelevant to the paper won't lead to answers.
