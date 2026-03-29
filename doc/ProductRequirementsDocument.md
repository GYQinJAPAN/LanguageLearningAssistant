# 中文版
需求:
最近我在hellotalk上和母语是英语的人聊天,由于我的英语基础很差,虽然我很想和对面聊天,但是我不知道该说什么英文.
所以,我的做法只能是把我想说的中文,先输入到苹果手机的一个叫翻译的APP,进行语言转换.
对于简单的英语来说,这样就足够了.但是对于一些比较口语化的内容,我有的时候不太信任这个app,因为我感觉它的翻译是直译,不够地道.
所以这个时候我就会寻求ai的帮助.但是这也有一个问题,就是每次都要询问一个ai,"........",这句话翻译成英文怎么说.
这很麻烦,起码对于整个聊天来说花费了很多不必要的时间.所以综上,我想做的app,初步是一个翻译app.


# English
## Problem
Non-native speakers using apps like HelloTalk struggle to produce natural, conversational English in real-time chats.
Existing translation tools (e.g., Apple Translate) tend to generate literal translations that lack fluency and contextual appropriateness.

## Solution
Design and implement an AI-powered conversational translation assistant that:
1. Converts Chinese input into natural, context-aware spoken English
2. Reduces interaction latency compared to traditional “ask AI each time” workflows
3. Supports real-time chat scenarios

## Core Features
Context-aware translation (chat history aware)
1. Tone selection (casual / polite / playful)
2. One-tap output for messaging apps
3. Continuous conversation optimization

## Technical Highlights
1. LLM-based rewriting (not translation)
2. Prompt engineering to avoid literal translation
3. Session memory for dialogue coherence
4. API latency optimization + caching

## Why it’s valuable
1. Targets real-world high-frequency scenario (chatting)
2. Clear differentiation from traditional translation apps
3. Combines NLP + product thinking