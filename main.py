from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Tasks.sqlite'
db = SQLAlchemy(app)
logging.getLogger().setLevel(logging.DEBUG)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    completed = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    logging.debug("Debug message")
    logging.info("Information message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")
    db.create_all()
    return render_template('home.html')

@app.route('/api/tasks', methods = ['GET', 'POST', 'PUT', 'DELETE'])  # ここからAPI
@app.route('/api/tasks/<int:id>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def tasks(id=None):
    if request.method == 'GET':  # GETメソッド
        if id:  # 一件ずつ
            task = Tasks.query.get_or_404(id)
            return render_template('index_one.html', task=task)
        else:  # 全件（登録日順）
            tasks = Tasks.query.order_by(Tasks.date_created).all()
            return render_template('index.html', tasks=tasks)
    elif request.method == 'POST':  # POSTメソッド（json or フォーム）
        if id:
            return '新規登録にidは不要です。'
        else:
            try:  # json
                json_post = request.get_json()
                task_content = json_post['content']
                new_task = Tasks(content=task_content, completed='□')
                db.session.add(new_task)
                db.session.commit()
                return redirect('/api/tasks')
            except:  # フォーム
                try:
                    task_content = request.form['content']
                    new_task = Tasks(content=task_content, completed='□')
                    db.session.add(new_task)
                    db.session.commit()
                    return redirect('/api/tasks')
                except:
                    return '登録中に問題が発生しました。'
    elif request.method == 'PUT':  # PUTメソッド経由の編集（json）
        if id:
            task_to_update = Tasks.query.get_or_404(id)
            try:
                json_put = request.get_json()
                task_to_update.content = json_put['content']
                db.session.commit()
                return redirect('/api/tasks')
            except:
                return '編集中に問題が発生しました。'  
        else:
            return '編集するタスクのidを入力してください。'      
    else:  # DELETEメソッド経由の削除
        if id:  # 一件ずつ
            task_to_delete = Tasks.query.get_or_404(id)
            try:
                db.session.delete(task_to_delete)
                db.session.commit()
                return redirect('/api/tasks')
            except:
                return '削除中に問題が発生しました。'
        else:  # 全件
            tasks = Tasks.query.all()
            try:
                for task in tasks:
                    db.session.delete(task)
                db.session.commit()
                return redirect('/api/tasks')
            except:
                return '削除中に問題が発生しました。'

@app.route('/api/tasks/<int:id>/delete')  # URL（ボタン）経由の削除
def delete(id):
    task_to_delete = Tasks.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/api/tasks')
    except:
        return '削除中に問題が発生しました。'

@app.route('/api/tasks/<int:id>/update', methods=['GET', 'POST'])  # URL（ボタン）経由の編集（フォーム）
def update(id):
    task_to_update = Tasks.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('update.html', task=task_to_update)
    else:
        task_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/api/tasks')
        except:
            return '編集中に問題が発生しました。'

@app.route('/api/tasks/<int:id>/complete')  # 完了を押したらチェック
def complete(id):
    task_to_complete = Tasks.query.get_or_404(id)
    try:
        task_to_complete.completed = '☑'
        db.session.commit()
        return redirect('/api/tasks')
    except:
        return '削除中に問題が発生しました。'

@app.errorhandler(400)
def handle_400(exception):
    res = {
        'message': 'Your browser sent a request that this server could not understand.',
        'description': exception.description
    }
    return res, 400

@app.errorhandler(404)
def handle_404(exception):
    res = {
        'message': 'Resource not found.',
        'description': exception.description
    }
    return res, 404

@app.errorhandler(500)
def handle_500(exception):
    res = {
        'message': 'Please contact the administrator.',
        'description': exception.description
    }
    return res, 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
