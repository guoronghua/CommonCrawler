from . import db
from datetime import datetime

class Rule(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer,primary_key=True)
    description=db.Column(db.Text())
    pattern = db.Column(db.String(64))
    instance = db.Column(db.String(64))
    parserType=db.Column(db.String(64))
    pageType=db.Column(db.String(64))
    state=db.Column(db.String(64))
    siteName=db.Column(db.String(64))
    nodes=db.relationship('Node', backref='rule', lazy='dynamic',cascade="all, delete-orphan")
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer,primary_key=True)
    label= db.Column(db.String(64))
    nodeType= db.Column(db.String(64))
    parentNode=db.Column(db.Integer)
    inputType=db.Column(db.String(64))
    inputOption=db.Column(db.String(64))
    extractorType=db.Column(db.String(64))
    condition=db.Column(db.String(64))
    value=db.Column(db.String(64))
    rule_id=db.Column(db.Integer, db.ForeignKey('rules.id'))
    properties=db.relationship('Property', backref='property', lazy='dynamic',cascade="all, delete-orphan")

class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer,primary_key=True)
    glue= db.Column(db.String(64))
    label= db.Column(db.String(64))
    isRequired=db.Column(db.String(64))
    isMultiply=db.Column(db.String(64))
    scopeType=db.Column(db.String(64))
    resultType=db.Column(db.String(64))
    httpMethod=db.Column(db.String(64))
    referer=db.Column(db.String(64))
    parserType=db.Column(db.String(64))
    node_id=db.Column(db.Integer, db.ForeignKey('nodes.id'))
    extraConfigs=db.relationship('ExtraConfig', backref='extraConfig', lazy='dynamic',cascade="all, delete-orphan")

class ExtraConfig(db.Model):
    __tablename__ = 'extraConfigs'
    id = db.Column(db.Integer,primary_key=True)
    inputType= db.Column(db.String(64))
    inputOption= db.Column(db.String(64))
    transformType=db.Column(db.String(64))
    extractorType=db.Column(db.String(64))
    condition=db.Column(db.String(64))
    value=db.Column(db.String(64))
    refExtraConfigId=db.Column(db.Integer)
    property_id=db.Column(db.Integer, db.ForeignKey('properties.id'))

