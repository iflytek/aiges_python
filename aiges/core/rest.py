#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: rest
@time: 2022/08/06
@contact: ybyang7@iflytek.com
@site:  
@software: PyCharm 

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛ 
"""

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

import logging
from flask import Flask, Response, request, send_from_directory
from flask_cors import CORS
from aiges.utils.flask_utils import *


logger = logging.getLogger(__name__)


def get_rest_microservice(user_model, seldon_metrics):
    app = Flask(__name__, static_url_path="")
    CORS(app)

    _set_flask_app_configs(app)

    # dict representing the validated model metadata
    # None value will represent a validation error
    metadata_data = seldon_core.seldon_methods.init_metadata(user_model)

    if hasattr(user_model, "model_error_handler"):
        logger.info("Registering the custom error handler...")
        app.register_blueprint(user_model.model_error_handler)

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        error = SeldonMicroserviceException(
            message=str(e), status_code=500, reason="MICROSERVICE_INTERNAL_ERROR"
        )
        response = jsonify(error.to_dict())
        logger.error("%s", error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(SeldonMicroserviceException)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        logger.error("%s", error.to_dict())
        response.status_code = error.status_code
        return response

    @app.route("/seldon.json", methods=["GET"])
    def openAPI():
        return send_from_directory("", "openapi/seldon.json")

    @app.route("/predict", methods=["GET", "POST"])
    @app.route("/api/v1.0/predictions", methods=["POST"])
    @app.route("/api/v0.1/predictions", methods=["POST"])
    def Predict():
        requestJson = get_request(skip_decoding=PAYLOAD_PASSTHROUGH)
        logger.debug("REST Request: %s", request)
        response = seldon_core.seldon_methods.predict(
            user_model, requestJson, seldon_metrics
        )

        json_response = jsonify(response, skip_encoding=PAYLOAD_PASSTHROUGH)
        if (
            isinstance(response, dict)
            and "status" in response
            and "code" in response["status"]
        ):
            json_response.status_code = response["status"]["code"]

        logger.debug("REST Response: %s", response)
        return json_response

    @app.route("/send-feedback", methods=["GET", "POST"])
    @app.route("/api/v1.0/feedback", methods=["POST"])
    @app.route("/api/v0.1/feedback", methods=["POST"])
    def SendFeedback():
        requestJson = get_request()
        logger.debug("REST Request: %s", request)
        requestProto = json_to_feedback(requestJson)
        logger.debug("Proto Request: %s", requestProto)
        responseProto = seldon_core.seldon_methods.send_feedback(
            user_model, requestProto, PRED_UNIT_ID, seldon_metrics
        )
        jsonDict = seldon_message_to_json(responseProto)
        return jsonify(jsonDict)

    @app.route("/transform-input", methods=["GET", "POST"])
    def TransformInput():
        requestJson = get_request()
        logger.debug("REST Request: %s", request)
        response = seldon_core.seldon_methods.transform_input(
            user_model, requestJson, seldon_metrics
        )
        logger.debug("REST Response: %s", response)
        return jsonify(response)

    @app.route("/transform-output", methods=["GET", "POST"])
    def TransformOutput():
        requestJson = get_request()
        logger.debug("REST Request: %s", request)
        response = seldon_core.seldon_methods.transform_output(
            user_model, requestJson, seldon_metrics
        )
        logger.debug("REST Response: %s", response)
        return jsonify(response)

    @app.route("/route", methods=["GET", "POST"])
    def Route():
        requestJson = get_request()
        logger.debug("REST Request: %s", request)
        response = seldon_core.seldon_methods.route(
            user_model, requestJson, seldon_metrics
        )
        logger.debug("REST Response: %s", response)
        return jsonify(response)

    @app.route("/aggregate", methods=["GET", "POST"])
    def Aggregate():
        requestJson = get_request()
        logger.debug("REST Request: %s", request)
        response = seldon_core.seldon_methods.aggregate(
            user_model, requestJson, seldon_metrics
        )
        logger.debug("REST Response: %s", response)
        return jsonify(response)

    @app.route("/health/ping", methods=["GET"])
    def HealthPing():
        """
        Lightweight endpoint to check the liveness of the REST endpoint
        """
        return "pong"

    @app.route("/health/status", methods=["GET"])
    @app.route("/api/v1.0/health/status", methods=["GET"])
    def HealthStatus():
        logger.debug("REST Health Status Request")
        response = seldon_core.seldon_methods.health_status(user_model, seldon_metrics)
        logger.debug("REST Health Status Response: %s", response)
        return jsonify(response)

    @app.route("/metadata", methods=["GET"])
    @app.route("/api/v1.0/metadata", methods=["GET"])
    def Metadata():
        if metadata_data is None:
            # None value represents validation error in current implementation
            # if user_model would not define init_metadata than metadata_data
            # would just contain a default values
            raise SeldonMicroserviceException(
                "Model metadata unavailable",
                status_code=500,
                reason="MICROSERVICE_BAD_METADATA",
            )
        logger.debug("REST Metadata Request")
        logger.debug("REST Metadata Response: %s", metadata_data)
        return jsonify(metadata_data)

    return app


def _set_flask_app_configs(app):
    """
    Set the configs for the flask app based on environment variables
    See https://flask.palletsprojects.com/config/#builtin-configuration-values
    :param app:
    :return:
    """
    FLASK_CONFIG_IDENTIFIER = "FLASK_"
    FLASK_CONFIGS_ALLOWED = [
        "DEBUG",
        "EXPLAIN_TEMPLATE_LOADING",
        "JSONIFY_PRETTYPRINT_REGULAR",
        "JSON_SORT_KEYS",
        "PROPAGATE_EXCEPTIONS",
        "PRESERVE_CONTEXT_ON_EXCEPTION",
        "SESSION_COOKIE_HTTPONLY",
        "SESSION_COOKIE_SECURE",
        "SESSION_REFRESH_EACH_REQUEST",
        "TEMPLATES_AUTO_RELOAD",
        "TESTING",
        "TRAP_HTTP_EXCEPTIONS",
        "TRAP_BAD_REQUEST_ERRORS",
        "USE_X_SENDFILE",
    ]

    for flask_config in FLASK_CONFIGS_ALLOWED:
        flask_config_value = getenv_as_bool(
            f"{FLASK_CONFIG_IDENTIFIER}{flask_config}", default=None
        )
        if flask_config_value is None:
            continue
        app.config[flask_config] = flask_config_value
    logger.info(f"App Config:  {app.config}")

