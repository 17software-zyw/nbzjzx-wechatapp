import pymysql
import requests
import hashlib
import re
from bs4 import BeautifulSoup
import logging

# username="s171405"
# password="12345678"
# 成绩爬取
def login(user, pwd):
    passwordhash = hashlib.md5(pwd.encode("utf8")).hexdigest() + hashlib.sha1(pwd.encode("utf8")).hexdigest()
    s = requests.Session()
    data = {
        'action': 'login',
        'username': user,
        'password': passwordhash,
        'server': '1013301',
        'url': 'http://zhgl.nbzjzx.com.cn/eisu/fpf/homepage/loginForEisOnly.action'
    }
    r = s.get('http://zhgl.nbzjzx.com.cn/passport/scriptLogin', params=data)

    if r.text.find('用户名不存在') >= 0:
        return '账号不存在'

    if r.text.find('请输入正确的账户或密码') >= 0:
        return '用户名或密码错误'

    loginurl = re.search(r'verifyURL="(.+?)"', r.text).group(1)
    login = s.get(loginurl)
    return s


def get_name(s):
    urluserinfo = 'http://zhgl.nbzjzx.com.cn/eisu/system/desktop/app/userInfo.action'
    stuinfo = 'http://zhgl.nbzjzx.com.cn/eisu/stuwork/desktop/app/stuInfo.action'

    r1 = s.get(urluserinfo)
    r2 = s.get(stuinfo)

    soup = BeautifulSoup(r1.text, "html.parser")
    soup1 = BeautifulSoup(r2.text, "html.parser")

    stu_name = soup.p.contents[0].strip()
    print(soup.p.contents[0].strip())
    stu_infor= soup1.find_all('li')
    stu_class = stu_infor[0].contents[1]
    print(stu_infor[0].contents[1])
    stu_num = stu_infor[1].contents[1]
    print(stu_infor[1].contents[1])

    stu_infor={'name':stu_name,'class':stu_class,'num':stu_num }

    return stu_infor


def get_cj(s):
    time = "2017-2018"
    num = "2"
    cjurl = "http://zhgl.nbzjzx.com.cn/eisu/achievement/stuplatform/personalAchisubmitquery.action?acadyear=%s&semester=%s" % (
    time, num)
    cjreq = s.get(cjurl);
    cjsoup = BeautifulSoup(cjreq.text, "html.parser")
    
    cjdata= cjsoup.find_all('td')
    cj_key=""
    cj_in_value=""
    cj_end_value=""
    cj_in_data={}
    cj_end_data={}
    x = 1
    for cj in cjdata:
        # print(cj.text.strip())
        if x==1:
            cj_key=cj.text.strip()
            # print(cj_key)
        elif x==3:
            cj_in_value=cj.text.strip();
            # print(cj_dic)
        elif x==4:
            cj_end_value=cj.text.strip();
            # print(cj_dic)
        elif x==8:
            cj_in_data[cj_key]=cj_in_value
            cj_end_data[cj_key]=cj_end_value
            x=0;
            
        x+=1
    print({"期中":cj_in_data,"期末":cj_end_data})
    return({"期中":cj_in_data,
            "期末":cj_end_data})

def get_threefrom(s):
    time = "2018-2019"
    num = "1"
    url = "http://zhgl.nbzjzx.com.cn/eisu/stuwork/stuplatform/sldQuery-list.action?acadyear=%s&semester=%s" % (
    time, num)
    req = s.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    fraction = soup.find(attrs={"class": "c-green b f14"}).text
    threefrom = {}
    threefrom["fraction"] = fraction
    td = soup.find_all("td")
    data = []
    datas = []
    n = 1
    for fr in td:
        data.append(fr.text.strip("\n"))
        if n == 4:
            n = 0
            datas.append(data)
            data=[]
        n += 1

    threefrom["data"] = datas
    print(threefrom)
    return threefrom


# # 打开数据库
# name=soup.find(attrs={"class":"name"}).text.strip()
# db = pymysql.connect("localhost","root","" ,"cj")
# cursor = db.cursor()
# # print(achievement)
# # 打开数据库连接
#
# cursor.execute('INSERT INTO midterm VALUES("%s","%d","%d","%d",0,"%s","%d")'
#                %(username,
#                  int(achievement["chinese"]),
#   
#
#               int(achievement["math"]),
#                  int(achievement["english"]),
#                  time,
#                  int(num)))
# db.commit()
# db.close()


from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/cj/api/v1.0', methods=['POST', 'GET'])
def get_tasks():
    if request.method == "GET":
        app.logger.info(" GET方法成功")
        return "aa";
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        s = login(username, password)
        print(s)
        if s == '账号不存在' or s == '用户名或密码错误':
            return s
        else:
            app.logger.info(username+"登陆成功")
            return '登入成功'

@app.route('/cj/api/v1.0/name', methods=['POST'])
def get_names():
    username = request.form.get('username')
    password = request.form.get('password')
    s = login(username, password)
    user = get_name(s)
    app.logger.info(user)
    return jsonify(user)


@app.route('/cj/api/v1.0/cj', methods=['POST'])
def get_cjs():
    username = request.form.get('username')
    password = request.form.get('password')
    s = login(username, password)
    cj = get_cj(s)
    app.logger.info(cj)
    return jsonify(cj)


@app.route('/cj/api/v1.0/threefrom', methods=['POST'])
def get_threefroms():
    username = request.form.get('username')
    password = request.form.get('password')
    s = login(username, password)
    fr = get_threefrom(s)
    app.logger.info(fr)
    return jsonify(fr)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
