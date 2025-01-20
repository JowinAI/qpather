# from fastapi import APIRouter, FastAPI,Request, Form, File, UploadFile,HTTPException,Header,Depends,status
# #from mangum import Mangum#
# #from dotenv import load_dotenv
# import boto3
# #from boto3.dynamodb.conditions import Key
# from openai import OpenAI,AssistantEventHandler
# import time
# import os
# import uuid
# from fastapi.responses import StreamingResponse
# import json
# from openai import AssistantEventHandler
# from typing_extensions import override
# from fastapi.middleware.cors import CORSMiddleware
# from boto3.dynamodb.conditions import Attr
# import io
# from PyPDF2 import PdfReader, PdfWriter
# import shutil
# from typing import Generator
# import asyncio
# import jwt
# import requests
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jwt.algorithms import RSAAlgorithm
# from jwt import ExpiredSignatureError, InvalidTokenError



# #load_dotenv()

# router = APIRouter()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all methods
#     allow_headers=["*"],  # Allow all headers
# )

# api_key = os.getenv('API_KEY')
# default_assistant_id = os.getenv('ASSISTANT_ID')
# client = OpenAI(api_key=api_key)
# dynamodb_table_name = os.getenv('DYNAMODB_TABLE_NAME')
# s3_client = boto3.client('s3')
# bucket_name = 'assistantknowledgebase'
# TENANT_NAME = os.getenv('TENANT_NAME')
# POLICY_NAME = os.getenv('POLICY_NAME')
# CLIENT_ID=os.getenv('CLIENT_ID')
# CLIENT_SECRET = os.getenv('CLIENT_SECRET')
# TENANT_ID=os.getenv('TENANT_ID')

# dynamodb = boto3.resource('dynamodb')
# table = dynamodb.Table(dynamodb_table_name)

# def get_assistant_from_dynamodb(id):
#     response = table.query(
#         KeyConditionExpression=Key('Id').eq(id)
#     )
#     print('response:')
#     print(response)
#     first_item = response['Items'][0]
#     return first_item
#     #return response.get('Item')

# def get_assistant_for_user_from_dynamodb(userid):
#     response = table.scan(
#         FilterExpression=Attr('userid').eq(userid)
#     )
#     print('response:')
#     print(response)
#     items = response.get('Items', [])
#     return {'items': items}
    

# def get_max_id_from_dynamodb():
#     response = table.scan(ProjectionExpression='Id')
#     items = response.get('Items', [])
#     if not items:
#         return 0
#     max_id = max(item['Id'] for item in items)
#     print('max_id:')
#     print(max_id)
#     return max_id

# def update_tokens(prompt_token, completion_token, assistant_id,assistant_name):
#     try:
#         response = table.update_item(
#             Key={'Id': assistant_id,'assistant_name': assistant_name},
#             UpdateExpression="ADD total_prompt_token :p, total_completion_token :c",
#             ExpressionAttributeValues={
#                 ':p': prompt_token,
#                 ':c': completion_token
#             },
#             ReturnValues="UPDATED_NEW"
#         )
#         print(f"Tokens updated: {response}")
#         return response
#     except Exception as e:
#         print(f"Error updating tokens: {e}")
#         return None

# def delete_dynamodb_item(id: str,assistant_name: str):
#     try:
#         response = table.delete_item(
#             Key={
#                 'id': id, 'assistant_name': assistant_name
#             }
#         )
#         print(f"Assiatnt deleted : {response}")
#         return response
#     except Exception as e:
#         print(f"Error deleting assiatnt: {e}")
#         return None

# def update_instructions(id, new_instructions,assistant_name,ask_for_contact,mandatory_contact,responses_before_ask,email,phone,address,welcome_message):
#     try:
         
