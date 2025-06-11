from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello_world():
    return "Hello, Joges !"

print(__name__)
if __name__ == "__main__":
    print("I am in if")
    app.run(host ='0.0.0.0',port=8080, debug=True)
    