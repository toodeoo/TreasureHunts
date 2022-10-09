from flask import Flask, request, render_template, url_for, make_response
import pymongo
import random
from werkzeug.utils import redirect
from hashlib import md5

app = Flask(__name__)

# Connect to Database
# 数据库中，Treasure 的class 0代表工具， 1代表配饰

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    if request.method == 'GET':
        name = request.args.get('username')
        pwd = request.args.get('password')
        pwd = md5(pwd.encode('utf-8')).hexdigest()
        person = db['User'].find_one({"username": name})
        if person == None:
            return render_template('sign.html')
        if person.get('pwd') == pwd:
            reps = make_response(render_template('homepage.html',re=[name]))
            reps.set_cookie("username", name)
            return reps

@app.route('/homepage')
def homepage():
    re = [request.cookies.get("username")]
    return render_template('homepage.html',re=re)

@app.route('/sign')
def sign():
    return render_template('sign.html')

@app.route('/signup')
def signup():
    if request.method == 'GET':
        username = request.args.get('username')
        pwd = request.args.get("password")
        pwd = md5(pwd.encode('utf-8'))
        flag = 0
        user = db['User']
        person = user.find_one({"username": username})
        if person != None:
            flag = 1
        else:
            treasure = db['Treasure']
            init_treasure = [treasure.find_one({"name": "帽子"}), treasure.find_one({"name": "充电器"})]
            treasure_list = [init_treasure[0].get('treasureId'), init_treasure[1].get('treasureId')]
            init_luck, init_work = 0, 0
            for i in init_treasure:
                if i.get('class') == 1:
                    init_luck += i.get('property')
                else:
                    init_work += i.get('property')
            user.insert_one({
                "username": username,
                "pwd": pwd.hexdigest(),
                "money": 10,
                "arm": [],
                "backpack": treasure_list,
                "luck": init_luck,
                "work": init_work
            })
        reps = make_response(render_template('signup.html',name=username,tag=flag))
        reps.set_cookie("username", username)
        return reps

@app.route('/myinfo')
def myinfo():
    username = request.cookies.get("username")
    user = db["User"].find_one({"username": username})
    money = user.get("money")
    # row1为装备在身上的装备， row2为放在背包里的装备，装备的格式为：装备名称 等级 装备详情
    row1, row2 = [], []
    treasure = db["Treasure"]
    for i in user.get("arm"):
        if i == None:
            break
        item = treasure.find_one({"treasureId": i})
        row1.append([item.get("name"), item.get("level")])
    for i in user.get("backpack"):
        if i == None:
            break
        item = treasure.find_one({"treasureId": i})
        row2.append([item.get("name"), item.get("level"), i])

    return render_template('myinfo.html',name=username,money=money,row1=row1,row2=row2)

@app.route('/equip_info')
def equip_info():
    return render_template('equipinfo.html')

@app.route('/sto_info')
def sto_info():
    if request.method == 'GET':
        name = request.args.get('name')
        treasure = db['Treasure'].find_one({"name": name})
        cla = "工具类" if treasure.get('class') == 0 else "配饰类"
        luck = 0 if treasure.get('class') == 0 else treasure.get('property')
        ability = 0 if treasure.get('class') == 1 else treasure.get('property')
        return render_template('stoinfo.html',
                               name=name, treasureId=treasure.get('treasureId'),
                               cla=cla, luck=luck, ability=ability)

@app.route('/take_off')
def take_off():
    return render_template('take_off.html'  ,tag=0)

@app.route('/take_on')
def take_on():
    return render_template('take_on.html',tag=0)

@app.route('/marinfo')
def marinfo():

    re=[['装备1',0,1,2,3],['装备2',0,1,2,3],['装备3',0,1,2,3]]
    return render_template('marinfo.html', re=re)

@app.route('/buy')
def buy():
    return render_template('buy.html', tag=0)
@app.route('/sell')
def sell():
    re = [['装备1', 'equip0001', 1, 2, 3], ['装备2', 'equip0002', 1, 2, 3], ['装备3', 'equip0002', 1, 2, 3]]
    return render_template('sell.html', re=re)
@app.route('/sell_it')
def sell_it():
    return render_template('sellinfo.html')

@app.route('/look_for_treasure')
def look_for_treasure():
    return render_template('look_for_treasure.html',equip_name='手套',tag=0)

@app.route('/look_for_money')
def look_for_money():
    return render_template('look_for_money.html',money=10)

app.config['DEBUG'] = True
app.secret_key = '123456'

if __name__ == '__main__':
    setting = {
        'ip': "mongodb://127.0.0.1:27017",
        'db_name': 'Game'
    }
    client = pymongo.MongoClient(setting['ip'])
    db = client[setting['db_name']]
    app.run(host='127.0.0.1', port=5005)
