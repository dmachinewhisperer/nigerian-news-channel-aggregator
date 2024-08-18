from flask import Blueprint, jsonify, request, abort
from .models import Current
from .models import Historical

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to the Home Page!"


@main.route('/about')
def about():
    return "This is the About Page."


@main.route('/api/news_items/<pub_name>', methods=['GET'])
def get_news_items(pub_name):
    if pub_name == "all":
        items = Current.query.all()
    else:
        items = Current.query.filter_by(name=pub_name).all()

        if not items:
            return jsonify({"error": f"No news items found for the name '{pub_name}'."}), 404

    '''
    file_path = 'output.txt'
    with open(file_path, 'w') as file:
        file.write(f'Length of items: {len(items)}\n')
    '''
    data = [{
        'id': item.id,
        'name': item.name,
        'pubDate': item.pubDate.isoformat(),
        'title': item.title,
        'description': item.description,
        'link': item.link
    } for item in items]

    return jsonify(data)

@main.route('/api/history', methods=['GET'])
def get_historical_news():
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        if limit < 1 or offset < 0:
            return jsonify({'error': 'Invalid limit or offset'}), 400
        
        items = Historical.query.offset(offset).limit(limit).all()
        
        data = [{
            'id': item.id,
            'name': item.name,
            'pubDate': item.pubDate.isoformat(),
            'title': item.title,
            'description': item.description,
            'link': item.link
        } for item in items]

        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500