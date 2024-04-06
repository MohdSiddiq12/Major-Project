# -*- coding: utf-8 -*-
"""Flask_Deployment_Question_Answering_System.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Zf_IuGDRMJxNxyq4UKqwt4NtFG40o4EL
"""

from google.colab import drive
drive.mount('/content/gdrive')

!pwd

import os
os.chdir('gdrive/My Drive/Colab Notebooks')

import tensorflow as tf
tf.test.gpu_device_name()

from tensorflow.python.client import device_lib
device_lib.list_local_devices()

!cat /proc/meminfo

!pip install pdfplumber
!pip install nltk
!pip install -U gensim
!pip install flask-ngrok
!pip install werkzeug
!pip install numpy

def pdf_extract(file_name):
  import pdfplumber
  directory = "docs"
  pdf_txt = ""
  for file in os.listdir(directory):
      filename = os.fsdecode(file)
      if(filename == file_name):
          pdf_txt = '' # new line
          with pdfplumber.open(directory + '/' + filename) as pdf:
              for pdf_page in pdf.pages:
                single_page_text = pdf_page.extract_text()
                pdf_txt = pdf_txt + single_page_text
  return pdf_txt

#print(pdf_extract('test.pdf'))

#New Way pdf Extractor
#!pip install pdf_layout_scanner

# from pdf_layout_scanner import layout_scanner
# toc=layout_scanner.get_toc('docs/test.pdf')
# pages=layout_scanner.get_pages('docs/test.pdf')
# print(len(pages))

# for i in range(len(pages)):
#     print(pages[i])

import re
import gensim
from gensim.parsing.preprocessing import remove_stopwords

def clean_sentence(sentence, stopwords=False):
  sentence = sentence.lower().strip()
  sentence = re.sub(r'[^a-z0-9\s]', '', sentence)
  if stopwords:
    sentence = remove_stopwords(sentence)
  return sentence

def get_cleaned_sentences(tokens, stopwords=False):
  cleaned_sentences = []
  for row in tokens:
    cleaned = clean_sentence(row, stopwords)
    cleaned_sentences.append(cleaned)
  return cleaned_sentences

def retrieveAndPrintFAQAnswer(question_embedding, sentence_embeddings, sentences):
  import sklearn
  from sklearn.metrics.pairwise import cosine_similarity
  max_sim = -1
  index_sim = -1
  for index, embedding in enumerate(sentence_embeddings):
    sim = cosine_similarity(embedding, question_embedding)[0][0]
    if sim > max_sim:
      max_sim = sim
      index_sim = index

  return index_sim

def naive_drive(file_name, question):
  pdf_txt = pdf_extract(file_name)
  import nltk
  import numpy
  import pprint
  nltk.download('punkt')
  tokens = nltk.sent_tokenize(pdf_txt)
  cleaned_sentences = get_cleaned_sentences(tokens, stopwords=True)
  cleaned_sentences_with_stopwords = get_cleaned_sentences(tokens, stopwords=False)
  sentences = cleaned_sentences_with_stopwords
  sentence_words = [[word for word in document.split()]
                    for document in sentences]

  from gensim import corpora
  dictionary = corpora.Dictionary(sentence_words)
  bow_corpus = [dictionary.doc2bow(text) for text in sentence_words]

  question = clean_sentence(question, stopwords=False)
  question_embedding = dictionary.doc2bow(question.split())

  index = retrieveAndPrintFAQAnswer(question_embedding, bow_corpus, sentences)
  return sentences[index]

# question = "What were the various steps taken by the government to boost domestic and foreign investment in India ?"
# answer = naive_drive('fdi.pdf', question)
# print(answer)

"""==================================================================================================================="""

from gensim.models import Word2Vec
import gensim.downloader as api

v2w_model = None
try:
  v2w_model = gensim.models.Keyedvectors.load('./w2vecmodel.mod')
  print("w2v Model Successfully loaded")
except:
  v2w_model = api.load('word2vec-google-news-300')
  v2w_model.save("./w2vecmodel.mod")
  print("w2v Model Saved")

w2vec_embedding_size = len(v2w_model['pc'])

def getWordVec(word, model):
  import numpy
  samp = model['pc']
  vec = [0]*len(samp)
  try:
    vec = model[word]
  except:
    vec = [0]*len(samp)
  return (vec)


def getPhraseEmbedding(phrase, embeddingmodel):
  import numpy
  samp = getWordVec('computer', embeddingmodel)
  vec = numpy.array([0]*len(samp))
  den = 0;
  for word in phrase.split():
    den = den+1
    vec = vec+numpy.array(getWordVec(word, embeddingmodel))
  return vec.reshape(1, -1)

