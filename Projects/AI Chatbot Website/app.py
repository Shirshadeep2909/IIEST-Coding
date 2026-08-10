from flask import *
from ai import ask_ai
from database import *

app=Flask(__name__)


conversation=[]


create_database()



@app.route("/")
def home():

    return render_template(
        "index.html"
    )



@app.route("/chat",methods=["POST"])

def chat():

    data=request.json


    msg=data["message"]

    mode=data["mode"]



    conversation.append(

    {
    "role":"user",
    "content":msg
    }

    )


    save_message(
        "user",
        msg
    )


    reply=ask_ai(
        conversation,
        mode
    )


    conversation.append(

    {
    "role":"assistant",
    "content":reply
    }

    )


    save_message(
        "assistant",
        reply
    )


    return jsonify(
    {
    "reply":reply
    })




app.run(debug=True)