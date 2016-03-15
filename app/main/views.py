#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app,flash,request,send_file,send_from_directory
from .. import db
from ..models import Rule,Node,Property,ExtraConfig,Role,User
from . import main
from .forms import RuleForm,NodeForm,PropertyForm,ExtraConfigForm,NameForm,EditProfileForm,EditProfileAdminForm
import requests,time,os,json,urllib
from werkzeug.utils import secure_filename
from ..decorators import admin_required, permission_required
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/rule/index', methods=['GET', 'POST'])
def Index():
    page = request.args.get('page', 1, type=int)
    rule=Rule.query
    pagination = rule.order_by(Rule.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    rules = pagination.items
    return render_template('index.html', rules=rules,pagination=pagination)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)



@main.route('/rule/index/', methods=['GET', 'POST'])
def Search():
    searchWord = request.args.get('searchWord')
    rule=Rule.query.filter(Rule.description.like('%' + searchWord + '%'))
    pagination = rule.order_by(Rule.description.desc()).paginate(page=1, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    rules = pagination.items
    return render_template('index.html', rules=rules,pagination=pagination)

@main.route('/rule/skeleton#AddRule', methods=['GET', 'POST'])
def AddNewRule():
    form = RuleForm()
    if form.validate_on_submit():
        description = Rule.query.filter_by(description=form.description.data).first()
        if description is None:
            proto, rest = urllib.splittype(form.instance.data)
            res, rest = urllib.splithost(rest)
            siteName= "Unknow" if not res else res
            rule = Rule(description=form.description.data,pattern=form.pattern.data,instance=form.instance.data,siteName=siteName.upper(),
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

@main.route('/rule/<RuleId>#Rule', methods=['GET', 'POST'])
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
        return  redirect(url_for('.UpdateRules',RuleId=RuleId,updateState='success'))
    else:
        form.description.data=rules.description
        form.pattern.data=rules.pattern
        form.instance.data=rules.instance
        form.parserType.data=rules.parserType
        form.pageType.data=rules.pageType
        form.state.data=rules.state
        return render_template('Rule.html',form=form,rules=rules,nodes=nodes,RuleId=RuleId)

@main.route('/rule/<RuleId>/updateState=<updateState>#Rule', methods=['GET', 'POST'])
def UpdateRules(RuleId,updateState):
    form = RuleForm()
    rules = Rule.query.get_or_404(RuleId)
    nodes=Node.query.filter_by(rule_id=RuleId).all()
    session['RuleId']=RuleId
    form.description.data=rules.description
    form.pattern.data=rules.pattern
    form.instance.data=rules.instance
    form.parserType.data=rules.parserType
    form.pageType.data=rules.pageType
    form.state.data=rules.state
    return render_template('Rule.html',form=form,rules=rules,nodes=nodes,RuleId=RuleId,updateState=updateState)

@main.route('/rule/delete/<RuleId>#Rule', methods=['GET', 'POST'])
def DeleteRules(RuleId):
    rules = Rule.query.get_or_404(RuleId)
    if  rules:
        db.session.delete(rules)
        db.session.commit()
        return  redirect(url_for('.Index'))
    else:
        pass

@main.route('/rule/copy/<RuleId>#Rule', methods=['GET', 'POST'])
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

@main.route('/rule/export/<RuleId>#Rule', methods=['GET', 'POST'])
def ExportRules(RuleId):
    RuleId=RuleId
    DOWNLOAD_FOLDER = os.getcwd()+"/app/static/Downloads"
    rules = Rule.query.get_or_404(RuleId)
    ruleDic={}
    ruleExport={}
    ruleDic["id"]=rules.id
    ruleDic["pattern"]=rules.pattern
    ruleDic["instance"]=rules.instance
    ruleDic["parserType"]=rules.parserType
    ruleDic["pageType"]=rules.pageType
    ruleDic["state"]=rules.state
    ruleDic["description"]=rules.description
    ruleDic["timestamp"]=str(rules.timestamp)
    ruleExport["rule"]=ruleDic
    """查询父节点"""
    topNodeTrees=[]
    IsorNot={u"是":True,u"否":False}
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
        extraConfigDic["cond"]=node.condition
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
            propDic["isRequired"]=IsorNot[propertie.isRequired]
            propDic["isMultiply"]=IsorNot[propertie.isMultiply]
            propDic["scopeType"]=propertie.scopeType
            propDic["resultType"]=propertie.resultType
            propDic["parserType"]=propertie.parserType
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
                ExtraConfigsDic["cond"]=extraConfig.condition
                ExtraConfigsDic["value"]=extraConfig.value
                ExtraConfigsDic["extractorType"]=extraConfig.extractorType
                ExtraConfigsDic["transformType"]=extraConfig.transformType
                ExtraConfigsDic["refExtraConfigId"]=extraConfig.refExtraConfigId
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


@main.route('/rule/upload#Rule', methods=['GET', 'POST'])
def UploadRules():
    UPLOAD_FOLDER = os.getcwd()+"/app/static/Uploads"
    filenames = []
    if request.method == 'GET':
        return render_template('import.html')
    elif request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        RuleID=[]
        for file in uploaded_files:
            if file:
                fname = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, fname))
                jsonData=json.load(open((UPLOAD_FOLDER+'/'+fname), 'r'))
                ruleData=jsonData['rule']
                RuleID.append(ruleData["id"])
                proto, rest = urllib.splittype(ruleData['instance'])
                res, rest = urllib.splithost(rest)
                siteName= "Unknow" if not res else res
                rule = Rule(description=ruleData['description'],pattern=ruleData['pattern'],instance=ruleData['instance'],
                parserType=ruleData['parserType'],pageType=ruleData['pageType'],state='DISABLE',siteName=siteName.upper())
                db.session.add(rule)
                db.session.commit()
                IsorNot={1:"是",0:"否"}
                def Insert(x):
                    node=x['node']
                    extraConfig=x['extraConfig']
                    propTrees=x['propTrees']
                    childNodeTrees=x['childNodeTrees']
                    nodes= Node(label=node['label'],nodeType=node['nodeType'],parentNode=node['parentNode'],
                        inputType=extraConfig['inputType'],inputOption=extraConfig['inputOption'],extractorType=extraConfig['extractorType'],
                        condition=extraConfig['cond'],value=extraConfig['value'],rule_id=rule.id)
                    db.session.add(nodes)
                    db.session.commit()
                    for y in propTrees:
                        if y:
                            prop=y['prop']
                            extraConfigs=y['extraConfigs']
                            propertie= Property(glue=prop['glue'],label=prop['label'],isRequired=IsorNot[prop['isRequired']],
                            isMultiply=IsorNot[prop['isMultiply']],scopeType=prop['scopeType'],resultType=prop['resultType'],
                            httpMethod=prop['httpMethod'],referer=prop['referer'],parserType=prop['parserType'],node_id=nodes.id)
                            db.session.add(propertie)
                            db.session.commit()
                            TopextraConfigs={}
                            for z in extraConfigs:
                                if  z['refExtraConfigId']==0:
                                    extraConfig = ExtraConfig(inputType=z['inputType'],inputOption=z['inputOption'], transformType=z['transformType'],
                                            extractorType=z['extractorType'],condition=z['cond'],value=z['value'],
                                            refExtraConfigId=0,property_id=propertie.id)
                                    db.session.add(extraConfig)
                                    db.session.commit()
                                    TopextraConfigs[z['id']]=extraConfig.id

                            for z in extraConfigs:
                                if  z['refExtraConfigId']!=0:
                                    extraConfig = ExtraConfig(inputType=z['inputType'],inputOption=z['inputOption'], transformType=z['transformType'],
                                            extractorType=z['extractorType'],condition=z['cond'],value=z['value'],
                                            refExtraConfigId=TopextraConfigs[z['refExtraConfigId']],property_id=propertie.id)
                                    db.session.add(extraConfig)
                                    db.session.commit()
                                    TopextraConfigs[z['id']]=extraConfig.id
                    for w in childNodeTrees:
                        if w:
                            Insert(w)
                    return "success!!"

                topNodeTrees=jsonData['topNodeTrees']
                for x  in topNodeTrees:
                    if x:
                        Insert(x)
        flash(u"导入成功！导入的RuleID为:"+','.join(map(str,RuleID)))
        return render_template('import.html')


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
        return  redirect(url_for('.UpdateNodes',NodeId=NodeId,updateState='success'))
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

