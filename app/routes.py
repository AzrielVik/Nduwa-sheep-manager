from flask import request, jsonify, url_for
from werkzeug.utils import secure_filename
import os
from app.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from app import app, db
from app.models import Sheep
from sqlalchemy.exc import IntegrityError


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper to resolve parent tag_id strings to actual DB IDs
def resolve_parent_id(tag_id):
    if not tag_id:
        return None
    parent = Sheep.query.filter_by(tag_id=tag_id).first()
    return parent.id if parent else None


# Add sheep
@app.route('/sheep', methods=['POST'])
def add_sheep():
    data = request.form
    file = request.files.get('image')

    # Check required fields
    if not data.get("tag_id") or not data.get("gender"):
        return jsonify({"error": "Missing required fields (tag_id, gender)"}), 400

    # Validate image file if present
    if file and not allowed_file(file.filename):
        return jsonify({"error": "Invalid image format"}), 400

    filename = secure_filename(file.filename) if file else None
    if filename:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    pregnant_raw = data.get("pregnant", "false")
    pregnant = pregnant_raw.lower() == "true"

    mother_id = resolve_parent_id(data.get("mother_id"))
    father_id = resolve_parent_id(data.get("father_id"))

    new_sheep = Sheep(
        tag_id=data["tag_id"],
        gender=data["gender"],
        pregnant=pregnant,
        medical_records=data.get("medical_records", ""),
        image=filename,
        age=data.get("age"),
        weight=data.get("weight"),
        breed=data.get("breed"),
        mother_id=mother_id,
        father_id=father_id
    )

    try:
        db.session.add(new_sheep)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "UNIQUE constraint failed: sheep.tag_id" in str(e):
            return jsonify({"error": "Tag ID already exists. Please use a unique Tag ID."}), 400
        else:
            return jsonify({"error": "Database error occurred."}), 500

    return jsonify({"message": "Sheep added successfully", "image": filename}), 201


# Get all sheep
@app.route('/sheep', methods=['GET'])
def get_sheep():
    sheep_list = Sheep.query.all()
    return jsonify([{
        'id': sheep.id,
        'tag_id': sheep.tag_id,
        'gender': sheep.gender,
        'pregnant': sheep.pregnant,
        'medical_records': sheep.medical_records,
        'image': sheep.image,
        'age': sheep.age,
        'weight': sheep.weight,
        'breed': sheep.breed,
        'mother_id': sheep.mother.tag_id if sheep.mother else None,
        'father_id': sheep.father.tag_id if sheep.father else None
    } for sheep in sheep_list])


# Get sheep by ID
@app.route('/sheep/<int:sheep_id>', methods=['GET'])
def get_sheep_by_id(sheep_id):
    sheep = Sheep.query.get_or_404(sheep_id)

    image_url = url_for('uploaded_file', filename=sheep.image, _external=True) if sheep.image else None

    return jsonify({
        "status": "success",
        "data": {
            "id": sheep.id,
            "tag_id": sheep.tag_id,
            "gender": sheep.gender,
            "pregnant": sheep.pregnant,
            "medical_records": sheep.medical_records,
            "image_url": image_url,
            "age": sheep.age,
            "weight": sheep.weight,
            "breed": sheep.breed,
            "mother_id": sheep.mother.tag_id if sheep.mother else None,
            "father_id": sheep.father.tag_id if sheep.father else None
        }
    })


# Get family (sheep + its lambs/children)
@app.route('/sheep/<int:sheep_id>/family', methods=['GET'])
def get_sheep_family(sheep_id):
    sheep = Sheep.query.get_or_404(sheep_id)

    # Lambs where this sheep is mother or father
    lambs = sheep.mother_children + sheep.father_children

    lambs_data = [{
        'id': lamb.id,
        'tag_id': lamb.tag_id,
        'gender': lamb.gender,
    } for lamb in lambs]

    return jsonify({
        'parent': {
            'id': sheep.id,
            'tag_id': sheep.tag_id,
            'gender': sheep.gender,
            'pregnant': sheep.pregnant,
            'medical_records': sheep.medical_records,
            'age': sheep.age,
            'weight': sheep.weight,
            'breed': sheep.breed,
        },
        'lambs': lambs_data
    })


# Update sheep
@app.route('/sheep/<int:sheep_id>', methods=['PUT'])
def update_sheep(sheep_id):
    sheep = Sheep.query.get_or_404(sheep_id)
    data = request.get_json()

    sheep.tag_id = data.get('tag_id', sheep.tag_id)
    sheep.gender = data.get('gender', sheep.gender)
    sheep.pregnant = data.get('pregnant', sheep.pregnant)
    sheep.medical_records = data.get('medical_records', sheep.medical_records)
    sheep.age = data.get('age', sheep.age)
    sheep.weight = data.get('weight', sheep.weight)
    sheep.breed = data.get('breed', sheep.breed)

    # Resolve mother and father tag_ids to IDs if provided
    mother_tag = data.get('mother_id')
    father_tag = data.get('father_id')

    if mother_tag is not None:
        sheep.mother_id = resolve_parent_id(mother_tag)
    if father_tag is not None:
        sheep.father_id = resolve_parent_id(father_tag)

    db.session.commit()
    return jsonify({'message': 'Sheep updated successfully'})


# Delete sheep
@app.route('/sheep/<int:sheep_id>', methods=['DELETE'])
def delete_sheep(sheep_id):
    sheep = Sheep.query.get_or_404(sheep_id)
    db.session.delete(sheep)
    db.session.commit()
    return jsonify({'message': 'Sheep deleted successfully'})


# 404 Error handler
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({"error": "Sheep not found"}), 404
