## LangChain 快速入门指南

(quickstart)[https://python.langchain.com/docs/integrations/chat/huggingface/]

看的应该是HuggingFacePipeline版本

实际上LangChain就是一个大型转接头，可以适配所有模型。

需要注意的是LangChain不能接受Lora，必须得把Lora和原模型合并后才能接入LangChain。

## Build a semantic search engine

[语义搜索](https://python.langchain.com/docs/tutorials/retrievers/)

这部分大概就是RAG部分的R，构建一个向量词库。