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

# 에러 코드와 메시지 전달
def errer_message_opencv(message, width1, height1, width2, height2):
    json_dic = json.dumps({
        "code" : 400,
        "message" : message,
        "problem_width" : width1,
        "problem_height" : height1,
        "submit_width" : width2,
        "submit_height" : height2
    })
    result = Response(json_dic, mimetype = "application/json", status = 400)
    return make_response(result)
