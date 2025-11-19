from flask import jsonify


def success_response(data=None, message='success', code=200):
    """成功响应"""
    response = {
        'code': code,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), code


def error_response(message='error', code=400, errors=None):
    """错误响应"""
    response = {
        'code': code,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), code


def paginate_response(items, total, page, page_size, message='success'):
    """分页响应"""
    return success_response(
        data={
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        },
        message=message
    )

