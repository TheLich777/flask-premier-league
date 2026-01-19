from epl import app

@app.route('/')
def index():
    return "Welcome to the Premier League Flask App!"