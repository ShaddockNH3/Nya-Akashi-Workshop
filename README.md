# Nya-Akashi-Workshop
Welcome to the Nya-Akashi-Workshop! 🛠️ This is where we build a fully interactive AI Agent of Akashi (Azur Lane), embedding her purr-sonality via LLMs and equipping her with game knowledge through a RAG pipeline.

tuning1.8bv1是测试版本，很乱
tuning1.8bv2是整理过的版本，增加了jsonl里的对话（至100句），优化了提示词，会稍微好一点
tuning1.8bv3引入了测试集和验证集，并且引入了Langchain框架，需要注意lora不能像此前那样简单加载了，必须得先将二者彻底融合为静态模型，然后再加载到Langchain里
tuning1.8bv4增加更多的对话数据（300+），尝试调整LoRA的超参数，r=16, epoch=4，不过效果很奇怪，因该是模型太小，epoch稍大，lr太大导致出了一些很神秘的问题
tuning1.8bv5计划把epoch降为2，将learning rate更改为1e-4，r暂时还是16，调整到这里能输出一些好的东西其实就差不多了