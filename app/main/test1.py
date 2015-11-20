#coding=utf-8
from flask import render_template, session, redirect, url_for, current_app,flash,request
from .. import db
from ..models import Rule,Node,Property,ExtraConfig
from . import main
from .forms import RuleForm,NodeForm,PropertyForm,ExtraConfigForm
import requests,time,os
rules = Rule.query.get_or_404(RuleID)
rule={}
rule["rule"]={}
rule.rule["'id"]=rules.id
rule.rule["'pattern"]=rules.pattern
rule.rule["'instance"]=rules.instance
rule.rule["'parserType"]=rules.parserType
rule.rule["'pageType"]=rules.pageType
rule.rule["'state"]=rules.state
print rule