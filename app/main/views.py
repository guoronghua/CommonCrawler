#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app,flash,request,send_file,send_from_directory
from .. import db
from ..models import Rule,Node,Property,ExtraConfig
from . import main
from .forms import RuleForm,NodeForm,PropertyForm,ExtraConfigForm
import requests,time,os
import json
from werkzeug.utils import secure_filename

@main.route('/rule/index', methods=['GET', 'POST'])
def Index():
    page = request.args.get('page', 1, type=int)
    rule=Rule.query
    pagination = rule.order_by(Rule.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    rules = pagination.items
    return render_template('index.html', rules=rules,pagination=pagination)

@main.route('/rule/index/', methods=['GET', 'POST'])
def Search():
    searchWord = request.args.get('searchWord')
    rule=Rule.query.filter(Rule.description.like('%' + searchWord + '%'))
    pagination = rule.order_by(Rule.description.desc()).paginate(page=1, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
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
            RuleId=rule.id
        else:
            RuleId=Rule.query.filter_by(description=form.description.data).first().id
        session['RuleId']=RuleId
        return  redirect(url_for('.AddNode', RuleId=RuleId))
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
        PropertyId=properties.id
        session['NodeId']=NodeId
        session['RuleId']=rules.id
        return  redirect(url_for('.AddExtraConfig', PropertyId=PropertyId))
    else:
        return render_template('AddProperty.html',form=form,rules=rules,nodes=nodes,properties=properties)

@main.route('/rule/prop/skeleton?propId=<PropertyId>#ExtraConfig', methods=['GET', 'POST'])
def AddExtraConfig(PropertyId):
    form= ExtraConfigForm(PropertyId)
    rules =Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes=Node.query.filter_by(id=session.get('NodeId')).first()
    properties=Property.query.filter_by(id=PropertyId).first()
    extraconfigs=ExtraConfig.query.filter_by(property_id=PropertyId).all()
    session['NodeId']=nodes.id
    session['RuleId']=rules.id
    session['PropertyId']=properties.id
    if form.validate_on_submit():
        extraConfigs = ExtraConfig(inputType=form.inputType.data,inputOption=form.inputOption.data, transformType=form.transformType.data,
            extractorType=form.extractorType.data,condition=form.condition.data,value=form.value.data,
            refExtraConfigId=form.refExtraConfigId.data,property_id=PropertyId)
        db.session.add(extraConfigs)
        db.session.commit()
        extraConfigID=extraConfigs.id
        return  redirect(url_for('.AddExtraConfig', PropertyId=PropertyId))
    else:
        return render_template('AddExtraConfig.html',form=form,rules=rules,nodes=nodes,properties=properties,extraconfigs=extraconfigs)

@main.route('/rule/<RuleId>', methods=['GET', 'POST'])
def Rules(RuleId):
    form = RuleForm()
    rules = Rule.query.get_or_404(RuleId)
    nodes=Node.query.filter_by(rule_id=RuleId).all()
    session['RuleId']=RuleId
    if form.validate_on_submit():
        rules.description=form.description.data
        rules.pattern=form.pattern.data
        rules.parserType=form.parserType.data
        rules.pageType=form.pageType.data
        rules.state=form.state.data
        db.session.add(rules)
        db.session.commit()
        return  redirect(url_for('.Rules',RuleId=RuleId))
    else:
        form.description.data=rules.description
        form.pattern.data=rules.pattern
        form.instance.data=rules.instance
        form.parserType.data=rules.parserType
        form.pageType.data=rules.pageType
        form.state.data=rules.state
        return render_template('Rule.html',form=form,nodes=nodes,RuleId=RuleId)

@main.route('/rule/delete/<RuleId>', methods=['GET', 'POST'])
def DeleteRules(RuleId):
    rules = Rule.query.get_or_404(RuleId)
    if  rules:
        db.session.delete(rules)
        db.session.commit()
        return  redirect(url_for('.Index'))
    else:
        pass

@main.route('/rule/copy/<RuleId>', methods=['GET', 'POST'])
def CopyRules(RuleId):
    rules = Rule.query.get_or_404(RuleId)
    rule = Rule(description=u"复制于Rule %s"%rules.id,pattern=rules.pattern,instance=rules.instance,
                parserType=rules.parserType,pageType=rules.pageType,state=rules.state)
    db.session.add(rule)
    db.session.commit()
    nodes=Node.query.filter_by(rule_id=RuleId).all()
    if nodes:
        for node in nodes:
            node1 = Node(label=node.label,nodeType=node.nodeType,parentNode=node.parentNode,
            inputType=node.inputType,inputOption=node.inputOption,extractorType=node.extractorType,
            condition=node.condition,value=node.value,rule_id=rule.id)
            db.session.add(node1)
            db.session.commit()
            properties=Property.query.filter_by(node_id=node.id).all()
            if properties:
                for propertie in properties:
                    propertie1= Property(glue=propertie.glue,label=propertie.label,isRequired=propertie.isRequired,
                        isMultiply=propertie.isMultiply,scopeType=propertie.scopeType,resultType=propertie.resultType,
                        httpMethod=propertie.httpMethod,referer=propertie.referer,parserType=propertie.parserType,node_id=node1.id)
                    db.session.add(propertie1)
                    db.session.commit()
                    extraconfigs=ExtraConfig.query.filter_by(property_id=propertie.id).all()
                    if extraconfigs:
                        for extraconfig in extraconfigs:
                            extraConfig1 = ExtraConfig(inputType=extraconfig.inputType,inputOption=extraconfig.inputOption, transformType=extraconfig.transformType,
                                    extractorType=extraconfig.extractorType,condition=extraconfig.condition,value=extraconfig.value,
                                    refExtraConfigId=extraconfig.refExtraConfigId,property_id=propertie1.id)
                            db.session.add(extraConfig1)
                            db.session.commit()
                    else:
                        pass
            else:
                pass
    else:
        pass
    return  redirect(url_for('.Rules',RuleId=rule.id))

@main.route('/rule/node/<NodeId>#Node', methods=['GET', 'POST'])
def Nodes(NodeId):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    form = NodeForm(RuleId=session.get('RuleId'))
    nodes = Node.query.get_or_404(NodeId)
    properties=Property.query.filter_by(node_id=NodeId).all()
    session['RuleId']=rules.id
    session['NodeId']=nodes.id
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
        return  redirect(url_for('.Nodes',NodeId=NodeId))
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

@main.route('/rule/node/delete/<NodeId>#Node', methods=['GET', 'POST'])
def DeleteNodes(NodeId):
    nodes = Node.query.get_or_404(NodeId)
    if  nodes:
        db.session.delete(nodes)
        db.session.commit()
        return  redirect(url_for('.Rules',RuleId=session.get('RuleId')))
    else:
        pass

@main.route('/rule/node/copy', methods=['GET', 'POST'])
def CopyNodes():
    NodeId = request.args.get('nodeId')
    nodes = Node.query.get_or_404(NodeId)
    node1 = Node(label=nodes.label,nodeType=nodes.nodeType,parentNode=nodes.parentNode,
                inputType=nodes.inputType,inputOption=nodes.inputOption,extractorType=nodes.extractorType,
                condition=nodes.condition,value=nodes.value,rule_id=session.get('RuleId'))
    db.session.add(node1)
    db.session.commit()
    properties=Property.query.filter_by(node_id=nodes.id).all()
    if properties:
        for propertie in properties:
            propertie1= Property(glue=propertie.glue,label=propertie.label,isRequired=propertie.isRequired,
                isMultiply=propertie.isMultiply,scopeType=propertie.scopeType,resultType=propertie.resultType,
                httpMethod=propertie.httpMethod,referer=propertie.referer,parserType=propertie.parserType,node_id=node1.id)
            db.session.add(propertie1)
            db.session.commit()
            extraconfigs=ExtraConfig.query.filter_by(property_id=propertie.id).all()
            if extraconfigs:
                for extraconfig in extraconfigs:
                    extraConfig1 = ExtraConfig(inputType=extraconfig.inputType,inputOption=extraconfig.inputOption, transformType=extraconfig.transformType,
                            extractorType=extraconfig.extractorType,condition=extraconfig.condition,value=extraconfig.value,
                            refExtraConfigId=extraconfig.refExtraConfigId,property_id=propertie1.id)
                    db.session.add(extraConfig1)
                    db.session.commit()
            else:
                pass
    else:
        pass
    return  redirect(url_for('.Rules',RuleId=session.get('RuleId')))


@main.route('/rule/property/<PropertyId>', methods=['GET', 'POST'])
def Properties(PropertyId):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes = Node.query.filter_by(id=session.get('NodeId')).first()
    properties = Property.query.get_or_404(PropertyId)
    extraConfigs=ExtraConfig.query.filter_by(property_id=PropertyId).all()
    session['RuleId']=rules.id
    session['NodeId']=nodes.id
    session['PropertyId']=properties.id
    form= PropertyForm(NodeId=session.get('NodeId'))
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
        return  redirect(url_for('.Properties', PropertyId=PropertyId))
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

@main.route('/rule/property/delete/<PropertyId>', methods=['GET', 'POST'])
def DeleteProperties(PropertyId):
    properties = Property.query.get_or_404(PropertyId)
    if  properties:
        db.session.delete(properties)
        db.session.commit()
        return  redirect(url_for('.Nodes',NodeId=session.get('NodeId')))
    else:
        pass

@main.route('/rule/property/copy', methods=['GET', 'POST'])
def CopyProperties():
    PropertyId = request.args.get('propertyId')
    properties = Property.query.get_or_404(PropertyId)
    propertie1= Property(glue=properties.glue,label=properties.label,isRequired=properties.isRequired,
            isMultiply=properties.isMultiply,scopeType=properties.scopeType,resultType=properties.resultType,
            httpMethod=properties.httpMethod,referer=properties.referer,parserType=properties.parserType,node_id=session.get('NodeId'))
    db.session.add(propertie1)
    db.session.commit()
    extraconfigs=ExtraConfig.query.filter_by(property_id=properties.id).all()
    if extraconfigs:
        for extraconfig in extraconfigs:
            extraConfig1 = ExtraConfig(inputType=extraconfig.inputType,inputOption=extraconfig.inputOption, transformType=extraconfig.transformType,
                    extractorType=extraconfig.extractorType,condition=extraconfig.condition,value=extraconfig.value,
                    refExtraConfigId=extraconfig.refExtraConfigId,property_id=propertie1.id)
            db.session.add(extraConfig1)
            db.session.commit()
    else:
        pass
    return  redirect(url_for('.Nodes',NodeId=session.get('NodeId')))

@main.route('/rule/extraconfig/<ExtraConfigId>', methods=['GET', 'POST'])
def ExtraConfigs(ExtraConfigId):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes = Node.query.filter_by(id=session.get('NodeId')).first()
    properties = Property.query.filter_by(id=session.get('PropertyId')).first()
    extraconfigs=ExtraConfig.query.get_or_404(ExtraConfigId)
    form= ExtraConfigForm(PropertyId=session.get("PropertyId"))
    session['RuleId']=rules.id
    session['NodeId']=nodes.id
    session['PropertyId']=properties.id
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
        return  redirect(url_for('.ExtraConfigs', ExtraConfigId=ExtraConfigId))
    else:
        form.inputType.data=extraconfigs.inputType
        form.inputOption.data=extraconfigs.inputOption
        form.transformType.data=extraconfigs.transformType
        form.extractorType.data=extraconfigs.extractorType
        form.condition.data=extraconfigs.condition
        form.value.data=extraconfigs.value
        form.refExtraConfigId.data=extraconfigs.refExtraConfigId
        return render_template('ExtraConfig.html',form=form,rules=rules,nodes=nodes,properties=properties,extraconfigs=extraconfigs)

@main.route('/rule/extraconfig/delete/<ExtraConfigId>', methods=['GET', 'POST'])
def DeleteExtraConfigs(ExtraConfigId):
    extraconfigs=ExtraConfig.query.get_or_404(ExtraConfigId)
    if  extraconfigs:
        db.session.delete(extraconfigs)
        db.session.commit()
        return  redirect(url_for('.Properties',PropertyId=session.get('PropertyId')))
    else:
        pass


@main.route('/rule/export/<RuleId>', methods=['GET', 'POST'])
def ExportRules(RuleId):
    RuleId=RuleId
    DOWNLOAD_FOLDER = os.getcwd()+"/app/static/Downloads"
    rules = Rule.query.get_or_404(RuleId)
    ruleDic={}
    ruleExport={}
    ruleDic["'id"]=rules.id
    ruleDic["'pattern"]=rules.pattern
    ruleDic["'instance"]=rules.instance
    ruleDic["'parserType"]=rules.parserType
    ruleDic["'pageType"]=rules.pageType
    ruleDic["'state"]=rules.state
    ruleDic["'timestamp"]=str(rules.timestamp)
    ruleExport["rule'"]=ruleDic
    """查询父节点"""
    topNodeTrees=[]
    def ChildNodeTree(node,subnode=False):
        topNodeTreesDic={}
        nodeDic={}
        extraConfigDic={}
        nodeDic["id"]=node.id
        nodeDic["label"]=node.label
        nodeDic["nodeType"]=node.nodeType
        nodeDic["parentNode"]=node.parentNode
        nodeDic["ruleId"]=RuleId
        extraConfigDic["inputType"]=node.inputType
        extraConfigDic["inputOption"]=node.inputOption
        extraConfigDic["condition"]=node.condition
        extraConfigDic["value"]=node.value
        extraConfigDic["extractorType"]=node.extractorType
        topNodeTreesDic["node"]=nodeDic
        topNodeTreesDic["extraConfig"]=extraConfigDic
        propTrees=[]
        properties=Property.query.filter_by(node_id=node.id).all()
        for propertie in properties:
            propTreesDic={}
            propDic={}
            propDic["id"]=propertie.id
            propDic["glue"]=propertie.glue
            propDic["label"]=propertie.label
            propDic["isRequired"]=propertie.isRequired
            propDic["isMultiply"]=propertie.isMultiply
            propDic["scopeType"]=propertie.scopeType
            propDic["resultType"]=propertie.resultType
            propDic["httpMethod"]=propertie.httpMethod
            propDic["referer"]=propertie.referer
            propDic["nodeId"]=node.id
            propTreesDic["prop"]=propDic
            extraConfigs=ExtraConfig.query.filter_by(property_id=propertie.id).all()
            ExtraConfigs=[]
            for extraConfig in extraConfigs:
                ExtraConfigsDic={}
                ExtraConfigsDic["id"]=extraConfig.id
                ExtraConfigsDic["inputType"]=extraConfig.inputType
                ExtraConfigsDic["inputOption"]=extraConfig.inputOption
                ExtraConfigsDic["condition"]=extraConfig.condition
                ExtraConfigsDic["value"]=extraConfig.value
                ExtraConfigsDic["extractorType"]=extraConfig.extractorType
                ExtraConfigsDic["transformType"]=extraConfig.transformType
                ExtraConfigs.append(ExtraConfigsDic)
                propTreesDic["extraConfigs"]=ExtraConfigs
            propTrees.append(propTreesDic)
        topNodeTreesDic["propTrees"]=propTrees
        if not subnode:
            topNodeTrees.append(topNodeTreesDic)
            ruleExport["topNodeTrees"]=topNodeTrees
        subnodes=Node.query.filter_by(parentNode=node.id).all()
        topNodeTreesDic["childNodeTrees"]=[ChildNodeTree(subnode,subnode=True) for subnode in subnodes if subnodes]
        return topNodeTreesDic

    nodes=Node.query.filter_by(rule_id=RuleId,parentNode=0).all()
    for node in nodes:
        ChildNodeTree(node)
    ruleExport=json.dumps(ruleExport,check_circular=False)
    f= open(DOWNLOAD_FOLDER+"/rule.text",'w')
    f.writelines(ruleExport)
    f.close()
    return send_file(DOWNLOAD_FOLDER+"/rule.text", as_attachment=True)


@main.route('/rule/upload', methods=['GET', 'POST'])
def Upload():
    UPLOAD_FOLDER = os.getcwd()+"/app/static/Uploads"
    filenames = []
    if request.method == 'GET':
        return render_template('import.html')
    elif request.method == 'POST':
        # f = request.files['files']
        uploaded_files = request.files.getlist("file[]")
        for file in uploaded_files:
            if file:
                fname = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fname))
        return '上传成功!!'



