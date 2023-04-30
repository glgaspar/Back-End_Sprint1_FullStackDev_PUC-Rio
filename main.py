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


@app.post("/login", tags=['user'], responses={400: {"model": LoginError}, 200: {"model":LoginSuccess}})
def login(Login:Login, response:Response):
    """
    Logs in user

    Returns message with login confirmation or rejection and user data
    """

    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    validation = cursor.execute(f"SELECT EMAIL, PASSWORD  FROM  LOGIN WHERE  EMAIL='{Login.email}'")
    validation_pass = validation.fetchone()
    
    if validation_pass and validation_pass[1] == Login.pssw:
        user_info = cursor.execute(f"SELECT  NAME, EMAIL, TEL, ADDRESS FROM USERS WHERE EMAIL = '{Login.email}'").fetchone()
        message = {
            "message":"Login successful"
        }
        data = {
            "user":user_info[0],
            "email":user_info[1],
            "tel":user_info[2],
            "address":user_info[3],
        }
    else:
        response.status_code=status.HTTP_400_BAD_REQUEST
        message = {
            "message":"Password no match"
        }
        data = {}
    return {'message':message,'user':data}


@app.get("/products", tags=['product'], responses={200: {"model":list[ProductList] }})
def products():
    """
    Fetches all data about the products from db
    
    Returns item details grpuped by category.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    products =  cursor.execute(f"""
        SELECT P.ID, P.NAME, P.DESCRIPTION, P.PRICE, P.CATEGORY, P.LINK AS IMG
        , B.NAME AS BRAND
        FROM PRODUCTS P
        JOIN BRANDS B
            ON B.ID = P.BRAND_ID
        """).fetchall()

    categories = cursor.execute(f"""
        SELECT DISTINCT CATEGORY 
        FROM PRODUCTS
        """).fetchall()    
    
    product_list = []
    for category in categories:
        product_list.append(
            {'categories':category[0],
            'itens': [
                        {
                            'id':product[0]
                            ,'name':product[1]
                            ,'description':product[2]
                            ,'price':product[3]
                            ,'category':product[4]
                            ,'img':product[5]
                            ,'brand':product[6]
                        }
                        for product in products if product[4]==category[0]
                    ]
            }
        )
    return {"product":product_list}


@app.get("/productDetail", tags=['product'], responses={200: {"model": Itens}})
def products(productId:int):
    """
    Fetches all data about a product from db
    
    Returns object with all data about requested product.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    product =  cursor.execute(f"""
        SELECT 
            P.ID, P.NAME, P.DESCRIPTION, P.PRICE, P.CATEGORY, P.LINK AS IMG
            , B.NAME AS BRAND
        FROM PRODUCTS P
        JOIN BRANDS B
            ON B.ID = P.BRAND_ID
        WHERE P.ID = {productId}
        """).fetchone()

    return {
            'id':product[0]
            ,'name':product[1]
            ,'description':[i for i in product[2].split(' | ')]
            ,'unitPrice':product[3]
            ,'category':product[4]
            ,'img':product[5]
            ,'brand':product[6]
            }


@app.post("/newPurchase", tags=['purchase'], responses={200: {"model": PurchaseSuccess}})
def new_purchase(NewPurchase:NewPurchase):
    """
    Registers new purchase in db
    
    Returns a message confirming success or not.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    cursor.execute(f"""INSERT INTO ORDERS (USER_ID, DATE, CANCEL)
                    VALUES('{NewPurchase.email}', DATETIME('now'), 0)""")
                    
    newOrderId = cursor.execute(f"SELECT MAX(ID) as id FROM ORDERS").fetchone()
    cursor.execute(f"""INSERT INTO ORDER_ITENS (ORDER_ID, PRODUCT_ID, AMOUNT, UNIT_PRICE)
                    VALUES('{newOrderId[0]}', {NewPurchase.productId}, {NewPurchase.amount}, {NewPurchase.unitPrice} )
                    """)
    db.commit()
    return {'message':'Purchase successful'}


@app.get("/purchases", tags=['purchase'], responses={200: {"model": UserPurchases}})
def purchases(userEmail:str):
    """
    Fetches all data about user purchases
    
    Returns array of purchases with neste array of itens related to the purchase.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    orders =  cursor.execute(f"""
        SELECT O.ID,  O.DATE, O.CANCEL
        FROM ORDERS O
        JOIN USERS U
            ON U.EMAIL = O.USER_ID
        WHERE O.USER_ID = '{userEmail}'
        """).fetchall()

    itens =  cursor.execute(f"""
    SELECT 
        I.ORDER_ID, P.NAME AS PRODUCT, B.NAME AS BRAND, I.AMOUNT, I.UNIT_PRICE
        , P.LINK AS IMG
    FROM ORDER_ITENS I
    JOIN PRODUCTS P ON P.ID = I.PRODUCT_ID
    JOIN BRANDS B ON B.ID = P.BRAND_ID
    JOIN ORDERS O ON O.ID = I.ORDER_ID
    WHERE O.USER_ID = '{userEmail}'""").fetchall()

    order_list = []
    for order in orders:
        order_list.append(
            {'id':order[0],
            'date':order[1],
            'cancel':order[2],
            'itens':[{'product':item[1],'brand':item[2],'amount':item[3],'unitPrice':item[4], 'img':item[5]} for item in itens if item[0]==order[0]]
            }
        )
    return {"orders":order_list}


@app.put('/cancelOrder', tags=['purchase'], responses={200: {"model": PurchaseCancelSuccess}})
def cancel_purchase(orderId:int):
    """
    Changes the cancel status of an order from 0 to 1
    
    Returns a message confirming the operation.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    cursor.execute(f"""UPDATE ORDERS
                    SET CANCEL = 1 WHERE ID = {orderId}""")
    db.commit()
    return {'message':'Order canceled'}


@app.post('/contact', tags=['contact'], responses={200: {"model": ContactSuccess}})
def contact(Contact:Contact):
    """
    Registers a message sent by an user to the db
    
    Returns a message confirming the operation.
    """
    
    db = sqlite3.connect('db.db')
    cursor = db.cursor()
    cursor.execute(f"""INSERT INTO CONTACT (NAME, EMAIL, TEL, MESSAGE)
                    VALUES('{Contact.name}','{Contact.email}','{Contact.tel}','{Contact.message}')""")
    db.commit()
    return {'message':'Contact registered'}


hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=3001)
