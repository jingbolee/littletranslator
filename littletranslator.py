#coding:utf-8
__author__='Jerome'

from flask import Flask, request, make_response
import hashlib,time
import xml.dom.minidom
import requests
import sys 
reload(sys)
sys.setdefaultencoding='utf-8'

app = Flask(__name__)

app.debug = True


@app.route('/', methods = ['GET', 'POST'] )
def wechat_auth():
    if request.method == 'GET':
        return checkSignature(request)
    elif request.method=='POST':
        return responseMsg(request)
    else:
        return None

def checkSignature(request):
      token = 'yourToken'
      signature = request.args.get('signature','')
      timestamp = request.args.get('timestamp','')
      nonce = request.args.get('nonce','')
      echostr = request.args.get('echostr','')
      tmpStr = ''.join(sorted([timestamp, nonce, token]))
      if  hashlib.sha1(tmpStr).hexdigest() == signature :  
          return make_response(echostr)

def responseMsg(request):
    dom=xml.dom.minidom.parseString(request.data)  #加载文件使用parse，加载数据使用parseString
    root=dom.documentElement #需要dom对象
    toUserName=root.getElementsByTagName('ToUserName')[0].firstChild.data
    fromUserName=root.getElementsByTagName('FromUserName')[0].firstChild.data
    if root.getElementsByTagName('Content'):
        content=root.getElementsByTagName('Content')[0].firstChild.data.strip()
    elif root.getElementsByTagName('Recognition'):
        content=root.getElementsByTagName('Recognition')[0].firstChild.data.strip()
    else:
        content=u'无法识别的内容'
    reply='''<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>'''
    msgType='text'
    contentStr=youdaoXML(content)
    if content:
        response=make_response(reply %(fromUserName,toUserName,str(int(time.time())),msgType,contentStr))
        response.content_type='application/xml'
        return response
        
def youdaoXML(content):    
    payload={'keyfrom':'youdao_keyform','key':'youdao_key','type':'data','doctype':'json','version':'1.1','q':''}
    payload['q']=content
    url='http://fanyi.youdao.com/openapi.do'
    r=requests.get(url,params=payload)
    res=r.json()
    if res['errorCode']==20:
        return '要翻译的文本过长\n'
    elif res['errorCode']==30:
        return '无法进行有效的翻译\n'
    elif res['errorCode']==40:
        return '不支持的语言类型\n'
    elif res['errorCode']==60:
        return '无词典结果\n'
    else:
        inputKey=res['query']+'\n'
        youdaoTranslation=u'---有道翻译---'+'\n'+res['translation'][0]+'\n'
        youdaoWeb=u'---网络释义---'+'\n'
        if res.has_key('basic'):
            for i in res['basic'].keys():
                if i=='us-phonetic':
                    youdaoWeb=youdaoWeb+u'美式读法：'+res['basic'][i]+u'（Sorry，只有音标，真的没有语言）'+'\n'
                elif i=='explains':
                    for a in  res['basic'][i]:
                        youdaoWeb=youdaoWeb+a+'\n'
        else:
            youdaoWeb=youdaoWeb+u'没有网络释义！'+'\n'
        contentStr=inputKey+youdaoTranslation+youdaoWeb
        return contentStr
    
    
    
    

    




