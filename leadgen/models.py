#! .env/bin/python
# *-* coding: utf-8 *-*

from leadgen import db
from sqlalchemy.orm import validates


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000), nullable=False)


class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(50), nullable=False)
    name_title = db.Column(db.String(50), nullable=False)
    name_first = db.Column(db.String(50), nullable=False)
    name_last = db.Column(db.String(50), nullable=False)
    location_street = db.Column(db.String(50), nullable=False)
    location_city = db.Column(db.String(50), nullable=False)
    location_state = db.Column(db.String(50), nullable=False)
    location_postcode = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, nullable=True, default=0)
    login_username = db.Column(db.String(50), nullable=False)
    login_password = db.Column(db.String(50), nullable=False)
    login_salt = db.Column(db.String(50), nullable=False)
    login_md5 = db.Column(db.String(50), nullable=False)
    login_sha1 = db.Column(db.String(255), nullable=False)
    login_sha256 = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False)
    cell_phone = db.Column(db.String(50), nullable=False)
    home_phone = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    nat_id_type = db.Column(db.String(50), nullable=True, default='None')
    nat_id_value = db.Column(db.String(50), nullable=True, default='None')
    img_lg = db.Column(db.String(255), nullable=False)
    img_md = db.Column(db.String(255), nullable=False)
    img_thumb = db.Column(db.String(255), nullable=False)
    seed = db.Column(db.String(50), nullable=False)
    location_type = db.Column(db.String(255), nullable=True)
    location_county = db.Column(db.String(255), nullable=True)
    location_latitude = db.Column(db.Float(), nullable=True)
    location_longitude = db.Column(db.Float(), nullable=True)
    location_country = db.Column(db.String(255), nullable=True)
    location_place_id = db.Column(db.String(255), nullable=True)
    location_geocoded = db.Column(db.Boolean(), nullable=True, default=0)

    def __repr__(self):
        if self.id and self.gender:
            return '{} {} {}'.format(
                self.name_title, self.name_first, self.name_last
            )

    def lead_nat(self):
        if self.nationality:
            return '{}'.format(self.nationality)

    @validates('email')
    def validate_email(self, key, email):
        assert '@' in email
        return email