def word2vec_drive(file_name, question):
  pdf_txt = pdf_extract(file_name)

  import nltk
  import numpy
  import pprint

  nltk.download('punkt')
  tokens = nltk.sent_tokenize(pdf_txt)
  cleaned_sentences = get_cleaned_sentences(tokens, stopwords=True)
  cleaned_sentences_with_stopwords = get_cleaned_sentences(tokens, stopwords=False)
  sentences = cleaned_sentences_with_stopwords
  sentence_words = [[word for word in document.split()]
                    for document in sentences]

  sent_embeddings = []
  for sent in sentences:
    sent_embeddings.append(getPhraseEmbedding(sent, v2w_model))

  question_embedding = getPhraseEmbedding(question, v2w_model)
  index = retrieveAndPrintFAQAnswer(question_embedding, sent_embeddings, cleaned_sentences_with_stopwords)
  return cleaned_sentences_with_stopwords[index]

# question = "What were the various steps taken by the government to boost domestic and foreign investment in India ?"
# answer = word2vec_drive('fdi.pdf', question)
# print(answer)

"""==================================================================================================================="""

from gensim.models import Word2Vec
import gensim.downloader as api

glove_model = None
try:
  glove_model = gensim.models.Keyedvectors.load('./glovemodel.mod')
  print("Glove Model Successfully loaded")
except:
  glove_model = api.load('glove-twitter-25')
  glove_model.save("./glovemodel.mod")
  print("Glove Model Saved")

glove_embedding_size = len(glove_model['pc'])

def glove_drive(file_name, question):
  pdf_txt = pdf_extract(file_name)

  import nltk
  import numpy
  import pprint

  nltk.download('punkt')
  tokens = nltk.sent_tokenize(pdf_txt)
  cleaned_sentences = get_cleaned_sentences(tokens, stopwords=True)
  cleaned_sentences_with_stopwords = get_cleaned_sentences(tokens, stopwords=False)
  sentences = cleaned_sentences_with_stopwords
  sentence_words = [[word for word in document.split()]
                    for document in sentences]

  sent_embeddings = []
  for sent in cleaned_sentences:
    sent_embeddings.append(getPhraseEmbedding(sent, glove_model))

  question_embedding = getPhraseEmbedding(question, glove_model)
  index = retrieveAndPrintFAQAnswer(question_embedding, sent_embeddings, cleaned_sentences_with_stopwords)
  return cleaned_sentences_with_stopwords[index]

# question = "What were the various steps taken by the government to boost domestic and foreign investment in India ?"
# answer = glove_drive('fdi.pdf', question)
# print(answer)

"""==================================================================================================================="""

!pip install transformers==3.1.0
import torch
from transformers import BertForQuestionAnswering
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

def answer_question_bert(question, answer_text):

    input_ids = tokenizer.encode(question, answer_text, max_length=512, truncation=True)

    print('Query has {:,} tokens.\n'.format(len(input_ids)))

    sep_index = input_ids.index(tokenizer.sep_token_id)

    num_seg_a = sep_index + 1

    num_seg_b = len(input_ids) - num_seg_a

    segment_ids = [0]*num_seg_a + [1]*num_seg_b

    assert len(segment_ids) == len(input_ids)

    start_scores, end_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))

    all_tokens = tokenizer.convert_ids_to_tokens(input_ids)

    #print(' '.join(all_tokens[torch.argmax(start_scores) : torch.argmax(end_scores)+1]))
    #print(f'score: {torch.max(start_scores)}')
    score = float(torch.max(start_scores))
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    answer = tokens[answer_start]

    for i in range(answer_start + 1, answer_end + 1):

        if tokens[i][0:2] == '##':
          answer += tokens[i][2:]
        else:
          answer += ' ' + tokens[i]
        #if tokens[i][0:2] == ' ':
         #   answer += tokens[i][2:]

        #else:
           # answer += ' ' + tokens[i]
    return answer, score, start_scores, end_scores, tokens
    #print('Answer: "' + answer + '"')

def expand_split_sentences(pdf_txt):
  import nltk
  nltk.download('punkt')
  new_chunks = nltk.sent_tokenize(pdf_txt)
  length = len(new_chunks)
  #for i in range(length):
    #tmp_token = tokenizer.encode(new_chunks[i])
    #print('The input has a total of {:} tokens.'.format(len(tmp_token)))

  new_df = [];
  for i in range(length):
    paragraph = ""
    for j in range(i, length):
      #tmp_str = paragraph + new_chunks[j]
      tmp_token = tokenizer.encode(paragraph + new_chunks[j])
      length_token = len(tmp_token)
      if length_token < 510:
        #print(length_token)
        paragraph = paragraph + new_chunks[j]
      else:
        #print(length_token)
        break;
    #print(len(tokenizer.encode(paragraph)))
    new_df.append(paragraph)
  return new_df
  #for i in new_df:
    #print(i)

