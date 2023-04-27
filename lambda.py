import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    # TODO implement
    intent = event['currentIntent']['name']
    if intent == 'StartingIntent':
        return {
            'dialogAction': {
                "type": "ElicitIntent",
                'message': {
                    'contentType': 'PlainText',
                    'content': 'hi, how may I help you?'
                }
            }
        }
        
    elif intent == 'EndingIntent':
        return {
            'dialogAction': {
                "type": "ElicitIntent",
                'message': {
                    'contentType': 'PlainText',
                    'content': 'you are welcome'
                }
            }
        }
        
    elif intent == 'ProductDetailsIntent':
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('pdp')
        #selection is 'product id' or 'keyword' as defined in bot
        selection = event['currentIntent']['slots']['Selection']
        #selectiontwo is the actual product id or keyword as stated in selection
        selectiontwo = event['currentIntent']['slots']['SelectionTwo']
        #selectionthree is what we need to search, it can be name, price, or details
        selectionthree = event['currentIntent']['slots']['SelectionThree']
        
        if selection == 'productid' or selection == 'id':
            selectiontwo = selectiontwo.upper()
            #searching the dynamodb table for the input product id
            response = table.query(
                    KeyConditionExpression=Key('productcode').eq(selectiontwo)
                    )
            if len(response['Items']) == 0:
                out = 'no item found'
            else:
                product = response['Items'][0]
                if selectionthree == 'productprice' or selectionthree == 'price':
                    if product['stock'] == 'Yes':
                        out = 'The product price is: '+ product['price']
                    else:
                        out = 'Sorry, the product is: '+ product['price']
                elif selectionthree == 'productdetails' or selectionthree == 'details':
                    out = 'The product details are: ' + product['detail']
                elif selectionthree == 'productname' or selectionthree == 'name':
                    out = 'The product name is: ' + product['name']
                    
        elif selection == 'keyword':
            #searching the dynamodb table for the input keyword
            response = table.scan(
                FilterExpression=Attr('name').contains(selectiontwo)
                )
            if len(response['Items']) == 0:
                out = 'no item found'
            else:
                no_items = len(response['Items'])
                if selectionthree == 'productprice' or selectionthree == 'price':
                    out = 'The products price are: '
                    for item in range(no_items):
                        product = response['Items'][item]
                        pcount = 0
                        if product['stock'] == 'Yes':
                            pcount = pcount+1
                            out = out + product['price'] + ', '
                        else:
                            if pcount== 0:
                                out = 'All items with given keyword are out of stock'
                elif selectionthree == 'productdetails' or selectionthree == 'details':
                    out = 'The product ids are: '
                    for item in range(no_items):
                        product = response['Items'][item]
                        out = out + product['productcode'] + ', '
                    out = out + ' Please re-search using one of these product ids.'
                elif selectionthree == 'productname' or selectionthree == 'name':
                    out = 'The product names are: '
                    for item in range(no_items):
                        product = response['Items'][item]
                        out = out + product['name'] + ', '
                        
        return {
                'dialogAction': {
                    "type": "ElicitIntent",
                    'message': {
                        'contentType': 'PlainText',
                        'content': out
                    }
                }
            }