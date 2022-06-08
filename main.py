import sqlite3
from flask import *
from flask_cors import CORS

DATABASE = './db.db'

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(
    app,
    supports_credentials=True
)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def clear_db():
    con = get_db()
    con.execute("CREATE TABLE IF NOT EXISTS thread(id INTEGER PRIMARY KEY AUTOINCREMENT, name STRING)")
    con.execute("CREATE TABLE IF NOT EXISTS response(id INTEGER PRIMARY KEY AUTOINCREMENT, post STRING, created_at TEXT NOT NULL DEFAULT (DATETIME('now', 'localtime')))")
    con.execute("CREATE TABLE IF NOT EXISTS thr_res(thread_id INTEGER, res_id INTEGER)")
    con.commit()


def create_seed_data():
    con = get_db()
    con.execute("INSERT INTO thread(name) values('テスト1')")
    con.execute("INSERT INTO thread(name) values('テスト2')")
    con.execute("INSERT INTO thread(name) values('テスト3')")
    con.execute("INSERT INTO thread(name) values('テスト4')")
    con.execute("INSERT INTO thread(name) values('テスト5')")
    con.commit()


@app.route("/health_check")
def health_check():
    return json.dumps({"language": "japanese"})


@app.route("/create_seed_db")
def create_db():
    clear_db()
    create_seed_data()
    return json.dumps({"status": "OK"})

@app.route("/api/thread", methods=['POST'])
def create_thread():
    req_json = request.get_json()

    try:
        con.execute("INSERT INTO thread(name) values({})".format(req_json["thread_name"]))
        con.close()
        return json.dumps({"status": "ok"})
    except:
        return json.dumps({"status": "false"})

@app.route("/api/thread", methods=['GET'])
def read_threads():
    con = get_db()

    if request.args.get('id'):
        thr_id = int(request.args.get('id'))
        print(thr_id)
        res_json = {"res": []}
        try:
            res_ids = []
            query1 = "SELECT * FROM thr_res WHERE thread_id={}".format(thr_id)
            print(query1)
            cur = con.execute(query1)
            for row in cur:
                res_ids.append(row[1])
            print(res_ids)
            for i in res_ids:
                query2 = "SELECT * FROM response WHERE id={}".format(i)
                res = con.execute(query2)
                for j in res:
                    print(j[2])
                    res_json["res"].append({
                        "id": j[0],
                        "content": j[1],
                        "timestamp": j[2]
                    })
                print("hogehoge")
            return json.dumps(res_json)
        except Exception as e:
            print(e)
            return json.dumps({"status": "false1"})


    res_json = {"threads": []}
    try:
        cur = con.execute("SELECT * FROM thread")
        for row in cur:
            res_json["threads"].append({
                "id": row[0],
                "name": row[1]
            })
        return json.dumps(res_json)

    except:
        return json.dumps({"status": "false2"})

@app.route("/api/res", methods=['POST'])
def create_post():
    req_json = request.get_json()
    print(req_json)
    con = get_db()

    try:
        con.execute("INSERT INTO response(post) values('{}')".format(req_json["content"]))
        con.commit()
        cur = con.execute("SELECT id FROM response WHERE post='{}'".format(req_json["content"]))
        post_id = 0
        for i in cur:
            post_id = i[0]
        query = "INSERT INTO thr_res(thread_id, res_id) VALUES({}, {})".format(req_json["id"], post_id)
        print(query)
        cur = con.execute(query)
        con.commit()
        return json.dumps({"status": "ok"})
    except Exception as e:
        print(e)
        return json.dumps({"status": "false"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)