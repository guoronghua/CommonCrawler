#coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import Required
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Rule, Node,Property,ExtraConfig

class RuleForm(Form):
    description=StringField(u'简介', validators=[Required(),])
    pattern = StringField(u'模式', validators=[Required(),])
    instance = StringField(u'实例', validators=[Required(), Regexp('(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', 0,
                                          u'请输入合法网址！')])
    parserType=SelectField(u'解析类型', choices=[(1,'JSOUP'),(2,'XML'),(3,'JSON'),(4,'IMAGE_MAGICK')],coerce=int,default=1)
    pageType=SelectField(u'页面类型', choices=[(1,'List'),(2,'Detail')],coerce=int,default=1)
    state=SelectField(u'状态', choices=[(1,'Enable'),(2,'Disable')],coerce=int,default=1)
    submit = SubmitField(u'提交')
    def __init__(self,*args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)



class NodeForm(Form):
     label=StringField(u'标签名', validators=[Required(),])
     nodeType=SelectField(u'节点类型', choices=[(1,'single'),(2,'mutiple')],coerce=int,default=1)
     parentNode=SelectField(u'父节点',coerce=int,default=1)
     inputType=SelectField(u'输入类型',choices=[(1,'DEFAULT'),(2,'URL'),(3,'REFEREINFO'),(4,'CONTEXTINFO'),(5,'LOCALINFO')],coerce=int,default=1)
     inputOption=StringField(u'输入选项')
     extractorType=SelectField(u'类型', choices=[(1,'HTML'),(2,'REGEX'),(3,'CONST'),(4,'JSON'),(5,'XML'),(6,'TEMPLATE'),(7,'NEXTPAGE'),(8,'UDF'),(9,'XML')],coerce=int,default=1)
     condition=StringField(u'条件' )
     value=StringField(u'选项')
     submit = SubmitField(u'提交')
     def __init__(self, RuleId=None, Node=Node,*args, **kwargs):
        super(NodeForm, self).__init__(*args, **kwargs)
        self.Node=Node
        self.RuleId=RuleId
        self.parentNode.choices = [(1,0)]
        for x in self.Node.query.filter_by(rule_id=self.RuleId).all():
            if x.id:
                self.parentNode.choices.append((x.id,x.id))

class PropertyForm(Form):
     glue=StringField(u'粘合标记')
     label=StringField(u'标签名', validators=[Required(),])
     isRequired=SelectField(u'是否必须',choices=[(1,u'是'),(2,u'否')],coerce=int,default=1)
     isMultiply=SelectField(u'是否多个',choices=[(1,u'是'),(2,u'否')],coerce=int,default=1)
     scopeType=SelectField(u'可见范围',choices=[(1,'LOCAL'),(2,'NODE'),(3,'RULE')],coerce=int,default=1)
     resultType=SelectField(u'导出类型', choices=[(1,'TEXT'),(2,'KEY'),(3,'LINK'),(4,'XML'),(5,'FORMITEM'),(6,'HEADITEM'),(7,'CUSTOMITEM')],coerce=int,id='resultType')
     httpMethod=SelectField(u'请求方式',choices=[(1,'GET'),(2,'POST')],coerce=int,default=1)
     referer=StringField(u'引用页')
     parserType=SelectField(u'解析类型', choices=[(1,'DEFAULT_PARSER_TYPE'),(2,'JSOUP'),(3,'JSON'),(4,'XML')],coerce=int,default=1)
     submit = SubmitField(u'提交')
     def __init__(self, NodeID=None,*args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        self.node_id=NodeID



class ExtraConfigForm(Form):
     inputType=SelectField(u'输入类型',choices=[(1,'DEFAULT'),(2,'URL'),(3,'REFEREINFO'),(4,'CONTEXTINFO'),(5,'LOCALINFO')],coerce=int,default=1)
     inputOption=StringField(u'输入选项')
     transformType=SelectField(u'值转换类型',choices=[(1,'ONE_TO_ONE'),(2,'ONE_TO_MANY'),(3,'MANY_TO_MANY')],coerce=int,default=1)
     extractorType=SelectField(u'类型', choices=[(1,'HTML'),(2,'REGEX'),(3,'CONST'),(4,'JSON'),(5,'XML'),(6,'TEMPLATE'),(7,'NEXTPAGE'),(8,'UDF'),(9,'XML')],coerce=int,default=1)
     condition=StringField(u'条件' )
     value=StringField(u'选项')
     refExtraConfigId=SelectField(u'前置配置项',coerce=int,default=1)
     submit = SubmitField(u'提交')
     def __init__(self, PropertyID=None, ExtraConfig=ExtraConfig,*args, **kwargs):
        super(ExtraConfigForm, self).__init__(*args, **kwargs)
        self.ExtraConfig=ExtraConfig
        self.PropertyID=PropertyID
        self.refExtraConfigId.choices = [(1,0)]
        for x in self.ExtraConfig.query.filter_by(property_id=self.PropertyID).all():
            if x.id:
                self.refExtraConfigId.choices.append((x.id,x.id))