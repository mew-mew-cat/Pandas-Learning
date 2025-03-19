import json
import re

# 定义转换函数
def convert_py_to_notebook(py_file, ipynb_file):
    print(f"开始处理: {py_file} -> {ipynb_file}")
    
    # 读取Python文件
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 读取现有的Notebook文件以保留元数据
    with open(ipynb_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # 清空现有的单元格，但保留元数据
    notebook['cells'] = []
    
    # 使用正则表达式分割内容
    # 分割注释块（用作markdown）和代码块
    parts = re.split(r'(#{3,}.*?#{3,})', content, flags=re.DOTALL)
    
    current_text = ""
    in_markdown = False
    
    for part in parts:
        # 如果是注释块的开始或结束
        if re.match(r'#{3,}', part):
            # 如果之前有内容，添加到notebook中
            if current_text.strip():
                if in_markdown:
                    notebook['cells'].append({
                        'cell_type': 'markdown',
                        'metadata': {},
                        'source': convert_to_markdown(current_text)
                    })
                else:
                    # 跳过空的代码块
                    if not all(line.strip() == "" for line in current_text.strip().split('\n')):
                        notebook['cells'].append({
                            'cell_type': 'code',
                            'execution_count': None,
                            'metadata': {},
                            'outputs': [],
                            'source': current_text.strip().split('\n')
                        })
            
            # 重置内容和状态
            current_text = part
            in_markdown = True
        else:
            # 如果之前的部分是注释块，且当前部分是代码
            if in_markdown and current_text:
                # 添加注释块为markdown
                notebook['cells'].append({
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': convert_to_markdown(current_text)
                })
                current_text = ""
                in_markdown = False
            
            # 处理代码部分
            lines = part.strip().split('\n')
            code_blocks = []
            current_block = []
            
            for line in lines:
                if line.strip() == "":
                    if current_block:  # 如果当前代码块不为空
                        code_blocks.append(current_block)
                        current_block = []
                else:
                    current_block.append(line)
            
            if current_block:  # 添加最后一个代码块
                code_blocks.append(current_block)
            
            # 为每个代码块创建一个单元格
            for block in code_blocks:
                # 跳过空的代码块
                if not all(line.strip() == "" for line in block):
                    notebook['cells'].append({
                        'cell_type': 'code',
                        'execution_count': None,
                        'metadata': {},
                        'outputs': [],
                        'source': block
                    })
    
    # 处理最后一部分
    if current_text.strip():
        if in_markdown:
            notebook['cells'].append({
                'cell_type': 'markdown',
                'metadata': {},
                'source': convert_to_markdown(current_text)
            })
    
    # 写入更新后的notebook
    with open(ipynb_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
    
    print(f"处理完成: {ipynb_file}")

# 将注释块转换为markdown
def convert_to_markdown(text):
    # 移除注释字符和开头结尾的#####
    lines = text.strip().split('\n')
    markdown_lines = []
    
    for line in lines:
        # 跳过只包含###的行
        if re.match(r'^#{3,}$', line.strip()):
            continue
        
        # 移除开头的#号和空格
        clean_line = re.sub(r'^#{3,}\s*', '', line)
        clean_line = re.sub(r'^#\s*', '', clean_line)
        
        # 提取标题并添加Markdown格式
        title_match = re.match(r'^(.*?):\s*(.*?)$', clean_line)
        if title_match and len(title_match.groups()) == 2:
            section, content = title_match.groups()
            if section.strip() and not section.strip().isdigit():
                markdown_lines.append(f"## {section.strip()}")
                if content.strip():
                    markdown_lines.append("")
                    markdown_lines.append(content.strip())
                continue
        
        markdown_lines.append(clean_line)
    
    # 处理Markdown格式，并将连续的空行合并为一个空行
    processed_lines = []
    prev_empty = False
    
    for line in markdown_lines:
        if line.strip() == "":
            if not prev_empty:
                processed_lines.append(line)
                prev_empty = True
        else:
            processed_lines.append(line)
            prev_empty = False
    
    return processed_lines

# 处理三个作业文件
convert_py_to_notebook('src/homework/H1-数据读取与基本操作.py', 'src/homework/H1-数据读取与基本操作.ipynb')
convert_py_to_notebook('src/homework/H2-数据清洗与格式转换.py', 'src/homework/H2-数据清洗与格式转换.ipynb')
convert_py_to_notebook('src/homework/H3-数据聚合与可视化分析.py', 'src/homework/H3-数据聚合与可视化分析.ipynb')

print("所有文件处理完成!") 