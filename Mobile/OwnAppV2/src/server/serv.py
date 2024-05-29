from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def root():
    return ''

@app.route('/score_from_user_app_android')
def winner():
    if request.headers.get("User-Agent") and request.headers["User-Agent"] == "Dart/2.18 (dart:io)":
        if request.args.get("score") and request.args["score"].isdigit():
            score = int(request.args["score"])
            if score < 133337:
                return "Your score is " + str(score) +" from the android app, gg, but you're not the best, the best is Kaluche with a score of 133337, sooo no flag for u :("
            elif score > 133337:
                return "Oh, you beat Kaluche, here is your reward: BZHCTF{flutt3r_c4n_b3_tr1cky_t0_byp4ss}"
        else:
            return "WTF dude" 
    elif request.args.get("score") and request.args["score"].isdigit(): 
        return "Your score is "+request.args["score"]+" from the web app, but i don't trust webbers like u, go away!"
    else:
        return "WTF dude"

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
