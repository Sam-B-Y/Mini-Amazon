from flask import Blueprint, request, jsonify

bp = Blueprint('search', __name__)

#TODO implement this, probably require 3 characters to start searching, then match based on *query* (case insensitive) in product name, description, and category

@bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    # Placeholder for search logic
    results = perform_search(query)
    
    return jsonify(results)

def perform_search(query):
    # Implement your search logic here
    # For now, returning a placeholder response
    return {"results": f"Search results for query: {query}"}