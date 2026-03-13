from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel

app = FastAPI()

# Initial Products
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Product Model
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# Helper Function
def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


# -------------------------
# Q1 – Add Product
# -------------------------
@app.post("/products")
def add_product(product: Product, response: Response):

    # duplicate check
    for p in products:
        if p["name"].lower() == product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product with this name already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    response.status_code = status.HTTP_201_CREATED

    return {
        "message": "Product added successfully",
        "product": new_product
    }


# -------------------------
# Q2 – Update Product
# -------------------------
@app.put("/products/{product_id}")
def update_product(
        product_id: int,
        price: int | None = None,
        in_stock: bool | None = None,
        response: Response = None):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }


# -------------------------
# Q3 – Delete Product
# -------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {
        "message": f"Product '{product['name']}' deleted successfully"
    }


# -------------------------
# Get All Products
# -------------------------
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# -------------------------
# Q5 – Inventory Audit
# (must be above product id route)
# -------------------------
@app.get("/products/audit")
def audit_products():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 10 for p in in_stock)

    expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_names": [p["name"] for p in out_stock],
        "total_stock_value": total_value,
        "most_expensive_product": {
            "name": expensive["name"],
            "price": expensive["price"]
        }
    }


# -------------------------
# BONUS – Bulk Discount
# -------------------------
@app.put("/products/discount")
def apply_discount(
        category: str = Query(...),
        discount_percent: int = Query(..., ge=1, le=99)):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_products": updated
    }


# -------------------------
# Get Product By ID
# -------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product