from flask import Blueprint, request, jsonify
from be.model.search import Search

bp_search = Blueprint("search", __name__, url_prefix="/search")

@bp_search.route("/books", methods=["GET"])
def search_books():
    keywords = request.args.get("keywords", "")
    store_id = request.args.get("store_id")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    s = Search()
    code, message, results = s.search_books(keywords, store_id, page, page_size)
    return jsonify({"message": message, "results": results}), code