#         response = table.update_item(
#             Key={'Id': id, 'assistant_name': assistant_name},
#             UpdateExpression="set instructions = :i, ask_for_contact = :a, mandatory_contact = :m, responses_before_ask = :r, email = :e, phone = :p, address = :ad, welcome_message = :w",
#             ExpressionAttributeValues={
#                 ':i': new_instructions,
#                 ':a': ask_for_contact,
#                 ':m': mandatory_contact,
#                 ':r': responses_before_ask,
#                 ':e': email,
#                 ':p': phone,
#                 ':ad': address,
#                 ':w': welcome_message
#             },
#             ReturnValues="UPDATED_NEW"
#         )
#         return response
#     except Exception as e:
#         print(f"Error updating instructions: {e}")
#         return None

# def simplify_pdf(input_path, output_path):
#     reader = PdfReader(input_path)
#     writer = PdfWriter()

#     for page in reader.pages:
#         writer.add_page(page)

#     with open(output_path, "wb") as f:
#         writer.write(f)

# def get_jwks(jwks_uri):
#     response = requests.get(jwks_uri)
#     response.raise_for_status()
#     return response.json()

# def get_public_key(token, jwks):
#     headers = jwt.get_unverified_header(token)
#     kid = headers.get("kid")
#     for key in jwks["keys"]:
#         if key["kid"] == kid:
#             return RSAAlgorithm.from_jwk(key)
#     raise Exception("Public key not found.")

# def verify_token(token):
#     return True
#     id_token = token
#     JWKS_URI = f'https://{TENANT_NAME}.b2clogin.com/{TENANT_NAME}.onmicrosoft.com/discovery/v2.0/keys?p={POLICY_NAME}'
#     JWT_ISSUER = f"https://{TENANT_NAME}.b2clogin.com/{TENANT_ID}/v2.0/"
#     jwks = get_jwks(JWKS_URI)
#     public_key = get_public_key(id_token, jwks)
    
#     try:
#         print('Vdecode ended')
#         payload = jwt.decode(
#             id_token,
#             public_key,
#             audience=CLIENT_ID,
#             algorithms=["RS256"],
#             issuer=JWT_ISSUER
#         )
#     except ExpiredSignatureError:
#        raise HTTPException(
#            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired!"
#        )
#     except InvalidTokenError as e:
#         print(e)
#         raise HTTPException(
#            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token claims"
#        )
#     except Exception:
#        raise HTTPException(
#            status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to validate token"
#        )
#     print('decode Ended')
#     print(payload)
#     users_table = dynamodb.Table('users')
#     email = payload.get("emails", [None])[0]
#     response = users_table.scan(
#             FilterExpression=Attr('email').eq(email)
#     )
#     if response['Count'] == 0:
#         return False
#     else:   
#         return True


# @app.post("/query")
# async def query(request: Request,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     data = await request.json()
#     user_query = data.get('query')
#     thread_id = data.get('thread_id')
#     assistant_id = default_assistant_id
#     print(user_query)
#     if thread_id:
#         thread = client.beta.threads.retrieve(thread_id=thread_id)
#         client.beta.threads.messages.create(thread_id=thread_id, role='user', content=user_query)
#     else:
#         thread = client.beta.threads.create(messages=[{'role': 'user', 'content': user_query}])
   
#     run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)# Replace with your method to load the decrypted assitant key
    
#     while run.status != "completed":
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
#         time.sleep(0.5)
    
#     message_response = client.beta.threads.messages.list(thread_id=thread.id)
#     messages = message_response.data
#     latest_message = messages[0]
#     print(latest_message.content[0].text.value)
#     if hasattr(run, 'usage'):
#         prompt_tokens = run.usage.prompt_tokens
#         completion_tokens = run.usage.completion_tokens
#         update_tokens(prompt_tokens, completion_tokens,'f4e40919-c0e2-4d61-8cd7-894e14813d05','EduNavigator')

#     return {'response': latest_message.content[0].text.value, 'thread_id': thread.id}


