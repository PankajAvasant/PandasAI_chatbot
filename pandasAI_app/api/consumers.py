from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from time import sleep
import json, os, shutil, pymongo, markdown, asyncio
import pandas as pd
from pandasai import Agent, SmartDataframe
from pandasai.llm.google_gemini import GoogleGemini
from django.conf import settings
from pymongo import MongoClient
from bson import json_util
from django.http import JsonResponse


# this class is for generating the Agent on selected excels sheet: 
# os.environ["PANDASAI_API_KEY"] = "$2a$10$r4z8hMvzak5RZBWYw3uy.OaZ3TgoL/K5vPEs3huf4hg.pgutwdOXK"
pandas_agent = None
class PandasAI_Agent:
    def __init__(self, selectedexcel) -> None:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["PandasAI"]
        collection = db["all_excels"]

        temp_df = None
        try:
            document = collection.find_one({'file_name': selectedexcel})
            if document:
                data_json = document['data']
                data_list = json.loads(data_json)
                temp_df = pd.DataFrame(data_list)
            else:
                print(f"No data found for file: {selectedexcel}")
                self.df = None
                self.agent = None
                return
        except Exception as e:
            print("Error:", e)
            self.df = None
            self.agent = None
            return

        if temp_df is not None:
            if '_id' in temp_df.columns:
                temp_df = temp_df.drop(columns=['_id'])
            
            self.df = temp_df
        else:
            self.df = None

        self.agent = None
        client.close()
        # removing the cache, exports and pandasai.log folder: 
        cache_folder_path = "C:/Users/Lenovo/Desktop/pandas_app/pandasAI_app/cache"
        if os.path.exists(cache_folder_path):
            try:
                # Attempt to remove the folder and its contents
                shutil.rmtree(cache_folder_path)
                print("cache Folder and its contents removed successfully.")
            except Exception as e:
                print("Error occurred:", e)
        else:
            print("cache Folder does not exist.")
            
        charts_folder_path = "C:/Users/Lenovo/Desktop/pandas_app/pandasAI_app/static/charts"
        if os.path.exists(charts_folder_path):
            try:
                # Attempt to remove the folder and its contents
                shutil.rmtree(charts_folder_path)
                print("charts Folder and its contents removed successfully.")
            except Exception as e:
                print("Error occurred:", e)
        else:
            print("charts Folder does not exist.")

    def generate_Agent(self):
        gemini_llm = GoogleGemini(
            api_key="AIzaSyB0PMN5Tag4BAC8xx46uGxUGXmd4FZUFHc",
        )
        agent = SmartDataframe(self.df, config={"llm": gemini_llm,"open_charts":False,"save_charts": True, "save_logs":False, "save_charts_path": 'static/charts'})
        self.agent = agent
    
    def get_ans(self, query):
        print(query)
        return self.agent.chat(query)



class PandasAI_MakeAgentWebsocket(AsyncConsumer):
    async def websocket_connect(self, event):
        print('makeagent websocket got connected...', event)
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        global pandas_agent
        selectedexcel = event['text']
        pandas_agent = PandasAI_Agent(selectedexcel)
        pandas_agent.generate_Agent()
        await self.send({
            'type': 'websocket.send',
            'text': 'agent successfully made of '+selectedexcel+' file',
        })
        
    async def websocket_disconnect(self, event):
        print("websocket disconnected ...", event)
        raise StopConsumer()




class PandasAI_ChatWebsocket(AsyncConsumer):
    async def websocket_connect(self, event):
        print('websockets connected...', event)
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        query = event['text']
        global pandas_agent
        
        if pandas_agent is None:
            await self.send({
                'type': 'websocket.send',
                'text': 'please select the excelsheet',
            })
        else :
            ans = pandas_agent.get_ans(query)
            if isinstance(ans, pd.DataFrame):
                html_table = ans.to_html(index=False)
                # html_table = ans.to_markdown(index=False)
                
                print("html_table : ",html_table)
                print(type(html_table))
                ans = html_table
            
            print(ans)
            
            await self.send({
                'type': 'websocket.send',
                'text': str(ans),
            })
        
    async def websocket_disconnect(self, event):
        print("websocket disconnected ...", event)
        raise StopConsumer()



class PandasAI_ResetWebsocket(AsyncConsumer):
    async def websocket_connect(self, event):
        print('reset status websockets connected...', event)
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        global pandas_agent
        pandas_agent = None
        await self.send({
            'type': 'websocket.send',
            'text': 'status reset succesfully...',
        })
        
    async def websocket_disconnect(self, event):
        print("websocket disconnected ...", event)
        raise StopConsumer()


