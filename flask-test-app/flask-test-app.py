from flask import Flask, url_for, render_template

SETTINGS = {
	"flask": {
		"host": "localhost",
		"port": 5000,
		"debug": True,
	}
}

app = Flask(__name__)
app.debug = SETTINGS["flask"]["debug"]

@app.route("/")
def page_index():
	css_path = url_for("static", filename="base.css")
	return render_template("index.html", name="foo", css=css_path)

if __name__ == "__main__":
	app.run(**SETTINGS["flask"])