@main.route('/rule/node/delete/<NodeId>/updateState=<updateState>#Node', methods=['GET', 'POST'])
def UpdateNodes(NodeId,updateState):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    form = NodeForm(RuleId=session.get('RuleId'))
    nodes = Node.query.get_or_404(NodeId)
    properties=Property.query.filter_by(node_id=NodeId).all()
    session['RuleId']=rules.id
    session['NodeId']=nodes.id
    form.label.data=nodes.label
    form.nodeType.data=nodes.nodeType
    form.parentNode.data=nodes.parentNode
    form.label.data=nodes.label
    form.inputType.data=nodes.inputType
    form.inputOption.data=nodes.inputOption
    form.extractorType.data=nodes.extractorType
    form.condition.data=nodes.condition
    form.value.data=nodes.value
    return render_template('Node.html',form=form,nodes=nodes,rules=rules,properties=properties,updateState=updateState)

@main.route('/rule/node/delete/<NodeId>#Node', methods=['GET', 'POST'])
def DeleteNodes(NodeId):
    nodes = Node.query.get_or_404(NodeId)
    if  nodes:
        db.session.delete(nodes)
        db.session.commit()
        return  redirect(url_for('.Rules',RuleId=session.get('RuleId')))
    else:
        pass

@main.route('/rule/node/copy#Node', methods=['GET', 'POST'])
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


