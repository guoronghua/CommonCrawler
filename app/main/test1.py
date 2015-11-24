#coding=utf-8
from .test1 import ChildNodeTree
def ChildNodeTree(node):
    nodeDic={}
    extraConfigDic={}
    topNodeTreesDic={}
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
    topNodeTrees.append(topNodeTreesDic)
    ruleExport["topNodeTrees"]=topNodeTrees
    return ruleExport