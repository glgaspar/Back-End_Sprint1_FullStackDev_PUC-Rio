from fastapi import FastAPI, Response, status
import sqlite3
from responses import *
from  schemas import Contact, Login, Register, NewPurchase
import socket  
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

description="""
API feita para o Back-end do sprint 1 da Pós-graducação em Desenvolvimento FullStack - PUC-RJ

Essa API controla todas as ações relacionadas a busca e envio de dados necessários 
para o Front-end desenvolvido em paralelo.
"""

app = FastAPI(title="Sprint1 Back-end",
    description=description,
    version="0.0.1",
    contact={
        "name": "Gustavo Gaspar",
        "url": "https://github.com/glgaspar"
    })

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/newUser", tags=['user'], responses={400: {"model": RegisterError}, 200: {"model":RegisterSuccess}})
def register(register:Register, response:Response):
    """
    Creates new user in db
    
    Returns message saying wether the registration was successful or not.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    try:
        cursor.execute(f"""INSERT INTO LOGIN (EMAIL, PASSWORD)
                        VALUES('{register.email}','{register.pssw}' )""")
        db.commit()

    except sqlite3.IntegrityError:
        response.status_code=400
        return {"message":'User alredy in database'}
    
    cursor.execute(f"""INSERT INTO USERS
                    VALUES('{register.email}','{register.name}','{register.tel}','{register.address}') """)
    db.commit()
    
    
    return {"message":'register successful'}



hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3001)