# @app.post("/query/{id}")
# async def query_with_assistant(id: str, request: Request,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     data = await request.json()
#     user_query = data.get('query')
#     thread_id = data.get('thread_id')
#     print('Id:')
#     print(id)
#     # Fetch assistant from DynamoDB
#     assistant_item = get_assistant_from_dynamodb(id)
#     if not assistant_item:
#         return {'error': 'Assistant not found'}, 404

#     assistant_id = assistant_item.get('assistant_id', default_assistant_id)
#     assistant_name = assistant_item.get('assistant_name')

#     if thread_id:
#         thread = client.beta.threads.retrieve(thread_id=thread_id)
#         client.beta.threads.messages.create(thread_id=thread_id, role='user', content=user_query)
#     else:
#         thread = client.beta.threads.create(messages=[{'role': 'user', 'content': user_query}])
    
#     #run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
#     run = client.beta.threads.runs.create_and_poll(thread_id=thread.id, assistant_id=assistant_id)

#     #while run.status != "completed":
#     #    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
#     #    time.sleep(0.5)
#     messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
#     message_content = messages[0].content[0].text

#     #message_response = client.beta.threads.messages.list(thread_id=thread.id)
#     #messages = message_response.data
#     #latest_message = messages[0]
#     annotations = message_content.annotations
#     for index, annotation in enumerate(annotations):
#          message_content.value = message_content.value.replace(annotation.text, "")
#     print('run:')
#     print(run)

#     if hasattr(run, 'usage'):
#         prompt_tokens = run.usage.prompt_tokens
#         completion_tokens = run.usage.completion_tokens
#         update_tokens(prompt_tokens, completion_tokens, id,assistant_name)
    
#     return {'response': message_content.value, 'thread_id': thread.id}


# # Define the EventHandler class to handle streaming events
# class EventHandler(AssistantEventHandler):
#     def __init__(self):
#         super().__init__()
#         self.text_buffer = []
#         self.finished = False

#     @override
#     def on_text_created(self, text) -> None:
#         self.text_buffer.append(f"\nassistant > {text}")
#         print(f"\nassistant > ", end="", flush=True)

#     @override
#     def on_tool_call_created(self, tool_call):
#         self.text_buffer.append(f"\nassistant > {tool_call.type}\n")
#         print(f"\nassistant > {tool_call.type}\n", flush=True)

#     @override
#     def on_message_done(self, message) -> None:
#         message_content = message.content[0].text
#         annotations = message_content.annotations
        
#         for index, annotation in enumerate(annotations):
#             message_content.value = message_content.value.replace(
#                 annotation.text, ""
#             )
            
#         self.text_buffer.append(message_content.value)
#         print(message_content.value)
#         self.finished = True

#     def get_streamed_data(self) -> Generator[str, None, None]:
#         """Yield the buffered data as a stream."""
#         while self.text_buffer:
#             yield self.text_buffer.pop(0) + "\n"

# @app.post("/query-stream/{id}")
# async def query_stream_with_assistant(id: str, request: Request,authorization: str = Header(...)):

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     data = await request.json()
#     user_query = data.get('query')
#     thread_id = data.get('thread_id')
    
#     # Fetch assistant from DynamoDB
#     assistant_item = get_assistant_from_dynamodb(id)
#     assistant_id = assistant_item.get('assistant_id', default_assistant_id)
#     assistant_name = assistant_item.get('assistant_name')


#     if thread_id:
#         thread = client.beta.threads.retrieve(thread_id=thread_id)
#         client.beta.threads.messages.create(thread_id=thread_id, role='user', content=user_query)
#     else:
#         thread = client.beta.threads.create(messages=[{'role': 'user', 'content': user_query}])

#     event_handler = EventHandler()
#     async def stream_generator():
#         with client.beta.threads.runs.stream(
#             thread_id=thread.id,
#             assistant_id=assistant_id,
#             event_handler=event_handler,
#         ) as stream:
#             while not event_handler.finished:
#                 await asyncio.sleep(0.1)  # Sleep for 100 milliseconds
#                 while event_handler.text_buffer:
#                     yield event_handler.text_buffer.pop(0) + "\n"
        
