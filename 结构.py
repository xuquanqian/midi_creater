midi_creater
├── src/                  # 源代码
│   ├── rhythm
│   │   ├── __init__.py
│   │   ├── editor.py
│   │   ├── handler.py
│   │   └── types.py
│   ├── song_structure/          # 新增目录
│   │   ├── __init__.py
│   │   ├── section_manager.py   # 段落管理核心逻辑
│   │   ├── clipboard.py         # 剪贴板功能
│   │   └── structure_editor.py  # 段落编辑器UI
│   ├── main_app.py
│   ├── chord_generator.py
│   ├── visualizer.py
│   ├── skin_manager.py
│   ├── grid_editor.py
│   ├── constants.py
│   ├── custom_types.py
│   ├── midi_player.py
│   ├── style_selector.py
│   └── utils
│       ├──__init__.py
│       ├── debug_tools.py
│       └── font_manager.py
├── docs/                 # 文档
│   └── design.md         # 设计文档
├── skins/                # 皮肤资源
│   ├── default/
│   ├── japanese/
│   └── modern/
├── tests/                # 测试目录
├── requirements.txt      # Python依赖
├── README.md             # 项目说明
└── .gitignore