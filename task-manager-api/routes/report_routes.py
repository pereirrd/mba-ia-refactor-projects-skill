from flask import Blueprint, jsonify, request

from controllers import category_controller, report_controller

report_bp = Blueprint("reports", __name__)
category_bp = Blueprint("categories", __name__)


@report_bp.route("/reports/summary", methods=["GET"])
def summary_report():
    body, status = report_controller.summary()
    return jsonify(body), status


@report_bp.route("/reports/user/<int:user_id>", methods=["GET"])
def user_report(user_id):
    body, status = report_controller.user_report(user_id)
    return jsonify(body), status


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    body, status = category_controller.list_categories()
    return jsonify(body), status


@category_bp.route("/categories", methods=["POST"])
def create_category():
    body, status = category_controller.create_category(request.get_json())
    return jsonify(body), status


@category_bp.route("/categories/<int:cat_id>", methods=["PUT"])
def update_category(cat_id):
    body, status = category_controller.update_category(cat_id, request.get_json())
    return jsonify(body), status


@category_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    body, status = category_controller.delete_category(cat_id)
    return jsonify(body), status
