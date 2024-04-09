# Data Engineering with Python Training

This training repository provides an introduction to data engineering in `python`, covering topics such as data modeling, schema design, storage and retrieval, data processing and transformation, and data pipelines and ETL processes. Participants will also learn how to use Python to interact with cloud-based data engineering services, such as AWS Glue, Google Cloud Dataflow, or Azure Data Factory.

Upon covering basic data modeling and engineering concepts, we also explore standing up real-time front end applications with backend db setup, exploring Generative AI, and its applications.

The repository includes hands-on exercises and examples, as well as resources for further learning and exploration.

## Proposed Syllabus

0. Fundamentals
    * [Introduction to Github](https://github.com/mhdk1602/python_training/blob/main/0.1%20Getting%20Started%20-%20Python.ipynb)
    * [Getting Started with Python](https://github.com/mhdk1602/python_training/blob/79820385ea90e32157e0852bfbdc109b0b0aa0e7/0.2%20Jupyter%20-%20Intro.ipynb)
        * [Functions](https://github.com/mhdk1602/python_training/blob/79820385ea90e32157e0852bfbdc109b0b0aa0e7/0.3%20Functions.ipynb)
        * [Looping](https://github.com/mhdk1602/python_training/blob/79820385ea90e32157e0852bfbdc109b0b0aa0e7/0.4%20Looping.ipynb)
        * [Reading Data](https://github.com/mhdk1602/python_training/blob/79820385ea90e32157e0852bfbdc109b0b0aa0e7/0.5%20Reading-Data.ipynb)
    * [Getting Started with Jupyter Notebooks](https://github.com/mhdk1602/python_training/blob/79820385ea90e32157e0852bfbdc109b0b0aa0e7/1.1%20Fundamentals.ipynb)

1. Introduction to Data Engineering

    * [Overview of data engineering and its role in the data pipeline](https://github.com/mhdk1602/python_training/blob/main/1.1%20Fundamentals.ipynb)
    * [Key concepts and terminology in data engineering](https://github.com/mhdk1602/python_training/blob/main/1.2%20Key%20concepts%20and%20terminology.ipynb)
    * [Common data formats and structures](https://github.com/mhdk1602/python_training/blob/main/1.3%20Data%20Formats%20%26%20Structures.ipynb)

2. Data Modeling and Schema Design

    * [Introduction](https://github.com/mhdk1602/python_training/blob/main/2.1%20Data%20Modeling.ipynb)
    * [NoSQL databases and data modeling](https://github.com/mhdk1602/python_training/blob/main/2.2%20NoSQL%20DB.ipynb)
    * [Schema Modeling](https://github.com/mhdk1602/python_training/blob/main/2.3%20Schema%20Modeling.ipynb)
    * [Data Modeling Exercise](https://github.com/mhdk1602/python_training/blob/main/2.4%20Data%20Modeling%20-%20Exercise.ipynb)

3. [Data Storage and Retrieval](https://github.com/mhdk1602/python_training/blob/main/3.%20Data%20Storage%20and%20Retrieval.ipynb)

    * Overview of different types of data storage systems (e.g. file systems, databases, data lakes)
    * Reading and writing data from various storage systems in Python (e.g. CSV, JSON, Parquet)
    * Best practices for managing data storage and retrieval

4. [Data Processing and Transformation](https://github.com/mhdk1602/python_training/blob/main/4.%20Data%20Processing%20and%20Transformation.ipynb)

    * Introduction to Data Processing and Transformation

        * Definition
        * Importance in Data Engineering

    * Data Cleaning

        * Handling Missing Values
        * Removing Duplicates
        * Code examples

    * Data Filtering

        * Definition and Importance
        * Techniques for Data Filtering
        * Code examples: Basic and Advanced

    * Data Aggregation

        * Definition and Importance
        * Techniques for Data Aggregation
        * Code examples

    * Tools and Libraries

        * Pandas: Overview and Code examples
        * NumPy: Overview and Code examples
        * Dask: Overview and Code examples

    * Optimizing Data Processing and Transformation Pipelines

        * Best Practices
        * Code examples

5. [Data Streaming and Real-time Processing](https://github.com/mhdk1602/python_training/blob/main/5.%20Data%20Streaming%20and%20Real-time%20Processing.ipynb)

    * Introduction to data streaming and real-time processing
    * Tools and libraries for real-time data processing in Python (e.g., Apache Kafka, Apache Flink, Faust)
    * Best practices for implementing real-time data processing pipelines

6. Data Integration and APIs

    * [Introduction to data integration and APIs in data engineering](https://github.com/mhdk1602/python_training/blob/main/6.1%20Data%20Integrations%20with%20APIs.ipynb)
    * [Working with APIs in Python (e.g., REST, GraphQL)](https://github.com/mhdk1602/python_training/blob/main/6.2%20Data%20Integrations%20with%20APIs%20-%20contd.ipynb)
    * [Introduction to GraphQL](https://github.com/mhdk1602/python_training/blob/main/6.3%20GraphQL.ipynb)
    * [Postgres/Postgraphile Setup](https://github.com/mhdk1602/python_training/blob/main/6.4.1%20Postgres%20Postgraphile%20setup.ipynb)
    * [NextJS front-end application for GraphQL](https://github.com/mhdk1602/python_training/blob/main/6.4.2%20NextJS%20Implementation.ipynb)
    * [Migration to Hasura](https://github.com/mhdk1602/python_training/blob/main/6.5%20Hasura%20-%20GraphQL.ipynb)
    * [Implementing a chatbot on our Stock Trading Platform Application](https://github.com/mhdk1602/python_training/blob/main/6.6%20Frontend%20Chatbot%20App.ipynb)
        * Recommended after Chapter 7

7. Text Comparison

    * [Fuzzy Matching, Levenshtein Distance, & Other text comparison algorithms](https://github.com/mhdk1602/python_training/blob/main/7.%20Text%20Comparison.ipynb)
    * [Text Embeddings](https://github.com/mhdk1602/python_training/blob/main/7.1%20Embeddings.ipynb)
    * [Embeddings in Data Engineering](https://github.com/mhdk1602/python_training/blob/main/7.2%20Embeddings%20-%20Contd.ipynb)
    * [Embeddings with Elastisearch](https://github.com/mhdk1602/python_training/blob/main/7.3%20Embeddings%20-%20Elasticsearch.ipynb)

8. Generative AI/LLMs

    * [GPT4 - Primer](https://github.com/mhdk1602/python_training/blob/main/GPT4-Chatbot/Chatbot%20-%20GPT4-%20Primer.docx)
    * [Anthropic Setup](https://github.com/mhdk1602/python_training/blob/main/8.2%20Anthropic%20setup.ipynb)
    * [Anthropic Chatbot](https://github.com/mhdk1602/python_training/blob/main/8.3%20Chatbot%20-%20Anthropic%20-%20Playbook.ipynb)
    * [Langchain](https://github.com/mhdk1602/python_training/blob/main/8.4%20Langchain.ipynb)

9. Data Quality & Validation
    * [Importance, Techniques, & Frameworks](https://github.com/mhdk1602/python_training/blob/main/9.1%20Data%20Quality%20and%20Validation.ipynb)
    * [Data Quality implementation using DBT](https://github.com/mhdk1602/python_training/blob/main/9.2%20DQ%20-%20Dbt.ipynb)
