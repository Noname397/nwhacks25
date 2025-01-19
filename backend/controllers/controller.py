from flask import Blueprint, request, jsonify
from bson import ObjectId
from backend.models.model import items_collection, item_schema, items_schema
from marshmallow import ValidationError

item_blueprint = Blueprint('items', __name__)

# Helper function to convert MongoDB document to a JSON-serializable dict
def serialize_doc(document):
    """
    Convert a MongoDB document into a dict that can be JSON-serialized,
    converting the ObjectId to a string.
    """
    document['_id'] = str(document['_id'])
    return document


# ------------------------------------------------------------------------------
# CREATE: Add a new item
# ------------------------------------------------------------------------------
@item_blueprint.route('', methods=['POST'])
def create_item():
    """
    POST /items
    Body JSON example:
    {
      "name": "Example Item",
      "quantity": 10,
      "price": 29.99
    }
    """
    try:
        data = request.get_json()
        validated_data = item_schema.load(data)  # Validate input with Marshmallow
        result = items_collection.insert_one(validated_data)
        return jsonify({
            "message": "Item created successfully",
            "item_id": str(result.inserted_id)
        }), 201
    except ValidationError as ve:
        return jsonify({"error": ve.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------------
# READ: Get all items
# ------------------------------------------------------------------------------
@item_blueprint.route('', methods=['GET'])
def get_items():
    """
    GET /items
    Returns a list of all items in the collection.
    """
    try:
        all_items = list(items_collection.find())
        serialized = [serialize_doc(item) for item in all_items]
        return jsonify(serialized), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------------
# READ: Get a single item by ID
# ------------------------------------------------------------------------------
@item_blueprint.route('/<string:item_id>', methods=['GET'])
def get_item(item_id):
    """
    GET /items/<item_id>
    Returns a single item by its ObjectId.
    """
    try:
        document = items_collection.find_one({"_id": ObjectId(item_id)})
        if document:
            return jsonify(serialize_doc(document)), 200
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------------
# UPDATE: Update a single item by ID
# ------------------------------------------------------------------------------
@item_blueprint.route('/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    PUT /items/<item_id>
    Body JSON example for updates (any subset of fields):
    {
      "quantity": 5,
      "price": 19.99
    }
    """
    try:
        data = request.get_json()
        # Optionally validate partial data with the schema (partial=True)
        # item_schema.load(data, partial=True)

        update_result = items_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": data}
        )
        if update_result.modified_count == 1:
            return jsonify({"message": "Item updated successfully"}), 200
        else:
            return jsonify({"error": "Item not found or no changes made"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------------
# DELETE: Remove a single item by ID
# ------------------------------------------------------------------------------
@item_blueprint.route('/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    DELETE /items/<item_id>
    Deletes an item from the collection by its ObjectId.
    """
    try:
        delete_result = items_collection.delete_one({"_id": ObjectId(item_id)})
        if delete_result.deleted_count == 1:
            return jsonify({"message": "Item deleted successfully"}), 200
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
