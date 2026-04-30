from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.get("/")
def get_root():
    return jsonify({"status": "ok", "service": "model_answer_backend"})