from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

print(1)
print(1)
print(1)
print(1)
print(1)
print(1)

if __name__ == '__main__':
    app.run()
