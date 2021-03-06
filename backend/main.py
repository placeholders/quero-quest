import os
import json
import datetime
from operator import itemgetter

from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
CORS(app)

db.init_app(app)

@app.route('/user/register', methods=['GET', 'POST'])
def register_user():
    #name = request.form.get('name')
    #login = request.form.get('login')
    #password = request.form.get('password')
    #confirm_password = request.form.get('confirmed_password')
    data = request.json
    name = data['name']
    login = data['login']
    password = data['password']
    confirm_password = data['confirmed_password']

    user = UserTable.query.filter_by(login=login).first()

    if user:
        return json.dumps({'status': 1, 'message': 'login already exists'})
    elif password != confirm_password:
        return json.dumps({'status': 1, 'message': 'passwords dont match'})
    else:
        db.session.add(UserTable(name, login, password))
        db.session.commit()
        return json.dumps({'status': 0, 'message': 'user {} successfully registered'.format(login)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    #login = request.form.get('user')
    #password = request.form.get('password')
    data = request.json
    login = data['login']
    password = data['password']

    user = UserTable.query.filter_by(login=login).first()

    if not user:
        return json.dumps({'status': 1, 'message': 'invalid login'})

    if user.password == password:
        return json.dumps({'status': 0, 'message': 'logged in successfully'})
    else:
        return json.dumps({'status': 1, 'message': 'wrong password'})

@app.route('/issue/add', methods=['GET', 'POST'])
def add_issue():
    #user = request.form.get('user')
    #title = request.form.get('title')
    #description = request.form.get('description')
    data = request.json
    user = data['login']
    title = data['title']
    description = data['description']

    issue = IssueTable.query.filter_by(title=title).first()

    if issue:
        return json.dumps({'status': 1, 'message': 'an issue with this title already exists'})
    else:
        creator_id = UserTable.query.filter_by(login=user).first().id
        db.session.add(IssueTable(title, description, creator_id, None, datetime.datetime.now(), 0, 0))
        db.session.commit()
        return json.dumps({'status': 0, 'message': 'quest successfully added'})

@app.route('/issue/update', methods=['GET', 'POST'])
def update_issue():
    #issue_id = request.form.get('issue_id')
    #title = request.form.get('title')
    #description = request.form.get('description')
    data = request.json
    issue_id = data['issue_id']
    title = data['title']
    description = data['description']

    issue = IssueTable.query.filter_by(id=issue_id).first()
    issue.title = title
    issue.description = description

    db.session.commit()

    return json.dumps({'status': 0, 'message': 'quest "{}" successfully updated'.format(title)})

@app.route('/solution/add', methods=['GET', 'POST'])
def add_solution():
    #login = request.form.get('user')
    #issue_id = request.form.get('issue_id')
    #description = request.form.get('description')
    data = request.json
    login = data['login']
    issue_id = data['issue_id']
    description = data['description']

    user = UserTable.query.filter_by(login=login).first()
    issue = IssueTable.query.filter_by(id=issue_id).first()

    issue.user_solver_id = user.id
    db.session.add(SolutionTable(description, user.id, issue_id, datetime.datetime.now(), 0, 0))
    db.session.commit()

    return json.dumps({'status': 0, 'message': 'quest "{}" successfully turned in'.format(issue.title)})

@app.route('/issue/update/upvote', methods=['GET', 'POST'])
def upvote_issue():
    #user = request.form.get('user')
    #issue_id = request.form.get('issue_id')
    data = request.json
    user = data['login']
    issue_id = data['issue_id']

    user = UserTable.query.filter_by(login=user).first()
    issue = IssueTable.query.filter_by(id=issue_id).first()
    issue_vote = VoteIssueTable.query.filter_by(user_id=user.id, issue_id=issue_id).first()

    if issue_vote:
        if not issue_vote.isupvote:
            issue.down_votes -= 1
            issue_vote.isupvote = True
        else:
            return json.dumps({'status': 0, 'up_votes': issue.up_votes, 'down_votes': issue.down_votes})
    else:
        db.session.add(VoteIssueTable(user.id, issue_id, True))

    issue.up_votes += 1

    db.session.commit()

    return json.dumps({'status': 0, 'up_votes': issue.up_votes, 'down_votes': issue.down_votes})

@app.route('/issue/update/downvote', methods=['GET', 'POST'])
def downvote_issue():
    #user = request.form.get('user')
    #issue_id = request.form.get('issue_id')
    data = request.json
    user = data['login']
    issue_id = data['issue_id']

    user = UserTable.query.filter_by(login=user).first()
    issue = IssueTable.query.filter_by(id=issue_id).first()
    issue_vote = VoteIssueTable.query.filter_by(user_id=user.id, issue_id=issue_id).first()

    if issue_vote:
        if issue_vote.isupvote:
            issue.up_votes -= 1
            issue_vote.isupvote = False
        else:
            return json.dumps({'status': 0, 'up_votes': issue.up_votes, 'down_votes': issue.down_votes})
    else:
        db.session.add(VoteIssueTable(user.id, issue_id, False))

    issue.down_votes += 1

    db.session.commit()

    return json.dumps({'status': 0, 'down_votes': issue.down_votes, 'up_votes': issue.up_votes})

@app.route('/solution/update/upvote', methods=['GET', 'POST'])
def upvote_solution():
    #user = request.form.get('user')
    #solution_id = request.form.get('solution_id')
    data = request.json
    user = data['login']
    solution_id = data['solution_id']

    user = UserTable.query.filter_by(login=user).first()
    solution = SolutionTable.query.filter_by(id=solution_id).first()
    #solution_vote = VoteSolutionTable.query.filter_by(user_id=user.id, solution_id=solution_id).first()
    solution_vote = VoteSolutionTable.query.filter_by(user_id=user.id, solution_id=solution_id).first()

    if solution_vote:
        if not solution_vote.isupvote:
            solution.down_votes -= 1
            solution_vote.isupvote = True
        else:
            return json.dumps({'status': 0, 'up_votes': solution.up_votes, 'down_votes': solution.down_votes})
    else:
        db.session.add(VoteSolutionTable(user.id, solution_id, True))

    solution.up_votes += 1

    db.session.commit()

    return json.dumps({'status': 0, 'up_votes': solution.up_votes, 'down_votes': solution.down_votes})

@app.route('/solution/update/downvote', methods=['GET', 'POST'])
def downvote_solution():
    #user = request.form.get('user')
    #solution_id = request.form.get('solution_id')
    data = request.json
    user = data['login']
    solution_id = data['solution_id']

    user = UserTable.query.filter_by(login=user).first()
    solution = SolutionTable.query.filter_by(id=solution_id).first()
    solution_vote = VoteSolutionTable.query.filter_by(user_id=user.id, solution_id=solution_id).first()

    if solution_vote:
        if solution_vote.isupvote:
            solution.up_votes -= 1
            solution_vote.isupvote = False
        else:
            return json.dumps({'status': 0, 'down_votes': solution.down_votes, 'up_votes': solution.up_votes})
    else:
        db.session.add(VoteSolutionTable(user.id, solution_id, False))

    solution.down_votes += 1

    db.session.commit()

    return json.dumps({'status': 0, 'down_votes': solution.down_votes, 'up_votes': solution.up_votes})

@app.route('/quests', methods=['GET'])
def get_quests():
    quests = IssueTable.query.all()
    ans = dict(quests=[])
    for q in quests:
        if q.user_solver_id:
            continue
        user = UserTable.query.filter_by(id=q.user_creator_id).first()
        quest = dict(
            quest_id=q.id,
            creator=user.login,
            created_date=str(q.created_date),
            description=q.description,
            title=q.title,
            up_votes=q.up_votes,
            down_votes=q.down_votes
        )
        ans['quests'].append(quest)

    return json.dumps(ans)

@app.route('/users/scores', methods=['GET'])
def user_scores():
    users = UserTable.query.all()

    ans = dict(users=[])
    for user in users:
        score = 0

        quests = IssueTable.query.filter_by(user_creator_id=user.id).all()
        for q in quests:
            score += (q.up_votes - q.down_votes)

        solved = SolutionTable.query.filter_by(user_id=user.id).all()
        for q in solved:
            score += q.up_votes

        user_dict = dict(
            name=user.name,
            login=user.login,
            score=score
        )
        ans['users'].append(user_dict)

    ans['users'] = sorted(ans['users'], key=itemgetter('score'), reverse=True)
    return json.dumps(ans)

@app.route('/quests/completed', methods=['GET'])
def get_completed_quests():
    quests = IssueTable.query.all()
    ans = dict(quests=[])
    for q in quests:
        if not q.user_solver_id:
            continue
        creator = UserTable.query.filter_by(id=q.user_creator_id).first()
        solver = UserTable.query.filter_by(id=q.user_solver_id).first()
        quest = dict(
            quest_id=q.id,
            creator=creator.login,
            solver=solver.login,
            created_date=str(q.created_date),
            description=q.description,
            title=q.title,
            up_votes=q.up_votes,
            down_votes=q.down_votes
        )
        ans['quests'].append(quest)

    return json.dumps(ans)

@app.route('/quest/get', methods=['GET', 'POST'])
def get_quest_by_id():
    data = request.json
    quest_id = data['id']

    quest = IssueTable.query.filter_by(id=quest_id).first()

    return json.dumps({'up_votes': quest.up_votes, 'down_votes': quest.down_votes,
                       'title': quest.title, 'description': quest.description})
