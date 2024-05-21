from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import json, os, shutil, pymongo, markdown
import pandas as pd
from pandasai import Agent, SmartDataframe
from pandasai.llm.google_gemini import GoogleGemini
from .serializers import PandasAI_Excel_Upload_Serializer
from django.conf import settings
from pymongo import MongoClient
from bson import json_util
from django.http import JsonResponse


# this api can get all the collections from the database : 
class PandasAI_getAllCollection(APIView):
    def get(self, request):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['PandasAI']
            collection = db['all_excels']
            documents = collection.find({}, {'_id': 0})  # Exclude the '_id' field for cleaner output
            # all_collections = list(documents)
            all_collections=[]
            for doc in list(documents):
                all_collections.append(doc['file_name'])
            
            client.close()
            return Response({'collections': all_collections}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# this is upload excel api which can upload the excel in the mongodb database : 
class PandasAI_uploadexcel(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PandasAI_Excel_Upload_Serializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            file_name = file.name
            
            df = pd.read_excel(file)
            df_json = df.to_json(orient='records')
            
            # Prepare the data to be inserted into MongoDB
            data = {
                'file_name': file_name,
                'data': df_json
            }
            client = MongoClient('mongodb://localhost:27017/')
            db = client['PandasAI']
            collection = db['all_excels']
            collection.insert_one(data)
            client.close()
            return Response({'message': 'File uploaded successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# ============================= CHAT USING REST API'S  =========================================== #


# # this class is for generating the Agent on selected excels sheet: 
# # os.environ["PANDASAI_API_KEY"] = "$2a$10$r4z8hMvzak5RZBWYw3uy.OaZ3TgoL/K5vPEs3huf4hg.pgutwdOXK"
# pandas_agent = None
# class PandasAI_Agent:
#     def __init__(self, selectedexcel) -> None:
#         # self.df = pd.read_excel("C:/Users/Lenovo/Desktop/pandas_app/pandasAI_app/input_excelSheets/input.xls")
#         client = pymongo.MongoClient("mongodb://localhost:27017/")
#         db = client["PandasAI"]
#         collection = db[selectedexcel]
#         data = list(collection.find())
#         data_json = json_util.dumps(data)
#         data_dict = json_util.loads(data_json)
#         temp_df = pd.DataFrame(data_dict)
        
#         if '_id' in temp_df.columns:
#             temp_df = temp_df.drop(columns=['_id'])
#         # Ensure all string columns are properly encoded in UTF-8
#         # for column in temp_df.select_dtypes(include=[object]).columns:
#         #     temp_df[column] = temp_df[column].apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8', 'ignore') if isinstance(x, str) else x)
            
#         self.df = temp_df
#         self.agent = None
        
#         # removing the cache, exports and pandasai.log folder: 
#         cache_folder_path = "C:/Users/Lenovo/Desktop/pandas_app/pandasAI_app/cache"
#         if os.path.exists(cache_folder_path):
#             try:
#                 # Attempt to remove the folder and its contents
#                 shutil.rmtree(cache_folder_path)
#                 print("cache Folder and its contents removed successfully.")
#             except Exception as e:
#                 print("Error occurred:", e)
#         else:
#             print("cache Folder does not exist.")
            
#         charts_folder_path = "C:/Users/Lenovo/Desktop/pandas_app/pandasAI_app/static/charts"
#         if os.path.exists(charts_folder_path):
#             try:
#                 # Attempt to remove the folder and its contents
#                 shutil.rmtree(charts_folder_path)
#                 print("charts Folder and its contents removed successfully.")
#             except Exception as e:
#                 print("Error occurred:", e)
#         else:
#             print("charts Folder does not exist.")

#     def generate_Agent(self):
#         gemini_llm = GoogleGemini(
#             api_key="AIzaSyB0PMN5Tag4BAC8xx46uGxUGXmd4FZUFHc",
#         )
#         agent = SmartDataframe(self.df, config={"llm": gemini_llm,"open_charts":False,"save_charts": True, "save_logs":False, "save_charts_path": 'static/charts'})
#         self.agent = agent
    
#     def get_ans(self, query):
#         print(query)
#         return self.agent.chat(query)


# # this api will make an agent corresponding to the particular excel: 
# class PandasAI_makeagent(APIView):
#     def post(self, request):
#         global pandas_agent
#         json_req = json.loads(request.body)
#         selectedexcel = json_req['collectionName']
#         pandas_agent = PandasAI_Agent(selectedexcel)
#         pandas_agent.generate_Agent()
#         return Response({"data":selectedexcel})


# # this api will reset the selected excel sheet : 
# class PandasAI_Resetstatus(APIView):
#     def get(self, request):
#         global pandas_agent
#         pandas_agent = None
#         return Response({"data": "successfull reset the status"})

# # this is chat api which can chat over the selected document: 
# class PandasAI_Chatapi(APIView):
#     def post(self, request):
#         json_req = json.loads(request.body)
#         query = json_req['query']
#         global pandas_agent
#         if pandas_agent is None:
#             return JsonResponse({"error": "no excel selected..."}, status=400)
#         ans = pandas_agent.get_ans(query)
#         if isinstance(ans, pd.DataFrame):
#             html_table = ans.to_html(index=False)
#             # html_table = ans.to_markdown(index=False)
            
#             print("html_table : ",html_table)
#             print(type(html_table))
#             ans = html_table
        
#         print(ans)
#         print(type(ans))
#         return Response({'data': ans})


