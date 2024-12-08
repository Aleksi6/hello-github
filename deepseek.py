import json
import logging
import time
import re
from tqdm import tqdm  # 导入tqdm用于显示进度条

import openai

# 使用你提供的API key，务必确保其合法有效且妥善保管，防止泄露
api_key = "sk-70ec806889b24bb0b6ca57b66b701fdd"
openai.api_key = api_key
openai.api_base = "https://api.deepseek.com"

# 模拟的10个英文句子列表，实际应用中可替换为真实获取的句子数据
english_sentences = [
    "This is a sample sentence 1.",
    "That's another example sentence.",
    "I'm happy today.",
    "She likes music.",
    "They are watching TV.",
    "He studies hard.",
    "We have a good time.",
    "The book is interesting.",
    "My dog is cute.",
    "It's a beautiful day."
]

results = []
logging.basicConfig(filename='translation_errors.log', level=logging.DEBUG)  # 将日志级别调整为DEBUG，方便查看详细信息

# 设置请求间隔时间，单位为秒，可以根据API限制适当调整这个值
interval = 2


def extract_french_translation(text):
    """
    简单尝试从文本中提取可能的法语翻译内容，通过查找符合法语句子结构特点的部分
    （这里只是简单示例，可根据实际情况优化判断规则）
    """
    possible_french = []
    lines = text.splitlines()
    for line in lines:
        if line.strip() and line[0].isupper() and any(char.isalpha() for char in line) and any(french_word in line.lower() for french_word in ["est", "et", "le", "la", "les", "de", "du", "à"]):
            possible_french.append(line.strip())
    return possible_french[-1] if possible_french else ""


def extract_chinese_translation(text):
    """
    简单尝试从文本中提取可能的中文翻译内容，通过查找包含中文常见汉字的部分
    （这里只是简单示例，可根据实际情况优化判断规则）
    """
    import re
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    matches = chinese_pattern.findall(text)
    return "".join(matches) if matches else ""


# 使用tqdm来包裹循环，显示进度条，total参数指定总任务数（即句子的数量）
for idx, sentence in tqdm(enumerate(english_sentences, start=1), total=len(english_sentences)):
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert translator assistant. Your task is to accurately translate the given English sentences into Chinese and French, providing accurate and fluent translations for each sentence."},
                {"role": "user", "content": sentence}
            ],
            stream=False
        )
        # 检查response中是否存在error信息来判断请求是否异常
        if 'error' in response:
            raise openai.error.APIError(f"Request failed with error: {response['error']}")
        translation_text = response['choices'][0]['message']['content']
        try:
            zh_translation = extract_chinese_translation(translation_text)
            fr_translation = extract_french_translation(translation_text)
            result_dict = {
                "sentence_id": idx,
                "original": sentence,
                "translations": {
                    "zh": zh_translation,
                    "fr": fr_translation
                }
            }
            results.append(result_dict)
        except:
            logging.error(f"Unexpected translation data format for sentence {idx}: {translation_text}. Setting empty translations.")
            result_dict = {
                "sentence_id": idx,
                "original": sentence,
                "translations": {
                    "zh": "",
                    "fr": ""
                }
            }
            results.append(result_dict)
    except (openai.error.OpenAIError, KeyError) as e:
        logging.error(f"Error translating sentence {idx}: {e}")
    time.sleep(interval)

print(json.dumps(results, ensure_ascii=False, indent=4))