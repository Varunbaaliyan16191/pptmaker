# ==========Load Module==========

import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st

# ==========Streamlit Front-End==========

# to show web-app: complete page layout
st.set_page_config(layout="wide")

st.title("AI PPT Generator")
st.divider()
st.sidebar.title("Enter API Key's")

# ==========Load API Key==========

GOOGLE_API_KEY = st.sidebar.text_input("Google-API", type = "password")
TAVILY_API_KEY = st.sidebar.text_input("Tavily-API", type = "password")

# ==========API Validations==========

ALL_API = [GOOGLE_API_KEY, TAVILY_API_KEY]

if not all(ALL_API):
  st.sidebar.error("Must Pass all API Key's")

elif all(ALL_API):
  st.sidebar.success("API KEY's Loaded Successfully")

  # Model Load
  model = ChatGoogleGenerativeAI(
    google_api_key = GOOGLE_API_KEY,
    model = st.sidebar.selectbox("Gemini-Model-Name",
                                 options = ['gemini-2.5-flash',
                                            'gemini-2.5-flash-lite',
                                            'gemini-3.5-flash',
                                            'gemini-3.5-flash-lite'])
  )
else:
  st.sidebar.info("Check API Key's")

# ==========Back-End code==========

# Tool 1:
# Search_latest_info using tavily

def Search_latest_info(query):
  """this function helps to give
  latest search using tavily
  based on given user query related research
  or contant"""

  client = TavilyClient(api_key = TAVILY_API_KEY)
  response = client.search(query)
  return response

# ==========User Input==========

st.header("Write prompt to Generate PPT or Image or fetch Latest News")

user_input = st.text_area("Write Here: ")



# Tool 2:
# Generate image using free api

def generate_image(img_prompt, slide_no = 1):
  """this function helps user to generate
  image using free api, with given
  img_promot"""

  url = f"https://image.pollinations.ai/{img_prompt}"

  import requests as r
  content = r.get(url).content
  with open(f"ai_image_{slide_no}.jpeg",'wb') as f:
    f.write(content)

  from PIL import Image
  img = Image.open(f"ai_image_{slide_no}.jpeg")
  return url



# Tool 3:

def agent_prompt(query):
  """this function to promptify the given user
  query, suppose user needs ppt based on given
  query by user, it give detailed professional
  prompt to return the prompt"""

  prompt = f"""give detailed highly professiional
  prompt for below given prompt.

  you are professional ppt designer,
  based on user given query, your task is to professional
  HTML output prompt with no markdown.
  User query: {query}"""

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open("PPT_prompt.txt", 'w') as f:
    f.write(final_prompt)

  return final_prompt



# Tool 4:

def run_agent(leader_agent,query):
  prompt = f"""Based on below given query,
  your task is to call specific tool, first to
  promptify user prompt, than call image tool, or
  latest search if required. give slide dynamic, ui ux,
  with creative design,keep help of function to generate image
  based on given topic,
  Generate image using
  with no of slide asked
  and imbed that in same html ppt
  and using file handling embed this in output html,
  use java script function
  to generate image using async func and threading
  and give output in HTML
  user query given below:

  """
  prompt+= query
  prompt = agent_prompt(prompt)
  
  response = leader_agent.invoke({'messages':[{'role':'user','content':prompt}]})
  code = response['messages'][-1].content[-1]['text']
  return code

# ==========Agent Call==========

# leader_agent creation
if all(ALL_API):
  leader_agent = create_agent(
      model = model,
      tools = [Search_latest_info,generate_image]
  )
else:
  st.info("Pass All API Key's and Return")
# ==========Navbar Streamlit=========

tab1, tab2, tab3 = st.tabs(["GENERATE IMAGE", 
                            "FETCH LATEST NEWS",
                            "GENERATE PPT"])

if (user_input) and (leader_agent):
  # TAB 1:
  with tab1:
    if st.button("Click to generate: ", key="generate_img_button"):
      with st.spinner("Running Agent.."):
        try:
          img = generate_image(user_input)
          st.image(img)
        except:
          url = f"https://image.pollinations.ai/{user_input}"
          time.sleep(4)
          st.image(url)
          
  # TAB 2:        
  with tab2:
    if st.button("Fetch news: ", key="news_button"):
      with st.spinner("Running Agent.."):
        try:
          prompt = "Give Multiple news in HTML card format for topic" + user_input
        
          response = leader_agent.invoke({'messages':[{'role':"user", "content":prompt}]})
          code = response['messages'][-1].content[-1]['text']
  
          st.html(code, width="stretch", unsafe_allow_javascript=True)
        except Exception as err:
          st.error(err)

  # TAB 3:
  with tab3:
    if st.button("Click to generate: ", key="generate_ppt_button"):
      with st.spinner("Running Agent.."):
        try:
          code = run_agent(leader_agent, user_input)
          st.html(code, width="stretch", unsafe_allow_javascript=True)

          # FILE Save
          with open("ppt.html",'w') as f:
            f.write(code)
          st.download_button(label = "DOWNLOAD PPT",
                          data = code,
                          file_name = 'ppt.html',
                          mime = 'text/html')
        except Exception as err:
          st.error(err)

else:
  st.error("Something went Wrong!!")
