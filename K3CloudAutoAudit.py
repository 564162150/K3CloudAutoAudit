import json,requests

login_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.AuthService.ValidateUser.common.kdsvc"

#保存
save_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Save.common.kdsvc"
#删除
delete_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Delete.common.kdsvc"
#提交
Submit_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Submit.common.kdsvc"
#审核
Audit_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.Audit.common.kdsvc"
#反审核
UnAudit_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.UnAudit.common.kdsvc"
#查询
ExecuteBillQuery_url="http://192.168.190.113/k3cloud/Kingdee.BOS.WebApi.ServicesStub.DynamicFormService.ExecuteBillQuery.common.kdsvc"


def jsmsg(Submit):
    jsResult=json.loads(Submit.text)
    if jsResult['Result']['ResponseStatus']['IsSuccess']:
        jserr=jsResult['Result']['ResponseStatus']['SuccessEntitys']
        for i in jserr:
            successmsg='单号【'+i['Number']+'】处理成功！'
            return successmsg
    else:
        jserr=jsResult['Result']['ResponseStatus']['Errors']
        for i in jserr:
            errmsg='错误信息：'+i['Message']
            return errmsg

#定义提交并审核方法
def sububill(billidinfo,billtype,step):
    #计算循环处理批次
    if len(billidinfo) and len(billidinfo)%step==0:
        b=(len(billidinfo)//step)
    elif len(billidinfo)%step:
        b=(len(billidinfo)//step)+1
    elif len(billidinfo)==0:
        b=[]
    #开始循环
    for i in range(b):
        #审核指定ID的单据
        ida=billidinfo[step*i:step*(i+1)]
        idd = [str(j) for j in flat1(ida)]
        ids = ','.join(idd)
        print('待提交ID：',ids)
        post_Su = {"FormId": "%s"%(billtype),
                "Data": json.dumps({"Ids": "%s" % (ids)})}
        #提交单据
        Submit=requests.post(url=Submit_url,data=post_Su,cookies=login())
        print(jsmsg(Submit))     
        #审核单据
        for xi in ida:
            print('待审核ID：',xi)
            post_Au = {"FormId": "%s"%(billtype),
                "Data": json.dumps({"Ids": "%s" % (xi[0])})}
            Audit=requests.post(url=Audit_url,data=post_Au,cookies=login())
            print(jsmsg(Audit))


#登录信息
acctid='xxxx'#帐套ID
username='xxxx'#登录用户名
password='xxxx'#密码
lcid='xxxx'
login_data={"acctid":acctid,"username":username,"password":password,"lcid":lcid}

# 定义登录函数
def login():  
    login_response=requests.post(url=login_url,data=login_data)
    return login_response.cookies   #  返回cookies,方便下次访问时携带

#摊平数组算法
def flat1(inputlist, result=None):
    if result is None:
        result = []
    for item in inputlist:
        if isinstance(item, list):
            flat1(item, result)
        else:
            result.append(item)
    return result



##开始查询待提交或审核ID范围
#检查单据类型
#IV_SALESOC 普票
#IV_SALESIC 专票
#AR_receivable 应收单
billtypes=['IV_SALESIC','IV_SALESOC']
#组装筛选条件时间
Jztime='2020/05/01 00:00:00'
#组装内容
for billtype in billtypes:
    post_data = {"data": json.dumps({"FormId": "%s"%(billtype), "FieldKeys": "FID","FilterString": "FDOCUMENTSTATUS !='C' AND FDATE>=TO_DATE(\'%s\','YYYY/MM/DD HH24:MI:SS')" % (Jztime)})}
    #提交并接收结果内容
    response=requests.post(url=ExecuteBillQuery_url,data=post_data,cookies=login())
    #显示ID结果
    jsob=json.loads(response.text)
    print('总共待审核单数：'+str(len(jsob)))
    #每次提交和审核单数
    if len(jsob):
        step=10
        sububill(jsob,billtype,step)
    else:
        pass
