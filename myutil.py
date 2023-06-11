import re
import PyPDF2
import openai
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util

# Set openai API key and token limit
openai.api_key = "SECRET"
TOKEN_LIMIT = 1000

# Initialize SentenceTransformer, stop words, and Lemmatizer
model = SentenceTransformer('bert-base-nli-mean-tokens')
stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()

########## Public Functions
# Function to parse a PDF into sentences
def parse_sentences(pdf_name):
    # Extract the text from all pages
    pdf_reader = PyPDF2.PdfReader(pdf_name)    
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    # Tokenize the text into sentences
    return sent_tokenize(pdf_text)

# Function to embed a list of sentences
def embed_sentences(sentences):
    sentence_embeddings = []
    for sentence in sentences:
        embedding = model.encode(sentence)
        sentence_embeddings.append(embedding)

    return sentence_embeddings

def get_response(question, sentences, sentence_embeddings):
    """
    Makes OpenAI API call to answer the question. Achieves this by first getting the sentences
    most similar to the question and using them in the call prompt.

    Args:
        question (str): The question string to answer.
        sentences (list): The list of PDF file sentences.
        sentence_embeddings (list): The list of embedded PDF file sentences.

    Returns:
        str: The API's response to the answer.
    """
    # Get the sentences most similar to the question
    matching_sentences = _top_matches(question, sentence_embeddings)
    
    # Generate the corresponding context for the prompt.
    limit = TOKEN_LIMIT - (len(question.split()) + 10)           
    context = _generate_context(sentences, matching_sentences, limit)

    # Construct prompt for API call
    prompt = f"Given this PDF's context:\nSTART\n{context}\nEND\n\nAnswer this question:\n\"{question}\""
    
    # Make API call and return response
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [{"role": "user",
                     "content": prompt}]
    )
    return completion.choices[0].message.content


########## Private Functions
# Function to convert NLTK POS tags to WordNet POS tags
def _get_wordnet_pos(tag):
    if tag.startswith('J'):     # adjective
        return wordnet.ADJ
    elif tag.startswith('V'):   # verb
        return wordnet.VERB
    elif tag.startswith('N'):   # noun
        return wordnet.NOUN
    elif tag.startswith('R'):   # adverb
        return wordnet.ADV
    else:
        return None

# Function to lemmatize tokens
def _lemmatize(tokens):
    tagged_words = pos_tag(tokens)

    # Lemmatize each word
    lemmatized_words = []
    for word, tag in tagged_words:
        wordnet_pos = _get_wordnet_pos(tag)
        if wordnet_pos:
            lemmatized_word = lemmatizer.lemmatize(word, pos=wordnet_pos)
        else:
            lemmatized_word = lemmatizer.lemmatize(word)
        lemmatized_words.append(lemmatized_word)

    return lemmatized_words

# Function to preprocess a document
def _preprocess(doc):
    # Remove special characters from the document
    doc = re.sub(r'[^\w\s]', '', doc)

    # Convert the document to lowercase
    doc = doc.lower()

    # Tokenize the document
    tokens = doc.split()

    # Remove stopwords and tokens with length of 1
    tokens = [tk for tk in tokens if tk not in stop_words and len(tk) > 1]

    # Lemmatize the tokens
    tokens = _lemmatize(tokens)
    
    return ' '.join(tokens)

def _top_matches(question, sentence_embeddings):
    """
    Returns the top matching sentences, ranked by the cosine similarity between the question and
    sentence embeddings.

    Args:
        question (str): The question string to match against.
        sentence_embeddings (list): The list of embedded sentences.

    Returns:
        list: A list of the top matching sentences and their similarity score.
    """
    # Compute embedding for the question
    question_embedding = model.encode(question)

    # Compute the cosine similarity between the question embedding and each matching sentence embedding
    similarities = []
    for i, embedding in enumerate(sentence_embeddings):
        similarity = util.cos_sim(question_embedding, embedding)
        similarities.append((i, similarity))
    
    # Sort the similarities in descending order
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    return sorted_similarities

def _generate_context(sentences, matching_sentences, token_limit):
    """
    Generates the context to be used for the GPT API prompt, by concatenating sentences from the top matches 
    until the token limit is reached or exceeded.

    Args:
        sentences (list): The list of sentences.
        matching_sentences (list): The list of tuples containing the index of a sentence and its similarity score.
        token_limit (int): The maximum number of tokens allowed in the generated context.

    Returns:
        str: The generated context consisting of concatenated preprocessed sentences.
    """
    # Concatenate sentence to the context, prioritizing higher ranking sentences
    context = ""
    for match in matching_sentences:
        match_index = match[0]
        match_sentence = sentences[match_index]

        # Preprocess the sentence
        preprocessed_sentence = _preprocess(match_sentence)

        # Add sentence only if it will not exceed the token limit
        if len(context.split()) + len(preprocessed_sentence.split()) < token_limit:
            split_sentence = preprocessed_sentence.split()
            joined_sentence = ' '.join(split_sentence)
            context += joined_sentence + ' '
    
    return context