#     # Return the streaming response
#     return StreamingResponse(stream_generator(), media_type="text/plain")
    
# @app.post("/create_update_assistant")
# async def create_assistant(assistant_name: str = Form(...),
#     instructions: str = Form(...),
#     file: UploadFile = File(None),
#     userid: str = Form(None),
#     id: str = Form(None),
#     ask_for_contact: bool = Form(None),
#     mandatory_contact: bool = Form(None),
#     responses_before_ask: int = Form(None),
#     email: bool = Form(None),
#     phone: bool = Form(None),
#     address: bool = Form(None),
#     welcome_message: str = Form(None),
#     authorization: str = Header(...)):

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")


#     # Save the file to a desired location
#     os.makedirs("/tmp", exist_ok=True)
#     file_paths = []
#     file_streams = []
#     if file:
#         file_path = f"/tmp/{file.filename}"
#         with open(file_path, "wb") as buffer:
#             buffer.write(await file.read())
#         file_paths = [file_path]
#         file_streams = [open(path, "rb") for path in file_paths]
    
#     if not id:
#         personal_assistant=client.beta.assistants.create(
#         name=assistant_name,
#         instructions=instructions,
#         model='gpt-4o-mini',
#         tools=[{"type": "file_search"}]
#         )
#         personal_assistant_id=personal_assistant.id
#         vector_store = client.beta.vector_stores.create(name=assistant_name)
#         vector_store_id=vector_store.id
#         id = str(uuid.uuid4())
#         table.put_item(Item={
#             'Id': id,
#             'assistant_name': assistant_name,
#             'assistant_id': personal_assistant_id,
#             'vector_store_id': vector_store_id,
#             'total_prompt_token': 0,
#             'total_completion_token': 0,
#             'instructions': instructions,
#             'userid': userid if userid is not None else "" ,
#             'ask_for_contact': ask_for_contact if ask_for_contact is not None else False,
#             'mandatory_contact': mandatory_contact if mandatory_contact is not None else False,
#             'responses_before_ask': responses_before_ask if responses_before_ask is not None else 0,
#             'email': email if email is not None else False,
#             'phone': phone if phone is not None else False,
#             'address': address if address is not None else False,
#             'welcome_message': welcome_message if welcome_message is not None else ""

#         })
        
#     else:
#         assistant_item = get_assistant_from_dynamodb(id)
#         personal_assistant_id = assistant_item.get('assistant_id', default_assistant_id)
#         vector_store_id=assistant_item.get('vector_store_id')
#         update_instructions(id, instructions,assistant_name,ask_for_contact,mandatory_contact,responses_before_ask,email,phone,address,welcome_message)

#     if file_streams:
#         file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
#             vector_store_id=vector_store_id, files=file_streams
#             )

#     assistant = client.beta.assistants.update(
#         assistant_id=personal_assistant_id,
#         tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
#         instructions=instructions
#     )
   
#     return {'message': 'Assistant created/Updated successfully', 'assistant_id': personal_assistant_id,'id':id}

# @app.post("/upload_file")
# async def upload_file(    
#     file: UploadFile = File(...),
#     id: str = Form(...),authorization: str = Header(...)):

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")

#     # Save the file to a desired location
#     #os.makedirs("/tmp", exist_ok=True)
#     file_paths = []
#     file_streams = []
#     if file:
#         #file_content = await file.read()
#         #file_stream = io.BytesIO(file_content)
#         s3_path = f"{id}/{file.filename}"
#         #file_stream.seek(0) 
#         s3_client.upload_fileobj(file.file, bucket_name, s3_path)
#         s3_file_stream = io.BytesIO()
#         s3_client.download_fileobj(bucket_name, s3_path, s3_file_stream)
#         s3_file_stream.seek(0)
#         s3_client.delete_object(Bucket=bucket_name, Key=s3_path)
#         file_streams = [s3_file_stream]

