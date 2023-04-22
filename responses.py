from pydantic import BaseModel

class RegisterError(BaseModel):
    message: str = 'User alredy in database'

class RegisterSuccess(BaseModel):
    message: str = 'register successful'

class PurchaseSuccess(BaseModel):
    message: str = 'Purchase successful'

class PurchaseCancelSuccess(BaseModel):
    message: str = 'Order canceled'

class ContactSuccess(BaseModel):
    message: str = 'Contact registered'

class LoginSuccessData(BaseModel):
    user      :str
    email     :str
    tel       :str
    address   :str

class LoginSuccessMessage(BaseModel):
    message   :str = "Login successful"

class LoginSuccess(BaseModel):
    message :LoginSuccessMessage
    data    :LoginSuccessData

class LoginError(BaseModel):
    message: str = 'Password no match'

class Itens(BaseModel):
    product     :str
    brand       :str
    amount      :int
    unitPrice   :int
    description :list[str]
    img         :str

class UserPurchases(BaseModel):
    id      :int
    date    :str
    cancel  :int
    itens   :list[Itens]

class ProductList(BaseModel):
    cetegories  :str
    itens       :list[Itens]
