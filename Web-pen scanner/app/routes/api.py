from flask import Blueprint, jsonify, request

from app.services.scan_service import create_scan_record, get_scan_by_id, list_scans, run_scan

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "web-pen-scanner"})


@api_bp.route("/scans", methods=["POST"])
def create_scan():
    payload = request.get_json(silent=True) or {}
    target = (payload.get("target") or payload.get("url") or "").strip()
    if not target:
        return jsonify({"error": "A target URL is required."}), 400

    try:
        scan = create_scan_record(target)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"message": "Scan created.", "scan": scan}), 201


@api_bp.route("/scans", methods=["GET"])
def get_scans():
    return jsonify({"scans": list_scans()})


@api_bp.route("/scans/<int:scan_id>", methods=["GET"])
def get_scan(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        return jsonify({"error": "Scan not found."}), 404
    return jsonify({"scan": scan})


@api_bp.route("/scans/<int:scan_id>/run", methods=["POST"])
def execute_scan(scan_id):
    scan = get_scan_by_id(scan_id)
    if not scan:
        return jsonify({"error": "Scan not found."}), 404

    result = run_scan(scan)
    return jsonify(result)
