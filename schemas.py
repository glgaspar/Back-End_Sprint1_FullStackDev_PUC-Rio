from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str = Field(description='Message sender`s name.'.upper())
    email: str = Field(description='Message sender`s email.'.upper())
    tel: str or None = Field(description='Message sender`s telephone.'.upper())
    message: str = Field(description='Message to be stored.'.upper())

class Login(BaseModel):
    email: str = Field(description='User`s login in the service.'.upper())
    pssw: str = Field(description='User`s password in the service.'.upper())

class Register(BaseModel):
    email: str = Field(description='User`s login in the service.'.upper())
    pssw: str = Field(description='User`s password in the service.'.upper())
    name: str = Field(description='Message sender`s name.'.upper())
    tel: str = Field(description='Message sender`s telephone.'.upper())
    address:str = Field(description='Message sender`s telephone.'.upper())

class NewPurchase(BaseModel):
    email: str = Field(description='User ID in the service.'.upper())
    productId: int = Field(description='Purchased iten ID.'.upper())
    amount: int = Field(description='Amount purchased.'.upper())
    unitPrice:float = Field(description='Unit price at time of sale.'.upper())