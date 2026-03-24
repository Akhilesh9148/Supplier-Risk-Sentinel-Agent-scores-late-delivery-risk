import streamlit as st
from openai import AzureOpenAI

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key="51ba5d46601c477b844d3883af93463c",
    api_version="2024-02-15-preview",
    azure_endpoint="https://genai-trigent-openai.openai.azure.com/"
)

deployment_name = "gpt-4o-mini"

st.set_page_config(page_title="AI PRoduct Review Analyer", layout="wide", page_icon="📄")

st.title("AI Product Review Analyzer")

st.write("Analyze customer product reviews using GPT-4o-mini")

review = st.text_area("Enter Product Review")

if st.button("Analyze Review"):

    if review.strip() == "":
        st.warning("Please enter a review")
    else:

        prompt = f"""
        Analyze the following product review.

        Return the output in this format:

        Sentiment:
        Positive Aspects:
        Negative Aspects:
        Key Issues:
        Summary:

        Review:
        {review}
        """

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert product review analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content

        st.subheader("Analysis Result")
        st.write(result)