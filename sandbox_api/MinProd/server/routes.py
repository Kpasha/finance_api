from functools import wraps
from flask import Response, request, abort, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_autodoc.autodoc import Autodoc

from MinProd import app
from MinProd.server.controllers.data import DataController
from MinProd.server.controllers.ping import PingController
from MinProd.server.controllers.loan import LoanController
from MinProd.server.controllers.error import ErrorController 
from MinProd.server.controllers.security import SecurityController


# global variables
auth = HTTPBasicAuth()
auto = Autodoc(app)


'''********************************************************************
Public Routes
********************************************************************'''
@app.route('/', methods=['GET'])
@auto.doc(groups=['public'])
def ping():
    '''Route to ping server'''
    try: 
        return PingController.get_ping_json()
    except Exception as e:
        abort(ErrorController.handle_errors(e))


# Loan routes ---------------------------------------------------------
@app.route('/loan/monthlypayment', methods=['GET'])
@auto.doc(groups=['public'])
def monthly_payment():
    '''
    Caclulcates the monthly payment for a loan

    Required payload is json stucture like the following:
    { "loan_terms":
        {
            "apr":0.04
            , "years":5
            , "amount":10000
        }
    }
    '''
    try:
        loan_terms = request.json.get('loan_terms')
        return LoanController.get_monthly_payment(loan_terms)
    except Exception as e:
        abort(ErrorController.handle_errors(e))


@app.route('/loan/totalinterest', methods=['GET'])
@auto.doc(groups=['public'])
def total_interest():
    '''
    Caclulcates the total interest for a loan

    Required payload is json stucture like the following:
    { "loan_terms":
        {
            "apr":0.04
            , "years":5
            , "amount":10000
        }
    }
    '''
    try:
        loan_terms = request.json.get('loan_terms')
        return LoanController.get_total_interest(loan_terms)
    except Exception as e:
        abort(ErrorController.handle_errors(e))


@app.route('/loan/totalcost', methods=['GET'])
@auto.doc(groups=['public'])
def total_cost():
    '''
    Caclulcates the total cost, principle and interest, for a loan

    Required payload is json stucture like the following:
    { "loan_terms":
        {
            "apr":0.04
            , "years":5
            , "amount":10000
        }
    }
    '''
    try:
        loan_terms = request.json.get('loan_terms')
        return LoanController.get_total_cost(loan_terms)
    except Exception as e:
        abort(ErrorController.handle_errors(e))


@app.route('/loan/totalremaining', methods=['GET'])
@auto.doc(groups=['public'])
def total_remaining():
    '''
    Caclulcates the total cost, principle and interest, for a loan

    Required payload is json stucture like the following:
    { "loan_terms":
        {
            "apr":0.04
            , "years":5
            , "amount":10000
            , "current_period":3
        }
    }
    '''
    #try:
    loan_terms = request.json.get('loan_terms')
    return LoanController.get_total_remaining(loan_terms)
    #except Exception as e:
    #    abort(ErrorController.handle_errors(e))


'''********************************************************************
Documention Routes
********************************************************************'''
@app.route('/help')
@auto.doc(groups=['public'])
def doc_public():
    '''Returns all public routes and descriptions'''
    try:   
        return auto.html('public')
    except Exception as e:
        abort(ErrorController.handle_errors(e))


@app.route('/help/private')
@auto.doc(groups=['private'])
@auth.login_required
def doc_private():
    '''Returns all private routes and descriptions'''
    try:
        return auto.html('private')
    except Exception as e:
        abort(ErrorController.handle_errors(e))


# return columns for a specific table
@app.route('/<string:table_name>/columns', methods=['GET'])
@auto.doc(groups=['private'])
@auth.login_required
def get_typesof_columns(table_name):
    '''Returns data types for any table available via the API
    Current tables available: User'''
    try:
        return Response(DataController.get_typesof_columns(table_name), 
            mimetype='application/json')
    except Exception as e:
        abort(ErrorController.handle_errors(e))


'''********************************************************************
Authentication and User MGMT
********************************************************************'''
# get token
@app.route('/token/<string:username>/<string:password>', methods=['GET'])
@auto.doc(groups=['public'])
def generate_auth_token(username, password):
    '''Route to generate a token
    
    Returns the token that must be sent in the header as the username
    with 'unused' as the password. All routes that contain data 
    require the token.
    
    Token expires in 20 minutes of issuance
    
    Example:
    curl -i -X GET -H "Content-Type: application/json" 
    https://localhost/token/username/password
    '''
    try:
        return SecurityController.generate_auth_token(username, password)
    except Exception as e:
        abort(ErrorController.handle_errors(e))


# auth with token
@auth.verify_password
def verify_token(token, password):
    try:
        if not token or not SecurityController.auth_user(token):
            return False
        return True 
    except Exception as e:
        abort(ErrorController.handle_errors(e))

'''
@app.route('/user/new', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    dc = DataController()
    return dc.new_user(username, password), 201
'''