<div align="center">
  <a href="https://ikaros-521.github.io/Luna-Docs/site/">
    <img src="./ui/icon.png" width="240" height="240" alt="Click to jump to documentation">
  </a>
</div>

<div align="center">

# ✨ Luna AI  ✨

> **Special Thanks**: This project is a fork of the original [Luna AI](https://github.com/Ikaros-521/AI-Vtuber) created by [Ikaros-521](https://github.com/Ikaros-521). We are grateful for their pioneering work in AI VTuber technology and the open-source community.

[![][python]][python]
[![][github-release-shield]][github-release-link]
[![][github-stars-shield]][github-stars-link]
[![][github-forks-shield]][github-forks-link]
[![][github-issues-shield]][github-issues-link]  
[![][github-contributors-shield]][github-contributors-link]
[![][github-license-shield]][github-license-link]
[![][FOSSA-Status]][FOSSA-Status]


</div>

`Luna AI` is a virtual AI streamer that combines cutting-edge technology. Its core consists of a series of efficient artificial intelligence models and platforms, including `ChatterBot, GPT, Claude, langchain, chatglm, text-generation-webui, iFlytek Spark, Zhipu AI, Google Bard, Tongyi Xingchen, Alibaba Cloud Bailian (Tongyi Qianwen, Baichuan, Moonshot, 01.AI, MiniMax), Qianfan Large Model (Wenxin Yiyan), Gemini, Kimi Chat, koboldcpp, FastGPT, Ollama, One-API, AnythingLLM, LLM_TPU, Dify, Volcano Engine (Doubao)`. These models can run locally or be supported through cloud services. To bring conversations to life, it also integrates multimodal models, including image recognition capabilities from `Gemini and glm-4v`, which can capture and analyze computer screens for explanations.

The appearance of `Luna AI` is powered by `Live2D, Vtube Studio, xuniren, UE5 combined with Audio2Face, EasyAIVtuber, Digital Human Video Player (Easy-Wav2Lip, Sadtalker, GeneFace++, MuseTalk, AniTalker, local video), metahuman-stream (ernerf, musetalk, wav2lip), DH_live, live2d-TTS-LLM-GPT-SoVITS-Vtuber` technology, providing users with a vivid and interactive virtual avatar. This enables `Luna AI` to perform real-time interactive streaming on major platforms such as `Bilibili, Douyin, Kuaishou, WeChat Channels, Pinduoduo, 1688, Douyu, Taobao, Letdanmakufly, YouTube, Twitch, and TikTok`. Of course, it can also have personalized conversations with you in a local environment.

To make communication more natural, `Luna AI` uses advanced natural language processing technology combined with text-to-speech systems such as `Edge-TTS, VITS-Fast, elevenlabs, VALL-E-X, Reecho AI, OpenVoice, GPT_SoVITS, clone-voice, Azure TTS, fish-speech, ChatTTS, CosyVoice, F5-TTS, MultiTTS, MeloTTS`. This not only allows it to generate fluent responses but also enables voice transformation through `so-vits-svc and DDSP-SVC` to adapt to different scenarios and characters.

Additionally, `Luna AI` can collaborate with `Stable Diffusion` through specific commands to showcase artwork. Users can also customize copy for Luna AI to loop playback to meet different occasions' needs.

```
This project is completely free for personal use. For commercial use, a 10% commission applies. Please contact the author for authorization if you need commercial use.
If you find any identical shell-packaged programs being sold, they are all pirated. Please stop losses in time.
```

<a href="//space.bilibili.com/3709626/channel/collectiondetail?sid=1422512" target="_blank">▶︎ Video Tutorial Collection</span></a>
<span> | </span>
<a href="//ikaros521.eu.org/site">📄 Online Documentation</span></a>
<span> | </span>
<a href="//github.com/groxaxo/AI-Vtuber" target="_blank">🍉 GitHub</span></a>
<span> | </span>
<a href="//gitee.com/ikaros-521/AI-Vtuber" target="_blank">🍓 Gitee</span></a>
<span> | </span>
<a href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=Q9vzZr7a2BUt3Nk0LDKZOVFaQ7lYUYEn&authKey=ze2sFJ7v5S6ffgpXoRh80H4c5%2FejPXc2OydSg%2FuAS4YZey6VuKxS%2FyUK0SuEHYjH&noverify=0&group_code=996470582" target="_blank">🐧 AI Communication Q Group</span></a>

```mermaid
mindmap
  root((AI Vtuber))
    Platform
      Bilibili
      Douyin
      Kuaishou
      WeChat Channels
      Pinduoduo
      1688
      Douyu
      Taobao
      Letdanmakufly
      YouTube
      Twitch
      TikTok
      Local
    Brain
      OpenAI
        ChatGPT
        Kimi Chat
        koboldcpp
        FastGPT
        Ollama
        One-API
        LM Studio
        Groq
        Siliconflow
        Claude
        ChatGLM
      Zhipu AI
      LangChain
        Chat_With_File
        langchain_ChatChat
      ChatterBot
      text-generation-webui
      Google Bard
      Tongyi Xingchen
      Tongyi Qianwen
      Qianfan Ernie
      Gemini
      AnythingLLM
      LLM_TPU
      Dify
      Volcano Engine Doubao
      Custom LLM
      Local QA DB
    Voice
      Edge-TTS
      VITS
      bert-vits2
      VITS-fast-fine-tuning
      ElevenLabs
      GPT_SoVITS
      Azure TTS
      CosyVoice
      F5-TTS
      MultiTTS
      MeloTTS
    Eyes
      gemini-pro-vision
      glm-4v
    Decoration
      captions_printer
      audio_player
      http_transfer
    Voice Conversion
      so-vits-svc
      DDSP-SVC
    Body
      Live2D
      Vtube Studio
      UE5 + Audio2Face
      xuniren
      EasyAIVtuber
      Digital Human Player
        Easy-Wav2Lip
        Sadtalker
        GeneFace++
        MuseTalk
        AniTalker
        Local Video
      metahuman-stream
        ernerf
        musetalk
        wav2lip
      DH_live
      live2d-TTS-LLM-GPT-SoVITS-Vtuber
```

## 💡 How To Ask Questions The Smart Way

Please read the following before submitting issues:

https://lug.ustc.edu.cn/wiki/doc/smart-questions

## 🀅 Development & Project Related

You can use GitHub Codespaces for online development:

[![][github-codespace-shield]][github-codespace-link]  

### Simple Flowchart

```mermaid
graph TD
    A([Start]) --> B[Configure Capabilities]
    B --> C[Listen to Chat]
    C --> D[/Chat Data/]
    D --> E[Pre-processing<br/>Filter, Local QA, Song Request]
    E --> F[LLM Processing]
    F --> G[TTS Synthesis]
    G --> H[SVC Voice Conversion]
    H --> I[Play Audio]
    I --> J([End])
    
    E --> K{Discard?}
    K -- Yes --> L[Discard]
    K -- No --> M{Need TTS?}
    M -- Yes --> G
    M -- No --> I
```

### Detailed Logic

```mermaid
graph TD
    Start([Start]) --> GUI[Init GUI]
    GUI --> Config[Load Config]
    Config --> Run[Run]
    Run --> Platform{Platform Type}
    
    Platform --> Bilibili
    Platform --> Douyin
    Platform --> Kuaishou
    Platform --> ChatMode[Chat Mode]
    
    Bilibili --> Init[Instantiate Common, Logger, Handlers]
    Douyin --> Init
    Kuaishou --> Init
    ChatMode --> Init
    
    Init --> Monitor[Monitor Signals]
    Monitor --> Events{Event Type}
    
    Events --> Entrance[Entrance Event]
    Events --> Chat[Chat Event]
    Events --> Gift[Gift Event]
    
    Chat --> Process[Chat Processing]
    Process --> LocalQA{Local QA?}
    LocalQA -- Yes --> Answer[Get Answer]
    LocalQA -- No --> Song{Song Request?}
    
    Song -- Yes --> Sing[Singing Mode]
    Song -- No --> Draw{Draw Mode?}
    
    Draw -- Yes --> SD[Stable Diffusion]
    Draw -- No --> LLM{Use LLM?}
    
    LLM -- Yes --> Gen[Generate Response]
    Gen --> Audio[Audio Synthesis]
    
    Audio --> TTS[TTS]
    TTS --> SVC{Use SVC?}
    SVC -- Yes --> Convert[Voice Conversion]
    SVC -- No --> Play
    Convert --> Play[Play Audio]
```

## License

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FIkaros-521%2FAI-Vtuber.svg?type=large&issueType=license)](https://app.fossa.com/projects/git%2Bgithub.com%2FIkaros-521%2FAI-Vtuber?ref=badge_large&issueType=license) 

## ⭐️ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=groxaxo/AI-Vtuber&type=Date)](https://star-history.com/#groxaxo/AI-Vtuber&Date)

## 🤝 Contribution

### 🎉 Acknowledgments

Thanks to the following developers for their contributions to this project:

<a href="https://github.com/groxaxo/AI-Vtuber/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=groxaxo/AI-Vtuber" />
</a>

### 💸 Investors

![image](./docs/投资人/invest.png)

### 🌏 Partners

AIHubMix: [aihubmix.com](https://aihubmix.com/register?aff=1BMI)  ———— API proxy site for large language models like OpenAI, Google, Tongyi Qianwen, etc.

Xunlei Accelerator: [jsq.xunlei.com](https://jsq.xunlei.com/) New users can claim 7x24 hours of free acceleration benefits with a code. Redemption code: ikaros

### 🙌 Sponsorship

<div>
  <img src="https://images.cnblogs.com/cnblogs_com/ikaros-521/2328032/o_230719075908_%E6%94%AF%E4%BB%98%E5%AE%9D.png" style="width: 200px;">
  <img src="https://images.cnblogs.com/cnblogs_com/ikaros-521/2328032/o_230719075908_%E5%BE%AE%E4%BF%A1.png" style="width: 230px;">
</div>

## 🕳️ Blacklist

| User Info | Famous Quote |
|--------|------|
| QQ: 750359376 | LOL, no open source spirit at all |
| QQ: 378198682 | [Spreading rumors] |
| QQ: 1939834860 | [Advertiser] |
| QQ: 1687246688 | [Freeloading and toxic] |

[FOSSA-Status]: https://app.fossa.com/api/projects/git%2Bgithub.com%2FIkaros-521%2FAI-Vtuber.svg?type=shield&labelColor=black&issueType=license
[python]: https://img.shields.io/badge/python-3.10+-blue.svg?labelColor=black
[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-black?style=flat-square
[github-action-release-link]: https://github.com/actions/workflows/groxaxo/AI-Vtuber/release.yml
[github-action-release-shield]: https://img.shields.io/github/actions/workflow/status/groxaxo/AI-Vtuber/release.yml?label=release&labelColor=black&logo=githubactions&logoColor=white&style=flat-square
[github-action-test-link]: https://github.com/actions/workflows/groxaxo/AI-Vtuber/test.yml
[github-action-test-shield]: https://img.shields.io/github/actions/workflow/status/groxaxo/AI-Vtuber/test.yml?label=test&labelColor=black&logo=githubactions&logoColor=white&style=flat-square
[github-codespace-link]: https://codespaces.new/groxaxo/AI-Vtuber
[github-codespace-shield]: https://github.com/codespaces/badge.svg
[github-contributors-link]: https://github.com/groxaxo/AI-Vtuber/graphs/contributors
[github-contributors-shield]: https://img.shields.io/github/contributors/groxaxo/AI-Vtuber?color=c4f042&labelColor=black&style=flat-square
[github-forks-link]: https://github.com/groxaxo/AI-Vtuber/network/members
[github-forks-shield]: https://img.shields.io/github/forks/groxaxo/AI-Vtuber?color=8ae8ff&labelColor=black&style=flat-square
[github-issues-link]: https://github.com/groxaxo/AI-Vtuber/issues
[github-issues-shield]: https://img.shields.io/github/issues/groxaxo/AI-Vtuber?color=ff80eb&labelColor=black&style=flat-square
[github-license-link]: https://github.com/groxaxo/AI-Vtuber/blob/main/LICENSE
[github-license-shield]: https://img.shields.io/github/license/groxaxo/AI-Vtuber?color=white&labelColor=black&style=flat-square
[github-release-link]: https://github.com/groxaxo/AI-Vtuber/releases
[github-release-shield]: https://img.shields.io/github/v/release/groxaxo/AI-Vtuber?color=369eff&labelColor=black&logo=github&style=flat-square
[github-releasedate-link]: https://github.com/groxaxo/AI-Vtuber/releases
[github-releasedate-shield]: https://img.shields.io/github/release-date/groxaxo/AI-Vtuber?labelColor=black&style=flat-square
[github-stars-link]: https://github.com/groxaxo/AI-Vtuber/network/stargazers
[github-stars-shield]: https://img.shields.io/github/stars/groxaxo/AI-Vtuber?color=ffcb47&labelColor=black&style=flat-square
[pr-welcome-link]: https://github.com/groxaxo/AI-Vtuber/pulls
[pr-welcome-shield]: https://img.shields.io/badge/%F0%9F%A4%AF%20PR%20WELCOME-%E2%86%92-ffcb47?labelColor=black&style=for-the-badge
[profile-link]: https://github.com/Ikaros-521
