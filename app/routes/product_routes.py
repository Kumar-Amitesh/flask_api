from flask import Blueprint
from app.controllers.product_controllers import scan_and_get_product

product_bp = Blueprint(
    "product",
    __name__,
    url_prefix="/product"
)

product_bp.route("/scan", methods=["POST"])(scan_and_get_product)