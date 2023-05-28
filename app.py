import logging
import os
import subprocess
import sys
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import (
    ConversationalRetrievalChain,
    LLMChain,
    SequentialChain,
    SimpleSequentialChain,
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI as LangChainOpenAI
import langchain.agents as lc_agents
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import DeepLake
from streamlit.components.v1 import html

# Load the environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_code():
    """
    Generate code using ChatOpenAI model and display it in the Streamlit app.
    """
    logger = logging.getLogger(__name__)
    try:
        model = ChatOpenAI(model_name='gpt-4')
        retriever = db.as_retriever()
        retriever.search_kwargs['distance_metric'] = 'cos'
        retriever.search_kwargs['fetch_k'] = 20
        retriever.search_kwargs['maximal_marginal_relevance'] = True
        retriever.search_kwargs['k'] = 20
        qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)

        st.session_state.generated_code = (
            qa({"question": prompt, "chat_history": []})["answer"]
            .split("```python\n")[1].split("```")[0]
        )

        st.session_state.code_language = code_language
        st.code(
            st.session_state.generated_code,
            language=st.session_state.code_language.lower(),
        )

        with st.expander('Message History'):
            st.info(prompt)
    except Exception as e:
        st.write(traceback.format_exc())
        logger.error(f"Error in code generation: {traceback.format_exc()}")


def save_code():
    """
    Save the generated code to a file.
    """
    logger = logging.getLogger(__name__)
    try:
        file_name = code_file
        logger.info(f"Saving code to file: {file_name}")
        if file_name:
            with open(file_name, "w") as f:
                f.write(st.session_state.generated_code)
            st.success(f"Code saved to file {file_name}")
            logger.info(f"Code saved to file {file_name}")
        st.code(
            st.session_state.generated_code,
            language=st.session_state.code_language.lower(),
        )
    except Exception as e:
        st.write(traceback.format_exc())
        logger.error(f"Error in code saving: {traceback.format_exc()}")


def setup_logging(log_file):
    """
    Setup logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
        filename=log_file,
        filemode='a',
    )


if __name__ == "__main__":
    # Session state variables
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = ""

    # Generate the code
    if button_generate:
        generate_code()

    # Save the code to a file
    if button_save and st.session_state.generated_code:
        save_code()
