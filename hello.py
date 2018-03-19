from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from elasticsearch import Elasticsearch


app = Flask(__name__)
app.config.from_pyfile('hello.cfg')
db = SQLAlchemy(app)
es = Elasticsearch()

class Model2ES(db.Model):
    __abstract__ = True


class Todo(Model2ES):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    text = db.Column(db.String(191))
    done = db.Column(db.Boolean)
    pub_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.done = False
        self.pub_date = datetime.utcnow()


def receive_after_update(mapper, connection, target):
    "listen for the 'after_update' event"
    # ... (event handling logic) ...
    # print('this is mapper', mapper, type(mapper), dir(mapper))
    # for x in dir(mapper):
    #     if x.startswith('_'):
    #         continue
    #     print(x, getattr(mapper, x))
    tablename = mapper.mapped_table.name
    body = {}
    for x in mapper.attrs:
        print(x, type(x))
    for name in mapper.c.keys():
        print(name, getattr(target, name))
        body[name] = getattr(target, name)

    print('this is tablename', tablename)
    print('this is body', body)
    # 使用es的接口更新es的数据
    index = 'logstash-todos-v2'
    doc_type = 'doc'
    id = target.id
    res = es.index(index=index, doc_type=doc_type, id=id, body=body)
    print('this is es index res', res)


event.listen(Model2ES, 'after_update', receive_after_update, propagate=True)


@app.route('/create_all')
def create_all():
    r = db.create_all()
    print(r)
    return 'create all'

@app.route('/')
def show_all():
    return render_template('show_all.html',
        todos=Todo.query.order_by(Todo.pub_date.desc()).all()
    )


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['title']:
            flash('Title is required', 'error')
        elif not request.form['text']:
            flash('Text is required', 'error')
        else:
            todo = Todo(request.form['title'], request.form['text'])
            db.session.add(todo)
            db.session.commit()
            flash(u'Todo item was successfully created')
            return redirect(url_for('show_all'))
    return render_template('new.html')


@app.route('/update', methods=['POST'])
def update_done():
    for todo in Todo.query.all():
        todo.done = ('done.%d' % todo.id) in request.form
    flash('Updated status')
    db.session.commit()
    return redirect(url_for('show_all'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
