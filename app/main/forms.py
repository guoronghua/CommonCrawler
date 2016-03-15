#coding=utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField,SelectField,TextAreaField,BooleanField
from wtforms.validators import Required
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Rule, Node,Property,ExtraConfig,Role, User

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class RuleForm(Form):
    description=StringField(u'简介', validators=[Required(),])
    pattern = StringField(u'模式', validators=[Required(),])
    instance = StringField(u'实例', validators=[Required(), Regexp('(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', 0,
                                          u'请输入合法网址！')])
    parserType=SelectField(u'解析类型', choices=[("JSON",'JSON'),("XML",'XML'),("JSOUP",'JSOUP'),("IMAGE_MAGICK",'IMAGE_MAGICK')],default="JSON")
    pageType=SelectField(u'页面类型', choices=[("List",'List'),("Detail",'Detail')],default="List")
    state=SelectField(u'状态', choices=[("ENABLE",'ENABLE'),("DISABLE",'DISABLE')],default="DISABLE")
    submit = SubmitField(u'submit')
    def __init__(self,*args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)



class NodeForm(Form):
     label=StringField(u'标签名', validators=[Required(),])
     nodeType=SelectField(u'节点类型', choices=[('single','single'),('mutiple','mutiple')],default='single')
     parentNode=SelectField(u'父节点',default=0,coerce=int,)
     inputType=SelectField(u'输入类型',choices=[('DEFAULT','DEFAULT'),('URL','URL'),('REFEREINFO','REFEREINFO'),('CONTEXTINFO','CONTEXTINFO'),('LOCALINFO','LOCALINFO')],default='DEFAULT')
     inputOption=StringField(u'输入选项')
     extractorType=SelectField(u'类型', choices=[('HTML','HTML'),('REGEX','REGEX'),('CONST','CONST'),('JSON','JSON'),('XML','XML'),('TEMPLATE','TEMPLATE'),('NEXTPAGE','NEXTPAGE'),('UDF','UDF'),('XML','XML')],default='HTML')
     condition=StringField(u'条件' )
     value=StringField(u'选项')
     submit = SubmitField(u'提交')
     def __init__(self, RuleId=None, Node=Node,*args, **kwargs):
        super(NodeForm, self).__init__(*args, **kwargs)
        self.Node=Node
        self.RuleId=RuleId
        self.parentNode.choices = [(0,0)]
        for x in self.Node.query.filter_by(rule_id=self.RuleId).all():
            if x.id:
                self.parentNode.choices.append((x.id,x.id))

class PropertyForm(Form):
     glue=StringField(u'粘合标记')
     label=StringField(u'标签名', validators=[Required(),])
     isRequired=SelectField(u'是否必须',choices=[(u'是',u'是'),(u'否',u'否')],default=u'否')
     isMultiply=SelectField(u'是否多个',choices=[(u'是',u'是'),(u'否',u'否')],default=u'否')
     scopeType=SelectField(u'可见范围',choices=[('LOCAL','LOCAL'),('NODE','NODE'),('RULE','RULE')],default='LOCAL')
     resultType=SelectField(u'导出类型', choices=[('TEXT','TEXT'),('KEY','KEY'),('LINK','LINK'),('XML','XML'),('FORMITEM','FORMITEM'),('HEADITEM','HEADITEM'),('CUSTOMITEM','CUSTOMITEM')],default='TEXT')
     httpMethod=SelectField(u'请求方式',choices=[('GET','GET'),('POST','POST')],default='GET')
     referer=StringField(u'引用页')
     parserType=SelectField(u'解析类型', choices=[('DEFAULT_PARSER_TYPE','DEFAULT_PARSER_TYPE'),('JSOUP','JSOUP'),('JSON','JSON'),('XML','XML')],default='DEFAULT_PARSER_TYPE')
     submit = SubmitField(u'提交')
     def __init__(self, NodeID=None,*args, **kwargs):
        super(PropertyForm, self).__init__(*args, **kwargs)
        self.node_id=NodeID



class ExtraConfigForm(Form):
     inputType=SelectField(u'输入类型',choices=[('DEFAULT','DEFAULT'),('URL','URL'),('REFEREINFO','REFEREINFO'),('CONTEXTINFO','CONTEXTINFO'),('LOCALINFO','LOCALINFO')],
        default='DEFAULT')
     inputOption=StringField(u'输入选项')
     transformType=SelectField(u'值转换类型',choices=[('ONE_TO_ONE','ONE_TO_ONE'),('ONE_TO_MANY','ONE_TO_MANY'),('MANY_TO_MANY','MANY_TO_MANY')],default='ONE_TO_ONE')
     extractorType=SelectField(u'类型', choices=[('HTML','HTML'),('REGEX','REGEX'),('CONST','CONST'),('JSON','JSON'),('XML','XML'),('TEMPLATE','TEMPLATE'),('NEXTPAGE','NEXTPAGE'),
        ('UDF','UDF'),('XML','XML')],default='HTML')
     condition=StringField(u'条件' )
     value=StringField(u'选项')
     refExtraConfigId=SelectField(u'前置配置项',coerce=int,default=0)
     submit = SubmitField(u'提交')
     def __init__(self, PropertyId=None, ExtraConfig=ExtraConfig,*args, **kwargs):
        super(ExtraConfigForm, self).__init__(*args, **kwargs)
        self.ExtraConfig=ExtraConfig
        self.PropertyId=PropertyId
        self.refExtraConfigId.choices = [(0,0)]
        for x in self.ExtraConfig.query.filter_by(property_id=self.PropertyId).all():
            if x.id:
                self.refExtraConfigId.choices.append((x.id,x.id))
            else:
                pass