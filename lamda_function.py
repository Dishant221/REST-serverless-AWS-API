from ast import Expression
from ctypes import cdll
from distutils.command.build import build
from distutils.log import info
from email import header
import imp
from itertools import product
from math import prod
from unittest import result
from urllib import response
import boto3
import json
import logging
from custom_encoder import CustonEncoder
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'

healthPath = '/health'
productPath = '/product'
productsPath = '/products'


def lamda_fucntion(event, context):
    logger.info(event)
    httpMethod = event['httpMethood']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response= buildResponse(200)
    elif httpMethod == getMethod and path == productPath:
        response = getProduct(event['queryStringParameters']['productId'])
    elif httpMethod == getMethod and path == productsPath:
        response =  getProducts()
    elif httpMethod == postMethod and path == productPath:
        response = saveProduct(json.loads(event['body']))
    elif httpMethod == patchMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = modifyProduct(requestBody['productId'],requestBody['updateKey'],requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == productPath:
        requestBody = json.loads(event['body'])
        response = deleteProduct(requestBody['productId'])


# get product

def getProduct(productId):
    try:
        response = table.get_item( key = { 'productId ': productId })

        if 'Item' in response :
            return buildResponse(200, response)
        else:
            return buildResponse(404 , {'message':'ProductId  %s not found '})
    except:
        logger.exception('Do your coustom error handling here , i just gonna logout here')


# get all products

def getProducts():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluateKey' in response:
            response = table.scan(ExclusiveStartKey = response ['LastEvaluateKey'])
            result.extend(response['Items'])
        body = {'products':result}

        return  buildResponse(200,body)

    except:
        logger.exception('Do your coustom error handling here , i just gonna logout here')

# save Product


def saveProduct(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'operation':'SAVE',
            'message':'success',
            'Item':requestBody
        }
        return buildResponse(200,body)
    except:
          logger.exception('Do your coustom error handling here , i just gonna logout here')

# modify product

def modifyProduct(productId,updateKey,updateValue):
    try:
        response = table.upadte_item(
            key ={
                'productId': productId
            },
            UpdateExpression = 'set %s = :value '% updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues = 'UPDATED_NEW'

        )

        body ={
            'operation':'UPADTE',
            'message': 'success',
            'UpdatedAttrebutes': response
        }
        return buildResponse(200,body)
    except:
        logger.exception('Do your coustom error handling here , i just gonna logout here')



# delete values

def deleteProduct(productId):
    try:
        response=table.delete_item(
            key={
                'productId':productId
            },
            ReturnValues='ALL_OLD'
        )
        body={
            'operation':'delete',
            'message':'success',
            'deletedItem':response
        }
        return buildResponse(200,body)
    except:
            logger.exception('Do your coustom error handling here , i just gonna logout here')






def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'header': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    if body is not None:
        response['body']= json.dumps(body, cls= CustonEncoder)
    

    return response
























    