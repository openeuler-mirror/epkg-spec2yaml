#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import datetime
import os
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.generation.spec_file import CreateSPEC
from openEulerTransition.actions.generation.yaml_file import CreateYAML
from openEulerTransition.configure.common import TransitionAPI
from flask import Flask
from flask_restful import fields, marshal_with, Resource, Api, reqparse

app = Flask(__name__)
app.config['DEBUG'] = True
parser = reqparse.RequestParser()
api = Api(app)

resource_fields = {
    'status':   fields.String,
    'result':    fields.Boolean
}


class TodoConvert(object):
    def __init__(self, status, result):
        self.status = status
        self.result = result


class Convert(Resource):
    @marshal_with(resource_fields)
    def get(self):
        parser.add_argument("method", help="[method] cannot be converted")  # Python3中参数的默认类型为str
        parser.add_argument("parameters", type=dict, help="[parameters] cannot be converted")
        parser.parse_args()
        return {"status": "success", "result": True}

    @marshal_with(resource_fields)
    def post(self):
        parser.add_argument("option", help="[method] cannot be converted", location=['form'])  # Python3中参数的默认类型为str
        parser.add_argument("file", type=str, help="[parameters] cannot be converted", location=['form'])
        data = parser.parse_args()
        option = data.get("option")
        file_path = data.get("file")
        conf_path = data.get("conf")
        shell_path = data.get("shell")
        python_path = data.get("python")
        target_type = data.get("target") if "target" in data else "spec"
        result = os.path.exists(file_path)
        if not result:
            return TodoConvert(status="fail", result=False)
        start_time = datetime.datetime.now()
        if option == "--parse" or option == "parse":
            if target_type == "spec":
                CreateSPEC(file_path, conf_path=conf_path, shell_path=shell_path, python_path=python_path).transition()
            else:
                logger.warn("cannot parse to this type,only spec")
        elif option == "--trans" or option == "trans":
            CreateYAML(file_path).transition()
        logger.info("Open Euler Build System framework start......")

        end_time = datetime.datetime.now()
        run_time = (end_time - start_time).seconds
        print('running time is: {}, seconds'.format(run_time))
        return TodoConvert(status="success", result=True)


api.add_resource(Convert, '/api/convert')


if __name__ == "__main__":
    app.run(host=TransitionAPI, port=8080)
