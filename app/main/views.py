#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app,flash,request
from .. import db
from ..models import Rule,Node,Property,ExtraConfig
from . import main
from .forms import RuleForm,NodeForm,PropertyForm,ExtraConfigForm
import requests,time,os

@main.route('/rule/index', methods=['GET', 'POST'])
def Index():
    page = request.args.get('page', 1, type=int)
    rule=Rule.query
    pagination = rule.order_by(Rule.description.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    rules = pagination.items
    return render_template('index.html', rules=rules,pagination=pagination)

@main.route('/rule/skeleton', methods=['GET', 'POST'])
def AddNewRule():
    form = RuleForm()
    if form.validate_on_submit():
        description = Rule.query.filter_by(description=form.description.data).first()
        if description is None:
            rule = Rule(description=form.description.data,pattern=form.pattern.data,instance=form.instance.data,
                parserType=form.parserType.data,pageType=form.pageType.data,state=form.state.data)
            db.session.add(rule)
            db.session.commit()
            ruleid=rule.id
        else:
            ruleid=Rule.query.filter_by(description=form.description.data).first().id
        session['RuleId']=ruleid
        return  redirect(url_for('.AddNode', RuleId=ruleid))
    else:
        return render_template('AddNewRule.html',form=form)

@main.route('/rule/node/skeleton/ruleId=<int:RuleId>#AddNode', methods=['GET', 'POST'])
def AddNode(RuleId):
    rules = Rule.query.filter_by(id=RuleId).first()
    nodes=Node.query.filter_by(rule_id=RuleId).all()
    form= NodeForm(RuleId)
    session['RuleId']=RuleId
    if form.validate_on_submit():
        node = Node(label=form.label.data,nodeType=form.nodeType.data,parentNode=form.parentNode.data,
                inputType=form.inputType.data,inputOption=form.inputOption.data,extractorType=form.extractorType.data,
                condition=form.condition.data,value=form.value.data,rule_id=RuleId)
        db.session.add(node)
        db.session.commit()
        nodeid=node.id
        return  redirect(url_for('.AddProperty',NodeId=nodeid))
    else:
        return render_template('AddNode.html',id=RuleId,form=form,rules=rules,nodes=nodes)

@main.route('/rule/prop/skeleton?nodeId=<NodeId>#Property', methods=['GET', 'POST'])
def AddProperty(NodeId):
    form= PropertyForm(NodeId)
    rules =Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes=Node.query.filter_by(id=NodeId).first()
    properties=Property.query.filter_by(node_id=NodeId).all()
    if form.validate_on_submit():
        properties = Property(glue=form.glue.data,label=form.label.data,isRequired=form.isRequired.data,
            isMultiply=form.isMultiply.data,scopeType=form.scopeType.data,resultType=form.resultType.data,
            httpMethod=form.httpMethod.data,referer=form.referer.data,parserType=form.parserType.data,node_id=NodeId)
        db.session.add(properties)
        db.session.commit()
        propertyID=properties.id
        session['NodeId']=NodeId
        return  redirect(url_for('.AddExtraConfig', propertyID=propertyID))
    else:
        return render_template('AddProperty.html',form=form,rules=rules,nodes=nodes,properties=properties)

@main.route('/rule/prop/skeleton?propId=<propertyID>#ExtraConfig', methods=['GET', 'POST'])
def AddExtraConfig(propertyID):
    form= ExtraConfigForm(propertyID)
    rules =Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes=Node.query.filter_by(id=session.get('NodeId')).first()
    properties=Property.query.filter_by(id=propertyID).first()
    extraconfigs=ExtraConfig.query.filter_by(property_id=propertyID).all()
    if form.validate_on_submit():
        extraConfigs = ExtraConfig(inputType=form.inputType.data,inputOption=form.inputOption.data, transformType=form.transformType.data,
            extractorType=form.extractorType.data,condition=form.condition.data,value=form.value.data,
            refExtraConfigId=form.refExtraConfigId.data,property_id=propertyID)
        db.session.add(extraConfigs)
        db.session.commit()
        extraConfigID=extraConfigs.id
        return  redirect(url_for('.AddExtraConfig', propertyID=propertyID))
    else:
        return render_template('AddExtraConfig.html',form=form,rules=rules,nodes=nodes,properties=properties,extraconfigs=extraconfigs)

@main.route('/rule/<RuleID>', methods=['GET', 'POST'])
def Rules(RuleID):
    form = RuleForm()
    rules = Rule.query.get_or_404(RuleID)
    nodes=Node.query.filter_by(rule_id=RuleID).all()
    session['RuleId']=RuleID
    if form.validate_on_submit():
        rules.description=form.description.data
        rules.pattern=form.pattern.data
        rules.parserType=form.parserType.data
        rules.pageType=form.pageType.data
        rules.state=form.state.data
        db.session.add(rules)
        db.session.commit()
        return  redirect(url_for('.Rules',RuleID=RuleID))
    else:
        form.description.data=rules.description
        form.pattern.data=rules.pattern
        form.instance.data=rules.instance
        form.parserType.data=rules.parserType
        form.pageType.data=rules.pageType
        form.state.data=rules.state
        return render_template('Rule.html',form=form,nodes=nodes,RuleID=RuleID)

@main.route('/rule/delete/<RuleID>', methods=['GET', 'POST'])
def DeleteRules(RuleID):
    rules = Rule.query.get_or_404(RuleID)
    if  rules:
        db.session.delete(rules)
        db.session.commit()
        return  redirect(url_for('.Index'))
    else:
        pass

@main.route('/rule/node/<NodeID>#Node', methods=['GET', 'POST'])
def Nodes(NodeID):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    form = NodeForm()
    nodes = Node.query.get_or_404(NodeID)
    properties=Property.query.filter_by(node_id=NodeID).all()
    session['RuleId']=rules.id
    session['NodeID']=nodes.id
    if form.validate_on_submit():
        nodes.label=form.label.data
        nodes.nodeType=form.nodeType.data
        nodes.parentNode=form.parentNode.data
        nodes.inputType=form.inputType.data
        nodes.inputOption=form.inputOption.data
        nodes.extractorType=form.extractorType.data
        nodes.condition=form.condition.data
        nodes.value=form.value.data
        db.session.add(nodes)
        db.session.commit()
        return  redirect(url_for('.Nodes',NodeID=NodeID))
    else:
        form.label.data=nodes.label
        form.nodeType.data=nodes.nodeType
        form.parentNode.data=nodes.parentNode
        form.label.data=nodes.label
        form.inputType.data=nodes.inputType
        form.inputOption.data=nodes.inputOption
        form.extractorType.data=nodes.extractorType
        form.condition.data=nodes.condition
        form.value.data=nodes.value
        return render_template('Node.html',form=form,nodes=nodes,rules=rules,properties=properties)

@main.route('/rule/node/delete/<NodeID>#Node', methods=['GET', 'POST'])
def DeleteNodes(NodeID):
    nodes = Node.query.get_or_404(NodeID)
    if  nodes:
        db.session.delete(nodes)
        db.session.commit()
        return  redirect(url_for('.Rules',RuleID=session.get('RuleId')))
    else:
        pass

@main.route('/rule/property/<PropertyID>', methods=['GET', 'POST'])
def Properties(PropertyID):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes = Node.query.filter_by(id=session.get('NodeID')).first()
    properties = Property.query.get_or_404(PropertyID)
    extraConfigs=ExtraConfig.query.filter_by(property_id=PropertyID).all()
    session['RuleId']=rules.id
    session['NodeID']=nodes.id
    session['PropertyID']=properties.id
    form= PropertyForm()
    if form.validate_on_submit():
        properties.glue=form.glue.data
        properties.label=form.label.data
        properties.isRequired=form.isRequired.data
        properties.isMultiply=form.isMultiply.data
        properties.scopeType=form.scopeType.data
        properties.resultType=form.resultType.data
        properties.httpMethod=form.httpMethod.data
        properties.referer=form.referer.data
        properties.parserType=form.parserType.data
        db.session.add(properties)
        db.session.commit()
        return  redirect(url_for('.Properties', PropertyID=PropertyID))
    else:
        form.glue.data=properties.glue
        form.label.data=properties.label
        form.isRequired.data=properties.isRequired
        form.isMultiply.data=properties.isMultiply
        form.scopeType.data=properties.scopeType
        form.httpMethod.data=properties.httpMethod
        form.referer.data=properties.referer
        form.parserType.data=properties.parserType
        form.resultType.data=properties.resultType
        return render_template('Property.html',form=form,rules=rules,nodes=nodes,properties=properties,extraConfigs=extraConfigs)

@main.route('/rule/property/delete/<PropertyID>', methods=['GET', 'POST'])
def DeleteProperties(PropertyID):
    properties = Property.query.get_or_404(PropertyID)
    if  properties:
        db.session.delete(properties)
        db.session.commit()
        return  redirect(url_for('.Nodes',NodeID=session.get('NodeID')))
    else:
        pass


@main.route('/rule/extraconfig/<ExtraConfigID>', methods=['GET', 'POST'])
def ExtraConfigs(ExtraConfigID):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes = Node.query.filter_by(id=session.get('RuleId')).first()
    properties = Property.query.filter_by(id=session.get('PropertyID')).first()
    extraconfigs=ExtraConfig.query.get_or_404(ExtraConfigID)
    form= ExtraConfigForm()
    if form.validate_on_submit():
        extraconfigs.inputType=form.inputType.data
        extraconfigs.inputOption=form.inputOption.data
        extraconfigs.transformType=form.transformType.data
        extraconfigs.extractorType=form.extractorType.data
        extraconfigs.condition=form.condition.data
        extraconfigs.value=form.value.data
        extraconfigs.refExtraConfigId=form.refExtraConfigId.data
        db.session.add(extraconfigs)
        db.session.commit()
        return  redirect(url_for('.ExtraConfigs', ExtraConfigID=ExtraConfigID))
    else:
        form.inputType.data=extraconfigs.inputType
        form.inputOption.data=extraconfigs.inputOption
        form.transformType.data=extraconfigs.transformType
        form.extractorType.data=extraconfigs.extractorType
        form.condition.data=extraconfigs.condition
        form.value.data=extraconfigs.value
        form.refExtraConfigId.data=extraconfigs.refExtraConfigId
        return render_template('ExtraConfig.html',form=form,rules=rules,nodes=nodes,properties=properties,extraconfigs=extraconfigs)

@main.route('/rule/extraconfig/delete/<ExtraConfigID>', methods=['GET', 'POST'])
def DeleteExtraConfigs(ExtraConfigID):
    extraconfigs=ExtraConfig.query.get_or_404(ExtraConfigID)
    if  extraconfigs:
        db.session.delete(extraconfigs)
        db.session.commit()
        return  redirect(url_for('.Properties',PropertyID=session.get('PropertyID')))
    else:
        pass