#API Functions
#--------------------------------------
#Imports
import pymongo
from pydantic import BaseModel
from fastapi import FastAPI
from bson import ObjectId

app = FastAPI()


#-------------usersDataBase------------#

#Conexion
client = pymongo.MongoClient('mongodb+srv://apitodolist:abacux64@cluster0.6dzr981.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
basedD = client['ToDoList']
collection = basedD['tasks']
#Esquema
class Task(BaseModel):
   id: str
   task: str
   isDone: str

"""{
  "id": "id",
  "task": "userName",
  "isDone": "password"
}"""

def userSchema(task) -> dict:
   print(task)
   return {"_id": str(task["id"]),
            "task": task["task"],
            "isDone": task["isDone"]}

#Funciones
#find
@app.get("/")
async def read_root():
   return {"API": "ToDoList"}

@app.get("/tasks/")
async def getTasks():
      data = {}
      for u in collection.find({}):
          data[str(u["_id"])] = u
      return data

@app.get("/one-task/{itemId}")
async def getOneTask(itemId:str):
      data = collection.find_one({itemId})
      return data

@app.post("/post-task/")
async def postTask(modelo:Task):
   dict_modelo = dict(modelo)
   idValue= dict_modelo["id"]
   dict_modelo.pop("id")
   dict_modelo["_id"]=idValue

   collection.insert_one(dict_modelo)

@app.put("/put-task/{itemId}")
async def putTask(itemId:str, modelo:Task):
    dict_modelo = dict(modelo)
    idValue= dict_modelo["id"]
    dict_modelo.pop("id")
    dict_modelo["_id"]=idValue

    collection.find_one_and_replace({"_id":itemId},dict_modelo)

@app.delete("/delete-task/{itemId}")
async def deleteTask(itemId:str):
  collection.delete_one({"_id":itemId})
