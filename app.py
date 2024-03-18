#API Functions
#--------------------------------------
#Imports
import pymongo
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
from bson import ObjectId
from typing import Optional

app = FastAPI()


#-------------usersDataBase------------#

#Conexion
client = pymongo.MongoClient('mongodb+srv://apitodolist:abacux64@cluster0.6dzr981.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
basedD = client['ToDoList']
collection = basedD['tasks']
#Esquema
class Task(BaseModel):
   id: Optional[str]="opcional"
   task: str
   isDone: Optional[str]="false"

"""{
  "id": "id",
  "task": "userName",
  "isDone": "password"
}"""

def task_schema(task) -> dict:
    return {"id": str(task["_id"]),
        "task": task["task"],
        "isDone": task["isDone"]}


def tasks_schema(tasks) -> list:
    return [task_schema(task) for task in tasks]

#Funciones
#find
@app.get("/")
async def read_root():
   return {"API": "ToDoList"}

@app.get("/tasks/", response_model=list[Task])
async def getTasks():
      return tasks_schema(collection.find())

@app.get("/one-task/{itemId}", response_model=Task)
async def getOneTask(itemId:str):
      return search_task("_id", ObjectId(itemId))

@app.post("/post-task/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def postTask(modelo:Task):
    if type(search_task("task",modelo.task)) == Task:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="La tarea ya existe")
    task_dict = dict(modelo)
    del task_dict["id"]
    id = collection.insert_one(task_dict).inserted_id
    new_task = task_schema(collection.find_one({"_id":id}))
    return Task(**new_task)

@app.put("/put-task/{itemId}", response_model=Task)
async def putTask(itemId:str, modelo:Task):
    dict_modelo = dict(modelo)
    del dict_modelo["id"]
    try:
        collection.find_one_and_replace({"_id":ObjectId(modelo.id)},dict_modelo)
    except:
        return {"Error":"No se ha actualizado la tarea"}
    return search_task("_id", ObjectId(modelo.id))

@app.delete("/delete-task/{itemId}", status_code=status.HTTP_301_MOVED_PERMANENTLY)
async def deleteTask(itemId:str):
  
  found = collection.delete_one({"_id":ObjectId(itemId)})

  if not found:
      return {"Error":"No se ha encontrado la tarea"}

@app.delete("/delete-all/", status_code=status.HTTP_205_RESET_CONTENT)
async def deleteAllTask():
  
  found = collection.delete_many({})

  if not found:
      return {"Error":"No se han encontrado tareas"}


def search_task(field: str, key):
    try:
        task = collection.find_one({field:key})
        return Task(task_schema(task))
    except:
        return {"Error":"No se ha encontrado la tarea"}
