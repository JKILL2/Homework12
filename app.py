# import libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# create instance of flask app
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"

# use flask_pymongo to set up mongo connection
mongo = PyMongo(app)

# create route that renders index.html template and finds docs from mongo
@app.route("/")
def home():

    # find data
    mars_db = mongo.db.mars_db.find()

    # return template and data
    return render_template("index.html", mars_db=mars_db)

# route that will trigger scrape functions
@app.route("/scrape")
def scrape():

    # run scraping function
    news = scrape_mars.scrape()
    
    # store results into a dictionary
    content = {
        "news_title": news["news_title"],
        "news_blurb": news["news_blurb"],
        "featured_image_url": news["featured_image_url"],
        "mars_weather": news["mars_weather"],
        "mars_facts": news["mars_facts_html"],
        "hemisphere_image_urls": news["hemisphere_image_urls"]
    }

    # delete previous news content
    mongo.db.mars_db.drop()

    # insert new content into database
    mongo.db.mars_db.insert_one(content)

    # redirect back to home page
    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)