import cv2
import numpy as np
from flask import request, jsonify
from app.utils.barcode_utils import read_barcode_production
from app.config.db_config import product_collection

def scan_and_get_product():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    scan_result = read_barcode_production(image)
    
    if scan_result.get("error"):
        return jsonify({"error": "Could not read barcode"}), 422
    
    barcode_value = scan_result["barcode"]

    # 3. Search in MongoDB
    # Based on your Mongoose schema: items -> variants -> barcode
    try:
        # client = get_mongo_db()
        # db = client.get_default_database() # or specific DB name
        # collection = db["itemcategories"] 

        product_doc = product_collection.find_one(
            {"items.variants.barcode": barcode_value},
            {"items.$": 1, "category": 1} 
        )

        if not product_doc:
            return jsonify({
                "barcode": barcode_value,
                "msg": "Product not found in database"
            }), 404


        return jsonify({
            "barcode": barcode_value,
            "source": scan_result["source"],
            "category": product_doc.get("category"),
            "product_details": product_doc.get("items")[0] 
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500