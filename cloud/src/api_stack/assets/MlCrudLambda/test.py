import os
import json
os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
os.environ["USER_POOL_ID"] = "eu-west-1_ssxv6p6Jz"
from lambda_function import handler


additional_super_admin_keys={'requestContext': {'resourceId': 'gytijo', 'authorizer': {'claims': {'sub': '5b1d77aa-d6f7-4ad1-952e-afb7fb6255e5', 'email_verified': 'true', 'custom:organization_id': '00000000-0000-0000-0000-000000000001', 'iss': 'https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_ssxv6p6Jz', 'cognito:username': '5b1d77aa-d6f7-4ad1-952e-afb7fb6255e5', 'origin_jti': '7fc13a9f-1318-4834-a57a-2aa2ebe8818a', 'aud': '6dp28n7cgk62k7kb6chns4lg18', 'event_id': 'efb4010a-3005-4d82-9ad8-f1ee2d0eabe4', 'token_use': 'id', 'custom:organization_type': 'super_admin', 'auth_time': '1713721781', 'exp': 'Mon Apr 22 05:49:41 UTC 2024', 'custom:user_type': 'admin', 'iat': 'Sun Apr 21 17:49:41 UTC 2024', 'jti': '6f39f124-1c63-4f86-960e-d42f66631591', 'email': 'mfahadm8+superadmin@gmail.com', 'custom:organization_name': 'Customer 1 - DEV'}}, 'resourcePath': '/admin/{proxy+}', 'extendedRequestId': 'Wlm0oG8cjoEEOXA=', 'requestTime': '21/Apr/2024:17:49:42 +0000', 'path': '/dev/admin/get_organizations', 'accountId': '951882055661', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': '7ro3yngu37', 'requestTimeEpoch': 1713721782992, 'requestId': '15734736-5dd6-4564-8ab4-2d270639a55c', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '122.129.87.234', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', 'user': None}, 'domainName': '7ro3yngu37.execute-api.eu-west-1.amazonaws.com', 'deploymentId': 'p0iwbb', 'apiId': '7ro3yngu37'},  'isBase64Encoded': False}
additional_contractor_keys={'requestContext': {'resourceId': 'gytijo', 'authorizer': {'claims': {'sub': '5b1d77aa-d6f7-4ad1-952e-afb7fb6255e5', 'email_verified': 'true', 'custom:organization_id': 'id8fd1519a39495', 'iss': 'https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_ssxv6p6Jz', 'cognito:username': '5b1d77aa-d6f7-4ad1-952e-afb7fb6255e5', 'origin_jti': '7fc13a9f-1318-4834-a57a-2aa2ebe8818a', 'aud': '6dp28n7cgk62k7kb6chns4lg18', 'event_id': 'efb4010a-3005-4d82-9ad8-f1ee2d0eabe4', 'token_use': 'id', 'custom:organization_type': 'contractor', 'auth_time': '1713721781', 'exp': 'Mon Apr 22 05:49:41 UTC 2024', 'custom:user_type': 'admin', 'iat': 'Sun Apr 21 17:49:41 UTC 2024', 'jti': '6f39f124-1c63-4f86-960e-d42f66631591', 'email': 'mfahadm8+superadmin@gmail.com', 'custom:organization_name': 'Customer 1 - DEV'}}, 'resourcePath': '/admin/{proxy+}',  'extendedRequestId': 'Wlm0oG8cjoEEOXA=', 'requestTime': '21/Apr/2024:17:49:42 +0000', 'path': '/dev/admin/get_organizations', 'accountId': '951882055661', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': '7ro3yngu37', 'requestTimeEpoch': 1713721782992, 'requestId': '15734736-5dd6-4564-8ab4-2d270639a55c', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '122.129.87.234', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', 'user': None}, 'domainName': '7ro3yngu37.execute-api.eu-west-1.amazonaws.com', 'deploymentId': 'p0iwbb', 'apiId': '7ro3yngu37'}, 'isBase64Encoded': False}
additional_customer_keys={ 'requestContext': {'resourceId': 'gytijo', 'authorizer': {'claims': {'sub': '5b1d77aa-d6f7-4ad1-952e-afb7fb6255e5', 'email_verified': 'true', 'custom:organization_id': 'id9b67e355890e5', 'iss': 'https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_ssxv6p6Jz', 'cognito:username': '5b1d77aa-d6f7-4ad1-952e-afb7fb6255e5', 'origin_jti': '7fc13a9f-1318-4834-a57a-2aa2ebe8818a', 'aud': '6dp28n7cgk62k7kb6chns4lg18', 'event_id': 'efb4010a-3005-4d82-9ad8-f1ee2d0eabe4', 'token_use': 'id', 'custom:organization_type': 'customer', 'auth_time': '1713721781', 'exp': 'Mon Apr 22 05:49:41 UTC 2024', 'custom:user_type': 'admin', 'iat': 'Sun Apr 21 17:49:41 UTC 2024', 'jti': '6f39f124-1c63-4f86-960e-d42f66631591', 'email': 'mfahadm8+superadmin@gmail.com', 'custom:organization_name': 'Customer 1 - DEV'}}, 'resourcePath': '/admin/{proxy+}','extendedRequestId': 'Wlm0oG8cjoEEOXA=', 'requestTime': '21/Apr/2024:17:49:42 +0000', 'path': '/dev/admin/get_organizations', 'accountId': '951882055661', 'protocol': 'HTTP/1.1', 'stage': 'dev', 'domainPrefix': '7ro3yngu37', 'requestTimeEpoch': 1713721782992, 'requestId': '15734736-5dd6-4564-8ab4-2d270639a55c', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '122.129.87.234', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36', 'user': None}, 'domainName': '7ro3yngu37.execute-api.eu-west-1.amazonaws.com', 'deploymentId': 'p0iwbb', 'apiId': '7ro3yngu37'}, 'isBase64Encoded': False}



event_add_user = {
    "httpMethod": "POST",
    "path": "/admin/add_user",
    "body": '{"user_email": "sikiwo5903@hisotyr.com", "user_type":"admin", "name":"Admin"}',
}



event_update_user = {
    "httpMethod": "POST",
    "path": "/admin/update_user",
    "body": json.dumps({
    "user_email": "mfahadm8@gmail.com",
    "name": "Muhammad Fahad Mustafa",
})
}

event_remove_user= {
    "httpMethod": "POST",
    "path": "/admin/remove_user",
    "body": '{"user_email": "mfahadm8@gmail.com"}',
}


event_enable_user = {
     "httpMethod": "GET",
    "path": "/admin/enable_user",
    "queryStringParameters": {
    "user_email": "mfahadm8@gmail.com"
    }
}

event_disable_user = {
     "httpMethod": "GET",
    "path": "/admin/disable_user",
    "queryStringParameters": {
    "user_email": "mfahadm8@gmail.com"
    }
}

event_get_user = {
     "httpMethod": "GET",
    "path": "/admin/get_user",
    "queryStringParameters": {
        "user_email": "ashish@crocsocial.com"
    }
}

event_get_users = {
     "httpMethod": "GET",
    "path": "/admin/get_users"
}

event_get_profile_pic_upload_link = {
    "httpMethod": "GET",
    "path": "/admin/get_profile_pic_upload_link",
    "queryStringParameters": {
        "file_name": "portmansquarefront.jpg"
    }
}

event_get_profile_img_link = {
    "httpMethod": "GET",
    "path": "/admin/get_profile_img_link",
    "queryStringParameters": {
        "s3_uri": "s3://aquacontrol-blobs-dev/public/images/00000000-0000-0000-0000-000000000000/2220d94c-9ef1-4f77-a6ea-7c0090d413a6/Screenshot%202023-08-29%20at%202.19.19%20AM.png"
    }
}


event_get_user = {'path': '/admin/get_user', 'httpMethod': 'GET',"queryStringParameters":None}
event_get_organizations = {'path': '/admin/get_organizations', 'httpMethod': 'GET',"queryStringParameters":None}

event_update_plant = {
"httpMethod": "POST",
"path": "/admin/update_plant",
"body": "{\"plant_id\": \"p123\", \"name_of_facility\": \"Water Facility One\", \"brand_id\": \"b001\", \"brand_name\": \"AquaPure\", \"gps_coordinates\": \"37.7749,-122.4194\", \"depth_intake\": 200, \"mail_contact\": \"contact@aquapure.com\", \"model\": \"AquaMax2000\", \"expected_capacity\": 5000, \"depth_from_surface_to_bottom\": 300, \"intake__distance_from_land\": 150}",
  
}

event_get_brand_plants = {'path': '/admin/get_brand_plants', 'httpMethod': 'GET',"queryStringParameters":None}

event_get_plant = {'path': '/admin/get_plant', 'httpMethod': 'GET',"queryStringParameters":{
    "plant_id":"p123"
}}


event = event_get_plant
event.update(additional_customer_keys)
print(handler(event, {}))
