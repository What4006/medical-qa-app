import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from ..models.user_model import DoctorModel
from ..services import auth_service, user_service
from ..schemas.auth_schema import LoginSchema, PatientRegisterSchema, DoctorRegisterSchema, UserDetailSchema
# 创建蓝图
auth_bp = Blueprint('auth_api', __name__, url_prefix='/api/auth')

@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    """患者注册"""
    try:
        data = PatientRegisterSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"code": 400, "msg": err.messages}), 400
    
    user, msg = auth_service.register_patient(data)
    
    if not user:
        return jsonify({"code": 400, "msg": msg}), 400
        
    return jsonify({"code": 200, "msg": msg}), 200

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register/doctor', methods=['POST'])
def register_doctor():
    """医生注册，处理 multipart/form-data 和文件上传"""
    # 1. 检查请求中是否包含文件部分
    if 'certificate' not in request.files:
        return jsonify({"code": 400, "msg": "请求中未包含 certificate 文件部分"}), 400

    file = request.files['certificate']

    # 2. 检查用户是否选择了文件
    if file.filename == '':
        return jsonify({"code": 400, "msg": "未选择任何文件"}), 400

    # 3. 使用 Schema 校验表单中的文本数据
    try:
        # multipart/form-data 的文本数据在 request.form 中
        form_data = DoctorRegisterSchema().load(request.form)
    except ValidationError as err:
        return jsonify({"code": 400, "msg": err.messages}), 400
    
    # 4. 如果文件存在且类型合法，则保存它
    if file and allowed_file(file.filename):
        # 使用 secure_filename 防止恶意文件名
        filename = secure_filename(file.filename)
        
        # 定义并创建上传目录，例如: backend/uploads/certificates/
        upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'certificates')
        os.makedirs(upload_folder, exist_ok=True)
        
        # 拼接文件的完整保存路径
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 准备存入数据库的相对路径 (跨平台兼容)
        db_file_path = os.path.join('uploads', 'certificates', filename).replace('\\', '/')

        # 5. 调用 service 层，传入文本数据和文件路径
        user, msg = auth_service.register_doctor(form_data, db_file_path)

        if not user:
            # 如果 service 层返回错误 (例如用户已存在)，则返回错误信息
            return jsonify({"code": 400, "msg": msg}), 400

        # 全部成功
        return jsonify({"code": 200, "msg": msg}), 200
    else:
        return jsonify({"code": 400, "msg": "文件类型不合法，仅允许 png, jpg, jpeg"}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as err:
        return jsonify({"code": 401, "msg": "无效的输入"}), 401

    user = auth_service.login_user(data)
    
    if not user:
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401
    
    # 创建 JWT Token，将用户ID作为身份标识
    access_token = create_access_token(identity=user.id)
    
    response_data = {
        "code": 200,
        "msg": "登录成功",
        "data": {
            "token": access_token,
            "user": {
                "user_id": user.id,
                "phone": user.username,
                "user_type": data['user_type']
            }
        }
    }
    return jsonify(response_data), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取当前登录用户的详细信息"""
    current_user_id = get_jwt_identity()
    user = user_service.get_user_by_id(current_user_id)

    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    exclude_fields = []
    if user.role == 'patient':
        exclude_fields.append('doctor_info')
    elif user.role == 'doctor':
        exclude_fields.append('patient_info')

    # 1. 在创建实例时传入 exclude (第一次失败的教训)
    schema = UserDetailSchema(exclude=tuple(exclude_fields))
    
    # 2. 直接获取 dump() 的结果，不加 .data (第二次失败的教训)
    result = schema.dump(user)

    return jsonify({"code": 200, "data": result}), 200