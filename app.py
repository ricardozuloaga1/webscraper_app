from flask import Flask, render_template, request, redirect, url_for, flash
from scraper import get_product_details_with_selenium
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def is_valid_url(url):
    return re.match(r'^https?://', url)

def construct_aliexpress_search_url(keyword):
    base_url = "https://www.aliexpress.com/wholesale"
    search_url = f"{base_url}?SearchText={keyword.replace(' ', '+')}"
    return search_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        page_url = request.form.get('url')
        keyword = request.form.get('keyword')
        pages_to_scrape = int(request.form.get('pages', 10))

        if page_url and is_valid_url(page_url):
            products = get_product_details_with_selenium(page_url, pages_to_scrape)
        elif keyword:
            search_url = construct_aliexpress_search_url(keyword)
            products = get_product_details_with_selenium(search_url, pages_to_scrape)
        else:
            flash('Please enter a valid URL or a keyword to search.')
            return redirect(url_for('index'))

        return render_template('index.html', products=products)

    return render_template('index.html', products=None)

if __name__ == '__main__':
    app.run(debug=True)