#         assistant_item = get_assistant_from_dynamodb(id)
#         personal_assistant_id = assistant_item.get('assistant_id', default_assistant_id)
#         vector_store_id=assistant_item.get('vector_store_id')

#     if file_streams:
#         file_create=client.files.create(file=(file.filename,  file_streams[0]),purpose='assistants')
#         print(file_create)
#         file_batch = client.beta.vector_stores.files.create(vector_store_id=vector_store_id, file_id=file_create.id)
#         #print(file_batch.status)
#         #print(file_batch.file_counts)
#         print(file_batch)
#         for stream in file_streams:
#             stream.close()  
    

#     assistant = client.beta.assistants.update(
#         assistant_id=personal_assistant_id,
#         tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
#     )
#     all_files = list(client.beta.vector_stores.files.list(vector_store_id))
#     file_info_array = []
#     for item in all_files:
#         tmpF = client.files.retrieve(file_id=item.id)
#         file_info = {
#             "id": tmpF.id,
#             "filename": tmpF.filename
#         }
#         file_info_array.append(file_info)
   
#     return {'message': 'File uploaded successfully', 'assistant_id': personal_assistant_id,'id':id,'files':file_info_array}

# @app.get("/get_assistants")
# async def get_items(authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
#     try:
#         response = table.scan()
#         items = response.get('Items', [])
#         return {'items': items}
#     except Exception as e:
#         return {'error': str(e)}
    
# @app.get("/get_assistants/{assistant_id}")
# async def get_assistant(assistant_id: str,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     assistant = get_assistant_from_dynamodb(assistant_id)
#     if assistant:
#         return assistant
#     else:
#         raise HTTPException(status_code=404, detail="Assistant not found")
    
# @app.get("/get_assistants_for_user/{userid}")
# async def get_assistants_for_user(userid: str, authorization: str = Header(...)):

#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     assistant = get_assistant_for_user_from_dynamodb(userid)
#     if assistant:
#         return assistant
#     else:
#         raise HTTPException(status_code=404, detail="Assistant not found")
    
# @app.get("/get_vector_store_file/{vector_store_id}")
# async def get_vector_store_file(vector_store_id: str,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     files_table = dynamodb.Table('files')
#     response = files_table.scan(
#         FilterExpression=Attr('vectorstore_id').eq(vector_store_id)
#     )
    
#     file_info_array = []
#     if response['Items']:
#         for item in response['Items']:
#             file_info = {
#                 "id": item['id'],
#                 "filename": item['filename'],
#                 "created_date": item['created_date']
#             }
#             file_info_array.append(file_info)
    
#     return file_info_array

# @app.post("/authenticate")
# async def authenticate(authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")

#     id_token = authorization[len("Bearer "):]
#     JWKS_URI = f'https://{TENANT_NAME}.b2clogin.com/{TENANT_NAME}.onmicrosoft.com/discovery/v2.0/keys?p={POLICY_NAME}'
#     JWT_ISSUER = f"https://{TENANT_NAME}.b2clogin.com/{TENANT_ID}/v2.0/"
#     jwks = get_jwks(JWKS_URI)
#     public_key = get_public_key(id_token, jwks)
    
    
#     try:
#        print('Vdecode ended')
#        payload = jwt.decode(
#             id_token,
#             public_key,
#             audience=CLIENT_ID,
#             algorithms=["RS256"],
#             issuer=JWT_ISSUER
#         )
#        print('decode Ended')
#        print(payload)
#        users_table = dynamodb.Table('users')
#        email = payload.get("emails", [None])[0]
#        name = payload.get("name")
       
#        response = users_table.scan(
#             FilterExpression=Attr('email').eq(email)
#         )
#        if response['Count'] == 0:
#            provider = payload.get("idp")
#            userid = str(uuid.uuid4())
#            users_table.put_item(Item={
#                 'userid': userid,
#                 'email': email,
#                 'name': name,
#                 'provider': provider
#             })
#        else:
#               userid = response['Items'][0]['userid']
           
