# Importing the required libraries
from flask import Flask, render_template, request, url_for, redirect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import speech_recognition as sr
import pandas as pd
# import base64
# from flask_ngrok import run_with_ngrok
# from flask_cors import CORS
# from IPython.display import display

# import pytesseract
# pytesseract.pytesseract.tesseract_cmd=r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


data = pd.read_csv('engineering_data.csv')		#reading the data
pdf_authors_name = pd.read_csv('authors.csv')

model = TfidfVectorizer(max_features=None)	

x = model.fit_transform(data['recommend char'])

cosine_recommend = cosine_similarity(x,x)		#cosine similarity for authors

indices = pd.Series(data.index, index=data['title'].str.lower()).drop_duplicates()		#indices of the book title


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


def recommend(book_title, sig=cosine_recommend):
    idx = indices[book_title]
    sig_scores = list(enumerate(cosine_recommend[idx]))
    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
    sig_scores = sig_scores[1:11]
    book_indices = [i[0] for i in sig_scores]
    a = data[['title', 'author', 'medium image', 'clean desc']].iloc[book_indices]
    a = a.reset_index(drop=True)
    b = data[['title', 'author', 'desc', 'download_link', 'pages','publisher','year', 'language',
    'file', 'large image']].iloc[idx]
    return a, b, idx


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
	
	if request.method == 'POST':	
		try:
			name = request.form['speech']
			if name == 'microphone':
				r = sr.Recognizer()
				with sr.Microphone() as source:
					r.pause_threshold = 0.6
					audio = r.listen(source)
					try:
						ask = r.recognize_google(audio, language='en-us')
						book_title = ask
						book_title = book_title.lower()
					except:
						return render_template('home.html', title='Engineers Hub')


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
						recommendation, info, index = recommend(book_title, cosine_recommend)
						book_title = info['title']
						book_author = info['author']
						book_desc = info['desc']
						book_download_link = info['download_link']
						image = info['large image']
						publisher = info['publisher']
						book_page = info['pages']
						year = info['year']	
						language = info['language']	
						file = info['file']

						pdf_name = pdf_authors_name.rename({'authors name':'authorsname'}, axis=1)
						pdf_name = '{} by {}'.format(data.title[index], pdf_name.authorsname[index])
						pdf_name = pdf_name.replace(':', '')
						pdf_name = pdf_name.replace("'", '')
						pdf_name = pdf_name[:200]
						pdf_name = pdf_name + ' (z-lib.org)'

						return render_template('recommend.html', title='Engineers Hub' ,book_title=book_title, book_author=book_author,
							book_desc=book_desc,book_download_link=book_download_link,image=image, publisher=publisher,
							book_page=book_page, year=year,language=language, file=file, recommendation=recommendation,
							pdf_name=pdf_name)



			
		except:
			book_title = request.form['book']
			book_title = book_title.lower()

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
				recommendation, info, index = recommend(book_title, cosine_recommend)
				book_title = info['title']
				book_author = info['author']
				book_desc = info['desc']
				book_download_link = info['download_link']
				image = info['large image']
				publisher = info['publisher']
				book_page = info['pages']
				year = info['year']	
				language = info['language']	
				file = info['file']

				pdf_name = pdf_authors_name.rename({'authors name':'authorsname'}, axis=1)
				pdf_name = '{} by {}'.format(data.title[index], pdf_name.authorsname[index])
				pdf_name = pdf_name.replace(':', '')
				pdf_name = pdf_name.replace("'", '')
				pdf_name = pdf_name[:200]
				pdf_name = pdf_name + ' (z-lib.org)'

				return render_template('recommend.html', title='Engineers Hub' ,book_title=book_title, book_author=book_author,
					book_desc=book_desc,book_download_link=book_download_link,image=image, publisher=publisher,
					book_page=book_page, year=year,language=language, file=file, recommendation=recommendation,
					pdf_name=pdf_name)

	else:
		return render_template('home.html', title='Engineers Hub')


@app.route('/team')
def team():
	return render_template('team.html', title='Engineers Hub Team')


@app.route('/about')
def about():
	return render_template('about.html', title='About')

#camera not in production yet ----------------------------------------------------------------------
# @app.route('/camera', methods=['GET', 'POST'])
# def capturephoto():
# 	if request.method == 'POST':

# 		Img = request.data
# 		imgdata = base64.b64decode(Img)
# 		char = request.form['useless']
# 		# text = pytesseract.image_to_string(Img)
# 		return render_template('new.html', title='Not None', Img=imgdata, char=char)
# 		# return render_template('new.html', title='None')

# 	else:
# 		return render_template('webcam.html', title='None')
#-----------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)