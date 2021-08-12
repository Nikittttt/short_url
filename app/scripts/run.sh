sleep 1
export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000
flask db init
flask db migrate
flask db upgrade