#        return {"userid": userid,"email": email,"name": name}
    
#     except ExpiredSignatureError:
#        #raise HTTPException(
#        #    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired!"
#        #)
#        return {"userid": "52b0fb30-b727-41d2-9775-fb6fe2befe23","email": "mailtonijesh@gmail.com","name": "Nijesh S"}
#     except InvalidTokenError as e:
#         print(e) 
#         #raise HTTPException(
#            #status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token claims"
#        #)
#         return {"userid": "52b0fb30-b727-41d2-9775-fb6fe2befe23","email": "mailtonijesh@gmail.com","name": "Nijesh S"}
#     except Exception:
#        #raise HTTPException(
#        #    status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to validate token"
#        #)
#        return {"userid": "52b0fb30-b727-41d2-9775-fb6fe2befe23","email": "mailtonijesh@gmail.com","name": "Nijesh S"}

# @app.delete("/delete_file/{file_id}")
# async def get_assistant(file_id: str,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
#     file = client.files.delete(file_id=file_id)
#     files_table = dynamodb.Table('files')
#     response = files_table.delete_item(
#             Key={
#                 'id': file_id
#             }
#         )

#     return {'message': 'File deleted successfully'}

# @app.delete("/delete_assistant/{id}")
# async def delete_assistant(id: str,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     assistant_item = get_assistant_from_dynamodb(id)
#     personal_assistant_id = assistant_item.get('assistant_id')
#     vector_store_id=assistant_item.get('vector_store_id')
#     assiatnt_name=assistant_item.get('assistant_name')
#     delete_response = client.beta.assistants.delete(assistant_id=personal_assistant_id)
#     delete_dynamodb_item(id,assiatnt_name)
#     #check vecotr store files and delete

#     return {'message': 'Assistant deleted successfully'}

# @app.get("/generate_presigned_url")
# async def generate_presigned_url(id: str, file_name: str,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     try:
#         s3_path = f"{id}/{file_name}"
#         presigned_url = s3_client.generate_presigned_url(
#             'put_object',
#             Params={
#                 'Bucket': bucket_name,
#                 'Key': s3_path,
#                 'ContentType': 'application/octet-stream'  # Set content type to binary
#             },
#             ExpiresIn=3600  # URL expiration time in seconds
#         )
#         return {"presigned_url": presigned_url}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {e}")
    
# @app.post("/save_custom_widget")
# async def save_custom_widget(request: Request,authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=400, detail="Invalid authorization header")
#     token = authorization[len("Bearer "):]
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid token")
    
#     data = await request.json()
#     assistant_id = data.get('assistant_id')
#     widget_config = data.get('widget_config')
#     headerTitle = widget_config.get('headerTitle')
#     primaryColor = widget_config.get('primaryColor')
#     showButtonText = widget_config.get('showButtonText')
#     buttonText = widget_config.get('buttonText')
#     iconLetter = widget_config.get('iconLetter')

#     assistant_item = get_assistant_from_dynamodb(assistant_id)
#     if not assistant_item:
#         return {'error': 'Assistant not found'}, 404
#     assistant_name = assistant_item.get('assistant_name')
#     response = table.update_item(
#             Key={'Id': assistant_id, 'assistant_name': assistant_name},
#             UpdateExpression="set headerTitle = :i, primaryColor = :a, showButtonText = :m, buttonText = :r, iconLetter = :e",
#             ExpressionAttributeValues={
#                 ':i': headerTitle,
#                 ':a': primaryColor,
#                 ':m': showButtonText,
#                 ':r': buttonText,
#                 ':e': iconLetter,
#             },
#             ReturnValues="UPDATED_NEW"
#         )
#     return {'message': 'Widget updated successfully'}

# #handler = Mangum(app)
