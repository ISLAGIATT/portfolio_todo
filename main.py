# TODO: Delete button, fix layout

from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.fields import TextAreaField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'something_else2'
Bootstrap5(app)

CSRFProtect(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

current_datetime = datetime.now()

class Todo(db.Model):
    __tablename__ = 'todo_list'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    due_date = db.Column(db.String)
    category = db.Column(db.String)
    priority = db.Column(db.String)
    timestamp = db.Column(db.Integer)

class Task(FlaskForm):
    description = TextAreaField("Task Name", validators=[DataRequired(), Length(max=25)], default="max 25 characters")
    due_date = StringField("Due Date", validators=[DataRequired()])
    category = SelectField("Category", choices=[('work', 'Work'), ('personal', 'Personal'), ('other', 'Other')],
                           validators=[DataRequired()])
    priority = SelectField("Priority", choices=[('urgent', 'Urgent'), ('normal', 'Normal'), ('low', 'Low')],
                           validators=[DataRequired()])
    timestamp = current_datetime.strftime("%m/%d/%y")
    submit = SubmitField("add task")


with app.app_context():
    db.create_all()
@app.route('/', methods=['GET', 'POST', 'DELETE'])
def home():
    form = Task(meta={'csrf': False})
    sort_by = request.form.get('sort_by', 'due_date')

    if sort_by == 'due_date':
        todo_items = Todo.query.order_by(Todo.due_date.asc()).all()
    elif sort_by == 'description':
        todo_items = Todo.query.order_by(Todo.description.asc()).all()
    elif sort_by == 'timestamp':
        todo_items = Todo.query.order_by(Todo.timestamp.asc()).all()
    elif sort_by == 'category':
        todo_items = Todo.query.order_by(Todo.category.asc()).all()
    elif sort_by == 'priority':
        todo_items = Todo.query.order_by(Todo.priority.asc()).all()
    else:
        todo_items = Todo.query.all()
    if form.validate_on_submit():
        if len(form.description.data) > 25:
            flash('Description may not exceed 25 characters', 'error')
        else:
            new_task = Todo(
                description=form.description.data,
                due_date=form.due_date.data,
                timestamp=datetime.now().strftime("%m/%d/%y %H:%M"),
                category=form.category.data,
                priority=form.priority.data
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
        return redirect(url_for('home'))
    else:
        print(form.errors)
    return render_template('index.html', form=form, todo_items=todo_items)


if __name__ == "__main__":
    app.run(debug=True, port=5002)