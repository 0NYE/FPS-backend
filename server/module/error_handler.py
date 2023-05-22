from flask import Response, make_response, jsonify, json

# 에러 코드와 메시지 전달
def errer_message(message):
    json_dic = json.dumps({
        "code" : 400,
        "message" : message
    })
    result = Response(json_dic, mimetype = "application/json", status = 400)
    return make_response(result)

# 성공 시 메시지 전달
def success_message(message):
    json_dic = {
        "code" : 200,
        "message" : message
    }
    return jsonify(json_dic)