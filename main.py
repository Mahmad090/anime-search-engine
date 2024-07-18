

#if __name__ == '__main__':
#    app.run(debug=True, port=os.getenv("PORT", default=5000))
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')
@app.route('/initial_response', methods=['GET'])
def initial_response():
    filename = 'initial_response.wav'
    predefined_text=generate_response("Start",True)
    text_to_wav(predefined_text, filename)
    return send_file(filename, mimetype='audio/wav')
if __name__ == '__main__':
  app.run(port=5000)
