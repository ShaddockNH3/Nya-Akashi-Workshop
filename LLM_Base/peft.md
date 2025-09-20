## peft

由于没有本地显卡，是在colab上跑的，因此传统的模型微调肯定是没办法跑的。

所以引出[peft](https://huggingface.co/docs/peft/quicktour)，这是一个lora技术，可以不进行真的微调，只是为模型穿上一层“外骨骼”，大大降低训练成本。

