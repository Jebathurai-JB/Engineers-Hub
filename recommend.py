# Importing the required libraries
from flask import Flask, render_template, request, url_for, redirect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import pickle
import string

# Reading the dataset
data = pd.read_csv('engineering_data.csv')	

# TFIDF vectorizer for recommendation
model1 = TfidfVectorizer(max_features=14000)	
model2 = TfidfVectorizer(max_features=1800)	

#vectorizer and classifier for sentiment analysis
vectorizer = pickle.load(open('sentiment_transformer.pkl', 'rb'))
classifier = pickle.load(open('sentiment_model.pkl', 'rb')) #SVM algorithm

x = model1.fit_transform(data['recommend char'])
y = model2.fit_transform(data['recommend char2'])

cosine_recommend1 = cosine_similarity(x, x)	

indices = pd.Series(data.index, index=data['title'].str.lower()).drop_duplicates()	

def suggestion_func(x):
	d = data['lower title']
	index = []
	x = x.split(' ')
	for i in range(data.shape[0]):
	    if len(x) == 1:
	        if x[0] in d[i]:
	            index.append(i)
	    if len(x) == 2:
	        if x[0] in d[i] and x[1] in d[i]:
	            index.append(i)
	    if len(x) == 3:
	        if x[0] in d[i] and x[1] in d[i] and x[2] in d[i]:
	            index.append(i)
	    if len(x) == 4:
	        if x[0] in d[i] and x[1] in d[i] and x[2] in d[i] and x[3] in d[i]:
	            index.append(i)
	    if len(x) == 5:
	        if x[0] in d[i] and x[1] in d[i] and x[2] in d[i] and x[3] in d[i] and x[4] in d[i]:
	            index.append(i)
	    if len(x) == 6:
	    	if x[0] in d[i] and x[1] in d[i] and x[2] in d[i] and x[3] in d[i] and x[4] in d[i] and x[5]in d[i]:
	            index.append(i)
	    if len(x) == 7:
	    	if x[0] in d[i] and x[1] in d[i] and x[2] in d[i] and x[3] in d[i] and x[4] in d[i] and x[5]in d[i] and x[6] in d[i]:
	            index.append(i)
	return index	            

def recommend1(book_title, sig=cosine_recommend1):
    idx = indices[book_title]
    sig_scores = list(enumerate(cosine_recommend1[idx]))
    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
    sig_scores = sig_scores[1:11]
    book_indices = [i[0] for i in sig_scores]
    a = data[['title', 'author', 'medium image', 'clean desc']].iloc[book_indices]
    a = a.reset_index(drop=True)
    b = data[['title', 'author', 'desc', 'pages', 'publisher', 'year', 'language', 'file', 
    'large image']].iloc[idx]
    return a, b, idx

def recommend2(searched_books):
	searched_words = model2.transform(searched_books)
	cosine_recommend2 = cosine_similarity(searched_words, y)
	sig_scores = list(enumerate(cosine_recommend2[0]))
	sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
	sig_scores = sig_scores[1:19]
	book_indices = [i[0] for i in sig_scores]
	a = data[['title', 'large image']].iloc[book_indices]
	a = a.reset_index(drop=True)
	return a

searched_books = []  #list to store the searched books
def show_searched_book():   #This function is used to activate the list (searched_books)
	return searched_books       # Will return the list

def append_searched_book(x):# This function is used to append the book_title in the searched boooks list
	searched_books = show_searched_book() # this is used to activate the the list....
	searched_books = searched_books.insert(0, x)   # adding the book title in the list
	return searched_books


def cleaning(text):
	text = ''.join([char for char in text if char not in string.punctuation])
	return text


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():

	if request.method == 'POST':	

		book_title = request.form['book']
		book_title = book_title.lower()

		searched_books = append_searched_book(book_title)

		if book_title not in list(data['title'].str.lower()):
			suggestion = suggestion_func(book_title)
			no_of_books = len(suggestion)

			search_title = book_title.title()
			book_title = data['title']
			book_author = data['author']
			publisher = data['publisher']
			image = data['medium image']
			year = data['year']	
			language = data['language']	
			file = data['file']

			if len(suggestion) == 0:
				return render_template('unavailable.html', title='Engineers Hub',
					search_title=search_title)
			else:
				return render_template('books.html', title='Engineers Hub',book_title=book_title, image=image,
				book_author=book_author, publisher=publisher, year=year, language=language, file=file,
				suggestion=suggestion, search_title=search_title, no_of_books=no_of_books) 

		else:
			recommendation, info, index = recommend1(book_title, cosine_recommend1)
			book_title = info['title']
			book_author = info['author']
			book_desc = info['desc']
			image = info['large image']
			publisher = info['publisher']
			book_page = info['pages']
			year = info['year']	
			language = info['language']	
			file = info['file']

			return render_template('recommend.html', title='Engineers Hub',book_title=book_title, 
				book_author=book_author, book_desc=book_desc,image=image, publisher=publisher,
				book_page=book_page, year=year,language=language, file=file, recommendation=recommendation)
	
	else:
		searched_books = show_searched_book()
		no_of_searched_books = len(searched_books)
		if no_of_searched_books > 10:
			searched_books = searched_books[:10]
		else:
			pass

		searched_books_str = ''
		for i in searched_books:
			searched_books_str = ' '.join(searched_books)
		searched_books_str = [searched_books_str]

		if no_of_searched_books > 0:
			most_popular_books = recommend2(searched_books_str)
			book_title = most_popular_books['title']
			image = most_popular_books['large image']
		else:
			image = None
			book_title = None

		return render_template('home.html', title='Engineers Hub', image=image, book_title=book_title, 
			no_of_searched_books=no_of_searched_books)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
	if request.method == 'POST':
		name = request.form['name']
		message = request.form['message']
		len_message = len(message)
		message = message.lower()
		clean_message = cleaning(message) 
		message_vec = vectorizer.transform([clean_message])
		result = classifier.predict(message_vec)
		len_result = len(result)
		return render_template('contact.html', title='Engineers Hub', name=name, result=result,
			len_message=len_message, len_result=len_result)
	else:
		return render_template('contact.html', title='Engineers Hub')


@app.route('/about')
def about():
	return render_template('about.html', title='About')


if __name__ == "__main__":
    app.run(debug=True)