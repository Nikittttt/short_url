from flask import Flask, redirect, abort, render_template, request
import shortuuid

from db import DB

app = Flask(__name__)
        
        
@app.route('/', methods=['post', 'get'])
def index():
    db = DB()
    message = ''
    if request.method == 'POST':
        url = request.form['url']
        short_url = request.form['short_url']

        if not short_url:
            id_l = db.get_or_create_id_url(url, 0)['id']

            short = shortuuid.uuid(name=url)

            id_info = db.get_or_create_connect(short, 1, id_l)
            if not id_info['is_create']:
                return abort(404)
        else:
            id_l = db.get_or_create_id_url(url, 0)['id']

            short = short_url

            id_info = db.get_or_create_connect(short, 1, id_l)
        
        message = f'Короткая ссылка для "{url}" - "{short}"'

    return render_template('form.html', message=message)


@app.route('/<string:short_url>', methods=['get'])
def short_url(short_url):
    db = DB()
    info_url = db.get_info_url(short_url)
    if not info_url:
        return abort(404)
    else:
        info_url = dict(zip(['id', 'is_short'], info_url))
    url = db.get_url_from_connect(info_url['is_short'], info_url['id'])
    if not url:
        return abort(404)
    return redirect(url[0], code=301)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
