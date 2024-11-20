import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
from stockfish import Stockfish
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)

# 配置密钥和JWT参数
SECRET_KEY = 'jiyejia666'  # 替换为您的密钥
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600  # 令牌有效期（秒）

# MongoDB 初始化
client = MongoClient('mongodb://localhost:27017/')
db = client['chess_db']  # 替换为您的数据库名称
users_collection = db['users']
games_collection = db['games']

# 初始局面
initial_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# 初始化 Stockfish 引擎
stockfish = Stockfish(path="./stockfish.exe")  # 请确保路径正确
stockfish.set_skill_level(1)  # 设置 AI 难度（0-20）

# 注册
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'message': '用户已存在'}), 400

    hashed_password = generate_password_hash(password)

    user_data = {
        'username': username,
        'password': hashed_password,
        'created_at': datetime.utcnow()
    }
    users_collection.insert_one(user_data)

    return jsonify({'message': '注册成功'}), 200

# 登录
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({'message': '用户不存在'}), 400

    if not check_password_hash(user['password'], password):
        return jsonify({'message': '密码错误'}), 400

    payload = {
        'user_id': str(user['_id']),
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return jsonify({'message': '登录成功', 'token': token}), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头中获取 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                raise Exception('User not found')
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# 验证 JWT 令牌
@app.route('/verify_token', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({'valid': True, 'username': current_user['username']}), 200

# 创建新游戏
@app.route('/start_game', methods=['POST'])
@token_required
def start_game(current_user):
    user_id = str(current_user['_id'])

    game_data = {
        'user_id': ObjectId(user_id),
        'start_time': datetime.utcnow(),
        'moves': [],
        'fen_positions': [initial_fen],
        'result': None
    }

    game = games_collection.insert_one(game_data)
    game_id = str(game.inserted_id)

    # 设置Stockfish初始位置
    stockfish.set_fen_position(initial_fen)

    return jsonify({'message': '游戏已创建', 'game_id': game_id, 'fen': initial_fen}), 200

# 重置棋局
@app.route('/reset', methods=['POST'])
def reset():
    stockfish.set_fen_position(initial_fen)  # 重置棋局到初始状态
    return jsonify({'fen': initial_fen}), 200

# 处理走棋
@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    game_id = data.get('game_id')
    user_move = data.get('user_move')

    if not game_id or not user_move:
        return jsonify({'message': '游戏ID和用户走棋不能为空'}), 400

    game = games_collection.find_one({'_id': ObjectId(game_id)})
    if not game:
        return jsonify({'message': '游戏不存在'}), 400

    # 处理用户的走棋
    stockfish.set_fen_position(game['fen_positions'][-1])
    valid_move = stockfish.is_move_correct(user_move)

    if not valid_move:
        return jsonify({'message': '无效的走棋'}), 400

    stockfish.make_moves_from_current_position([user_move])
    new_fen = stockfish.get_fen_position()
    board = chess.Board(fen=new_fen)

    # 更新游戏记录
    games_collection.update_one(
        {'_id': ObjectId(game_id)},
        {
            '$push': {
                'moves': {'player': 'white', 'move': user_move},
                'fen_positions': new_fen
            }
        }
    )

    # 检查游戏是否结束
    if board.is_game_over():
        result = board.result()
        end_time = datetime.utcnow()
        games_collection.update_one(
            {'_id': ObjectId(game_id)},
            {
                '$set': {
                    'result': result,
                    'end_time': end_time
                }
            }
        )
        return jsonify({'message': '游戏结束', 'result': result}), 200

    # 获取AI的最佳走棋
    ai_move = stockfish.get_best_move()
    stockfish.make_moves_from_current_position([ai_move])
    ai_fen = stockfish.get_fen_position()
    board = chess.Board(fen=ai_fen)
    
    # 更新游戏记录
    games_collection.update_one(
        {'_id': ObjectId(game_id)},
        {
            '$push': {
                'moves': {'player': 'black', 'move': ai_move},
                'fen_positions': ai_fen
            }
        }
    )

    # 检查游戏是否结束
    if board.is_game_over():
        result = board.result()
        end_time = datetime.utcnow()
        games_collection.update_one(
            {'_id': ObjectId(game_id)},
            {
                '$set': {
                    'result': result,
                    'end_time': end_time
                }
            }
        )
        return jsonify({'ai_move': ai_move, 'fen': ai_fen, 'message': '游戏结束', 'result': result}), 200

    return jsonify({'ai_move': ai_move, 'fen': ai_fen}), 200

# 获取用户的游戏历史
@app.route('/game_history', methods=['GET'])
@token_required
def game_history(current_user):
    user_id = str(current_user['_id'])
    
    games = games_collection.find({'user_id': ObjectId(user_id)}).sort('start_time', -1)
    game_list = []
    for game in games:
        game_list.append({
            'game_id': str(game['_id']),
            'start_time': game['start_time'],
            'end_time': game.get('end_time'),
            'result': game.get('result'),
            'moves': game['moves']
        })
    
    return jsonify({'games': game_list}), 200

# 获取单个游戏的详细信息
@app.route('/game/<game_id>', methods=['GET'])
@token_required
def get_game(current_user, game_id):
    try:
        game = games_collection.find_one({'_id': ObjectId(game_id), 'user_id': ObjectId(current_user['_id'])})
        if not game:
            return jsonify({'message': '游戏不存在或无权限访问'}), 404
        
        game_details = {
            'game_id': str(game['_id']),
            'user_id': str(game['user_id']),
            'start_time': game['start_time'],
            'end_time': game.get('end_time'),
            'result': game.get('result'),
            'moves': game['moves'],
            'fen_positions': game.get('fen_positions', [])
        }

        return jsonify({'game': game_details}), 200
    except Exception as e:
        return jsonify({'message': '发生错误', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)