from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def hello_airtel():
    return render_template('home.html')

@app.route("/signup/")
def signup_page():
  print("Control signup  here.....")
  return render_template("signup.html")

print(__name__)
if __name__ == "__main__":
    print("I am in if")
    app.run(host ='0.0.0.0',port=8080, debug=True)
    