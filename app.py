from flask import Flask,jsonify,render_template,request,redirect,url_for
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai
from datetime import datetime


app = Flask(__name__)

genai.configure(api_key="AIzaSyAvyLEzkIaibw5BFF4ZCISLljZNbLKd2Cg")
model = genai.GenerativeModel("gemini-2.0-flash")

cloudinary.config(
     cloud_name="dbrmvywb0",
    api_key="799647841433247",
    api_secret="XLtCOYXxRTnjZqwaF2oFnQ0AK7k"
)
client = MongoClient("mongodb+srv://sriram65raja:1324sriram@cluster0.dejys.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
data_base = client["ai"]
User_Upload = data_base["UserUpload"]

@app.route("/")
def home():
    collect_data  = list(User_Upload.find({} , {"_id":1 , "Title":1 , "Description":1 , "Author":1, "Category":1, "Image_url":1}))
    return render_template("index.html" , data=collect_data)


@app.route("/recent")
def recent():
    recents = User_Upload.find().sort("_id" , -1)
    return render_template("recent.html" , recents = recents)


@app.route("/genDes/")
def genDes():
    prompts = request.args.get("prompt")
    Gentext = model.generate_content(f'Generate a description about this title and give only the description and display the text content on the text editor about a 250 words: {prompts} ')
    return jsonify({"description": Gentext.text})  



@app.route('/post/<post_id>')
def post_details(post_id):
    post = User_Upload.find_one({"_id": ObjectId(post_id)})
    
    return render_template('post_details.html', post=post)


@app.route("/search" , methods=["GET"])
def search():
    query = request.args.get("query" , "").strip()
    if not query:
        return jsonify({"Error":"Unable To Fetch"})
    else:
        search_res = User_Upload.find({
            "$or":[
            {"Title" : 
                {
                    "$regex":query , "$options":"i"
                }
            },
           
            {"Category": 
                {
                    "$regex": query, "$options": "i"
                }
            },   
           
            ]
        })
    return render_template("searchR.html" , result = search_res,q=query)


PASSSWORD = "1324meta"
@app.route("/dash/page/Auth/<password>/functions/getPage")
def dash(password):
    if(password == PASSSWORD):
           dashPost = User_Upload.find({} , {"_id":1 , "Title":1})
           cout_post = User_Upload.count_documents({})
           return render_template("DashBoard.html" , posts=dashPost , count= cout_post)
    else:
        return render_template("Err.html" , msgs = "You Are Not A Developer")
        
 


@app.route("/del/<post_id>" , methods=["POST"])
def delete(post_id):
    try:
        User_Upload.delete_one({"_id":ObjectId(post_id)})
        return redirect(url_for("home"))
        
    except:
        return jsonify({"ERROR" : "ERROR ON DELETING THE POST"})
        
@app.route("/upload", methods=["POST"])
def upload():
    try:
        user_title = request.form.get("title")
        user_des = request.form.get("des")
        user_author = request.form.get("author")
        user_cat = request.form.get("cat")
        user_file = request.files.get("file")

        if not user_title or not user_des or not user_author or not user_cat or not user_file:
            return "Missing required fields", 400  

        image = cloudinary.uploader.upload(user_file ,  resource_type="auto") 
        image_url = image.get("secure_url")

        DATA = {
            "Title": user_title,
            "Description": user_des,
            "Author": user_author,
            "Category": user_cat,
            "Image_url": image_url,
            "Create_at":datetime.utcnow(),
          
            
        }

        User_Upload.insert_one(DATA) 

        return redirect("/")

    except Exception as e:
        return f"Upload failed: {str(e)}", 500  


@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/uploadge")
def upload_page():
    return render_template("upload.html")


@app.errorhandler(404)
def notfound(a):
    return render_template("404.html" , url=request.path) , 404
    
if __name__ == "__main__":
    app.run(debug=True , port=1111)
