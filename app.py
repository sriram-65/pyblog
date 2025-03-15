from flask import Flask,jsonify,render_template,request,redirect
import cloudinary
import cloudinary.uploader
from pymongo import MongoClient

app = Flask(__name__)

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
    collect_data  = list(User_Upload.find({} , {"_id":0}))
    print("Fetched Data:", collect_data)
    return render_template("index.html" , data=collect_data)
    
@app.route("/recent")
def recent():
    recents = User_Upload.find().sort("_id" , -1)
    return render_template("recent.html" , recents = recents)

@app.route("/detail")
def detail():
    return render_template("postdetail.html")

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
            {"Description":
                {
                    "$regex": query, "$options": "i"
                }
            }, 
            {"Category": 
                {
                    "$regex": query, "$options": "i"
                }
            },   
            {"Author": 
                {
                    "$regex": query, "$options": "i"
                }
            }   
            ]
        })
    return render_template("searchR.html" , result = search_res,q=query)

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

        image = cloudinary.uploader.upload(user_file)
        image_url = image.get("secure_url")

        DATA = {
            "Title": user_title,
            "Description": user_des,
            "Author": user_author,
            "Category": user_cat,
            "Image_url": image_url
        }

        User_Upload.insert_one(DATA) 

        return redirect("/")

    except Exception as e:
        return f"Upload failed: {str(e)}", 500  


@app.route("/uploadge")
def upload_page():
    return render_template("upload.html")

@app.errorhandler(404)
def notfound(a):
    return render_template("404.html" , url=request.path) , 404
    
if __name__ == "__main__":
    app.run(debug=True)