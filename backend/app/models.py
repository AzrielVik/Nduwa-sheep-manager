from app import db

class Sheep(db.Model):
    __tablename__ = 'sheep'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    pregnant = db.Column(db.Boolean, default=False)
    medical_records = db.Column(db.Text)
    image = db.Column(db.String(200))
    
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    breed = db.Column(db.String(50))

    # Foreign keys to parent sheep IDs (integer primary keys)
    mother_id = db.Column(db.Integer, db.ForeignKey('sheep.id'), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey('sheep.id'), nullable=True)

    # Relationships to parent sheep objects
    mother = db.relationship(
        'Sheep',
        remote_side=[id],
        foreign_keys=[mother_id],
        backref='mother_children',
        lazy='joined'
    )
    father = db.relationship(
        'Sheep',
        remote_side=[id],
        foreign_keys=[father_id],
        backref='father_children',
        lazy='joined'
    )

    def __repr__(self):
        return f"<Sheep {self.tag_id}>"