def bert_drive(file_name, question):
  import numpy
  text = pdf_extract(file_name)
  max_score = 0;
  final_answer = ""
  new_df = expand_split_sentences(text)
  tokens = []
  s_scores = numpy.array([])
  e_scores = numpy.array([])
  for new_context in new_df:
    #new_paragrapgh = new_paragrapgh + answer_question(question, answer_text)
    ans, score, start_score, end_score, token = answer_question_bert(question, new_context)
    if score > max_score:
      max_score = score
      s_scores = start_score.detach().numpy().flatten()
      e_scores = end_score.detach().numpy().flatten()
      tokens = token
      final_answer = ans
  return final_answer, s_scores, e_scores, tokens

def draw_graph(s_scores, e_scores, tokens):
  import matplotlib.pyplot as plt
  import seaborn as sns

  sns.set(style='darkgrid')
  plt.rcParams["figure.figsize"] = (48,8)
  token_labels = []
  for (i, token) in enumerate(tokens):
      token_labels.append('{:} - {:>2}'.format(token, i))
  ax = sns.barplot(x=token_labels, y=s_scores, ci=None)
  ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center")
  ax.grid(True)
  plt.title('Start Word Scores')
  plt.show()

  ax = sns.barplot(x=token_labels, y=e_scores, ci=None)
  ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center")
  ax.grid(True)
  plt.title('End Word Scores')
  plt.show()

  import pandas as pd
  scores = []
  for (i, token_label) in enumerate(token_labels):
      scores.append({'token_label': token_label,
                    'score': s_scores[i],
                    'marker': 'start'})
      scores.append({'token_label': token_label,
                    'score': e_scores[i],
                    'marker': 'end'})
  df = pd.DataFrame(scores)
  g = sns.catplot(x="token_label", y="score", hue="marker", data=df,
                kind="bar", height=9, aspect=7)
  g.set_xticklabels(g.ax.get_xticklabels(), rotation=90, ha="center")
  g.ax.grid(True)

# question = "How many insurance plans are there?"
# answer, s_scores, e_scores, tokens = bert_drive('test.pdf', question)
# print(answer)
# draw_graph(s_scores, e_scores, tokens)

# draw_graph(s_scores, e_scores, tokens)

"""==================================================================================================================="""

# !pip install cdqa

# import os
# import pandas as pd
# from ast import literal_eval

# from cdqa.utils.converters import pdf_converter
# from cdqa.pipeline import QAPipeline
# from cdqa.utils.download import download_model
#   download_model(model='bert-squad_1.1', dir='./models')
# !pip install pandas==1.1.0

# def fine_tuning_drive(question):
#   df = pdf_converter(directory_path="docs/")
#   pd.set_option('display.max_colwidth', -1)
#   df.head()
#   cdqa_pipeline = QAPipeline(reader='./models/bert_qa.joblib', max_df=1.0)
#   cdqa_pipeline.fit_retriever(df=df)
#   import joblib
#   joblib.dump(cdqa_pipeline, './models/bert_qa_custom.joblib')
#   cdqa_pipeline=joblib.load('./models/bert_qa_custom.joblib')
#   prediction = cdqa_pipeline.predict(question, 1)
#   return prediction

# question = "What were the various steps taken by the government to boost domestic and foreign investment in India ?"
# print(fine_tuning_drive(question))

"""==================================================================================================================="""

# question = "What were the various steps taken by the government to boost domestic and foreign investment in India ?"
# answer = naive_drive('fdi.pdf', question)
# print(answer)
# answer = word2vec_drive('fdi.pdf', question)
# print(answer)
# answer = glove_drive('fdi.pdf', question)
# print(answer)
# answer = (bert_drive('fdi.pdf', question)
# print(answer)
# answer = fine_tuning_drive(question)
# print(answer)



from flask import *
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

app = Flask(__name__)
run_with_ngrok(app)
@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    if(request.form.get('btn') == 'index'):
      upload = request.files['upload']
      path = "docs"
      global file_name
      file_name = upload.filename
      print(file_name)
      upload.save(os.path.join(path, secure_filename(upload.filename)))
      return redirect(url_for('qa'))
    elif (request.form.get('btn') == 'qa'):
      question = request.form.get('question')
      answer = ""
      if(func == 'naive'):
        answer = naive_drive(file_name, question)
      elif(func == 'w2v'):
        answer = word2vec_drive(file_name, question)
      elif(func == 'glove'):
        answer = glove_drive(file_name, question)
      elif(func == 'bert'):
        answer, s_scores, e_scores, tokens = bert_drive(file_name, question)
        draw_graph(s_scores, e_scores, tokens)
      else:
        answer = "Currently Fine Tunning Not Supported"
        # answer = fine_tuning_drive(question)
      #answer = fine_tuning_drive(question)
      print(answer)
      return render_template('qa.html', answer = answer, question = question)
  return render_template('index.html')
@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    global func
    func = request.args.get('type')
    return render_template('upload.html')

@app.route('/qa/', methods=['GET', 'POST'])
def qa():
    return render_template('qa.html')

!pip install pyngrok

!ngrok authtoken ENTER_YOUR_AUTH_TOKEN

app.run()