@main.route('/rule/property/<PropertyId>#Property', methods=['GET', 'POST'])
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
        return  redirect(url_for('.UpdateProperties', PropertyId=PropertyId,updateState='success'))
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

@main.route('/rule/property/update/<PropertyId>/updateState=<updateState>#Property', methods=['GET', 'POST'])
def UpdateProperties(PropertyId,updateState):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes = Node.query.filter_by(id=session.get('NodeId')).first()
    properties = Property.query.get_or_404(PropertyId)
    extraConfigs=ExtraConfig.query.filter_by(property_id=PropertyId).all()
    session['RuleId']=rules.id
    session['NodeId']=nodes.id
    session['PropertyId']=properties.id
    form= PropertyForm(NodeId=session.get('NodeId'))
    form.glue.data=properties.glue
    form.label.data=properties.label
    form.isRequired.data=properties.isRequired
    form.isMultiply.data=properties.isMultiply
    form.scopeType.data=properties.scopeType
    form.httpMethod.data=properties.httpMethod
    form.referer.data=properties.referer
    form.parserType.data=properties.parserType
    form.resultType.data=properties.resultType
    return render_template('Property.html',form=form,rules=rules,nodes=nodes,properties=properties,extraConfigs=extraConfigs,updateState=updateState)


@main.route('/rule/property/delete/<PropertyId>#Property', methods=['GET', 'POST'])
def DeleteProperties(PropertyId):
    properties = Property.query.get_or_404(PropertyId)
    if  properties:
        db.session.delete(properties)
        db.session.commit()
        return  redirect(url_for('.Nodes',NodeId=session.get('NodeId')))
    else:
        pass


@main.route('/rule/property/copy#Property', methods=['GET', 'POST'])
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


@main.route('/rule/extraconfig/<ExtraConfigId>#ExtraConfig', methods=['GET', 'POST'])
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
        return  redirect(url_for('.UpdateExtraConfigs', ExtraConfigId=ExtraConfigId,updateState='success'))
    else:
        form.inputType.data=extraconfigs.inputType
        form.inputOption.data=extraconfigs.inputOption
        form.transformType.data=extraconfigs.transformType
        form.extractorType.data=extraconfigs.extractorType
        form.condition.data=extraconfigs.condition
        form.value.data=extraconfigs.value
        form.refExtraConfigId.data=extraconfigs.refExtraConfigId
        return render_template('ExtraConfig.html',form=form,rules=rules,nodes=nodes,properties=properties,extraconfigs=extraconfigs)

@main.route('/rule/extraconfig/<ExtraConfigId>/updateState=<updateState>#ExtraConfig', methods=['GET', 'POST'])
def UpdateExtraConfigs(ExtraConfigId,updateState):
    rules = Rule.query.filter_by(id=session.get('RuleId')).first()
    nodes = Node.query.filter_by(id=session.get('NodeId')).first()
    properties = Property.query.filter_by(id=session.get('PropertyId')).first()
    extraconfigs=ExtraConfig.query.get_or_404(ExtraConfigId)
    form= ExtraConfigForm(PropertyId=session.get("PropertyId"))
    session['RuleId']=rules.id
    session['NodeId']=nodes.id
    session['PropertyId']=properties.id
    form.inputType.data=extraconfigs.inputType
    form.inputOption.data=extraconfigs.inputOption
    form.transformType.data=extraconfigs.transformType
    form.extractorType.data=extraconfigs.extractorType
    form.condition.data=extraconfigs.condition
    form.value.data=extraconfigs.value
    form.refExtraConfigId.data=extraconfigs.refExtraConfigId
    return render_template('ExtraConfig.html',form=form,rules=rules,nodes=nodes,properties=properties,extraconfigs=extraconfigs,updateState=updateState)


@main.route('/rule/extraconfig/delete/<ExtraConfigId>#ExtraConfig', methods=['GET', 'POST'])
def DeleteExtraConfigs(ExtraConfigId):
    extraconfigs=ExtraConfig.query.get_or_404(ExtraConfigId)
    if  extraconfigs:
        db.session.delete(extraconfigs)
        db.session.commit()
        return  redirect(url_for('.Properties',PropertyId=session.get('PropertyId')))
    else:
        pass



@main.route('/rule/<RuleId>#RuleTest', methods=['GET', 'POST'])
def RulesTest(RuleId):
    rules = Rule.query.get_or_404(RuleId)
    session['RuleId']=RuleId
    return render_template('RuleTest.html',form=form,rules=rules)

@main.route('/rule/<RuleId>/test', methods=['GET', 'POST'])
def TestResult(RuleId):
    rules = Rule.query.get_or_404(RuleId)
    nodes=Node.query.filter_by(rule_id=RuleId).all()
    properties=[Property.query.filter_by(rule_id=node.id).all() for node in nodes]
    session['RuleId']=RuleId
    return render_template('RuleTest.html',form=form,rules=rules)